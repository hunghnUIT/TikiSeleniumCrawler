from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from config.redis import redis_client as redis
from config.db import col_tracked_item

# Settings
from settings import (
    CLASS_NAME_NAME_ITEM, CLASS_NAME_RATING,
    CLASS_NAME_PRICE, CLASS_NAME_REVIEW_NUMBER,
    CLASS_NAME_ITEM_NAME, CLASS_NAME_ITEM_RATING,
    CLASS_NAME_ITEM_PRICE, CLASS_NAME_ITEM_IMAGE,
    CLASS_NAME_ITEM_TOTAL_REVIEW, CLASS_NAME_ITEM_CATEGORY_ID,
    CLASS_NAME_THUMBNAIL, CLASS_NAME_SCROLL_TO_REVIEW_BUTTON,
    CLASS_NAME_ITEM_SELLER,
    REDIS_TRACKED_ITEMS_HASH_NAME, REDIS_REPRESENTATIVE_TRUE_VALUE, WAIT_TIME_LOAD_PAGE,
)

# Functions
from helper import (
    get_item_id, calculate_rating,
    convert_string_to_int, get_current_time_in_ms, proccess_category_url,
    process_item_price, extract_background_image_url,
    map_extract_image_url, get_total_review,
)

import timing_value


def extract_data_from_category_dom_object(dom_object: object, category_id: int) -> object:
    item = {} 
    try:
        product_url = dom_object.get_attribute('href')
        rating = dom_object.find_elements_by_class_name(CLASS_NAME_RATING)
        review = dom_object.find_elements_by_class_name(
            CLASS_NAME_REVIEW_NUMBER)

        item['id'] = get_item_id(product_url)
        item['name'] = dom_object.find_element_by_css_selector(
            CLASS_NAME_NAME_ITEM).text
        # item['sellerId'] = info_from_url['sellerId'] # This is not exists in both DOM and API
        item['categoryId'] = category_id
        item['productUrl'] = product_url
        item['rating'] = calculate_rating(
            rating[0].get_attribute('style')) if rating else 0
        item['totalReview'] = get_total_review(review[0].text) if review else 0
        item['update'] = get_current_time_in_ms()
        item['expired'] = timing_value.expiredTime
        item['price'] = convert_string_to_int(
            dom_object.find_element_by_class_name(CLASS_NAME_PRICE).text)
        item['thumbnailUrl'] = dom_object.find_element_by_css_selector(
            CLASS_NAME_THUMBNAIL).get_attribute('src')
        if not item['thumbnailUrl']:
            return {
                'success': False,
                'data': item,
            }
        else:
            return {
                'success': True,
                'data': item,
            }

    except NoSuchElementException:
        return {
            'success': False,
            'data': None,
        }

# These fields below is usually failed for category url.
def extract_field_from_category_dom_object(key: str, dom_object: object) -> any:
    switcher = {
        'thumbnailUrl': dom_object.find_element_by_css_selector(CLASS_NAME_THUMBNAIL).get_attribute('src')
    }
    return switcher.get(key, None)


# These fields below is usually failed for item url.
def extract_field_from_item_dom_object(key: str, dom_object: object, is_trying_again: bool = False) -> any:
    try:
        if is_trying_again:
            WebDriverWait(dom_object, WAIT_TIME_LOAD_PAGE).until(
            EC.presence_of_element_located((By.CLASS_NAME, CLASS_NAME_ITEM_RATING)))
                
        switcher = {
            'rating': dom_object.find_element_by_class_name(CLASS_NAME_ITEM_RATING).text,
            'totalReview': ((dom_object.find_element_by_class_name(CLASS_NAME_ITEM_TOTAL_REVIEW).text).split(' '))[0],
        }
        value = switcher.get(key, None)
    except NoSuchElementException:
        value = None
    except TimeoutException:
        print("Loading rating took too much time!")
        value = None

    return value

def extract_data_from_item_dom_object(dom_object: object, product_url: str):
    item = {} 
    try:
        # Scroll to the end no matter having review or not
        # ActionChains(dom_object).send_keys(Keys.END).perform()

        item_id = get_item_id(product_url)
        seller_id = dom_object.find_element_by_css_selector(CLASS_NAME_ITEM_SELLER).get_attribute('data-view-label')
        item_price = dom_object.find_element_by_class_name(
            CLASS_NAME_ITEM_PRICE).text
        images = dom_object.find_elements_by_css_selector(
            CLASS_NAME_ITEM_IMAGE)
        category_ids = dom_object.find_elements_by_class_name(
            CLASS_NAME_ITEM_CATEGORY_ID)
        href = category_ids[-2].get_attribute('href') if category_ids else ''
        category_id = proccess_category_url(href) if href else 0
        scroll_to_review_button = dom_object.find_elements_by_css_selector(CLASS_NAME_SCROLL_TO_REVIEW_BUTTON)
        rating = 0.0
        total_review = 0
        if scroll_to_review_button:
            scroll_to_review_button[0].click()
            try:
                rating = dom_object.find_element_by_class_name(CLASS_NAME_ITEM_RATING).text
                total_review = ((dom_object.find_element_by_class_name(CLASS_NAME_ITEM_TOTAL_REVIEW).text).split(' '))[0]
            except NoSuchElementException as err:
                rating = None
                total_review = None

        item['id'] = item_id
        item['name'] = dom_object.find_element_by_css_selector(
            CLASS_NAME_ITEM_NAME).text
        item['sellerId'] = int(seller_id)
        item['categoryId'] = int(category_id)
        item['productUrl'] = product_url
        item['rating'] = float(rating) if rating is not None else None
        item['totalReview'] = int(total_review) if total_review is not None else None
        item['update'] = get_current_time_in_ms()
        item['expired'] = timing_value.expiredTime
        item['price'] = process_item_price(item_price)
        item['thumbnailUrl'] = images[0].get_attribute('src')
        item['images'] = map_extract_image_url(images)

        if not item['thumbnailUrl'] or item['rating'] is None or item['totalReview'] is None:
            return {
                'success': False,
                'data': item,
            }

        return {
            'success': True,
            'data': item,
        }
    except NoSuchElementException as err:
        print(str(err))
        return {
            'success': False,
            'data': None,
        }
    except Exception as err:
        print(str(err))


def store_tracked_items_to_redis():
    # Delete the old one before update new.
    redis.delete(REDIS_TRACKED_ITEMS_HASH_NAME)

    limit = 2000
    skip = 0
    tracked_items = []
    while True:
        items = list(col_tracked_item.find().limit(limit).skip(skip))
        if items:
            tracked_items += items
            skip += limit
        else:
            break

    for el in tracked_items:
        redis.hset(REDIS_TRACKED_ITEMS_HASH_NAME, int(el['itemId']), REDIS_REPRESENTATIVE_TRUE_VALUE)