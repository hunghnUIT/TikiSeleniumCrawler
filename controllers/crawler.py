from queue import Queue
from time import sleep
from typing import List
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import threading

# Settings
from settings import (
    WAIT_TIME_LOAD_PAGE,
    CLASS_NAME_CARD_ITEM, MAXIMUM_PAGE_NUMBER,
    LOAD_ITEM_SLEEP_TIME, CLASS_NAME_ITEM_PRICE,
    CLASS_NAME_PAGINATION_BUTTONS, CLASS_NAME_BUTTON_NEXT_PAGE,
    CLASS_NAME_ITEM_SELLER, CLASS_NAME_ITEM_OUT_OF_STOCK,
    HEADLESS, FIREFOX_PROFILE, ALLOWED_CATEGORIES_TO_CRAWL, 
    WILL_CRAWL_ALL_CATEGORIES, MAX_THREAD_NUMBER_FOR_CATEGORY,
)

# Functions
from helper import (
    proccess_category_url,
)
from controllers.item import (
    extract_data_from_category_dom_object, extract_field_from_category_dom_object,
    extract_data_from_item_dom_object, store_tracked_items_to_redis,
    extract_field_from_item_dom_object,
)
import timing_value
from services.item import save_item_to_db
from config.db import col_category


'''
Function receive a category URL at a moment, start at page #1, then crawl to the last page and exit browser.
@method     POST
@body       JSON {urls: List[str]}
@body       None
'''
def crawl_with_category_url(url: str, jobs_queue: Queue, driver: webdriver = None, is_in_recursive: bool = False):
    timing_value.init_timing_value()

    # Not in recursive => This function was called the first time to do crawling job.
    if not is_in_recursive:
        store_tracked_items_to_redis()

    if not driver:
        options = Options()
        if HEADLESS:
            options.headless = True
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')

        driver = webdriver.Firefox(options=options, firefox_profile=FIREFOX_PROFILE)

    category_id = proccess_category_url(url)

    page = 1
    count = 0 # temp

    print(f'Start to crawl category ID: {category_id}')
    while True:
        driver.get(url)

        # Format: [{idx: 1, item_info: {item}}, {idx: 6, item_info: {item}}]
        list_items_failed = []

        try:
            myElem = WebDriverWait(driver, WAIT_TIME_LOAD_PAGE).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, CLASS_NAME_CARD_ITEM)))

            # Scroll to deal with lazy load.
            actions = ActionChains(driver)
            for _ in range(8):  # space 8 times = heigh of the document
                actions.send_keys(Keys.SPACE).perform()
                sleep(LOAD_ITEM_SLEEP_TIME)

            # query all items
            items = driver.find_elements_by_css_selector(CLASS_NAME_CARD_ITEM)

            # if len(items) == last_page_item_number and last_page_item_number < 50:
            #     print(f'Done crawling category {category_id}, last page: {page - 1}')
            #     break

            if (items):
                for idx, el in enumerate(items):
                    result = extract_data_from_category_dom_object(el, category_id)
                    if not result['success']:
                        list_items_failed.append({
                            'idx': idx,
                            'item_info': result['data'],
                        })
                    else:
                        count += 1
                        # print(result['data'])
                        save_item_to_db(result['data'])

            # Format "list_items_failed": [{idx: 1, item_info: {item}}, {idx: 6, item_info: {item}}]
            if list_items_failed:
                # try again twice
                for _ in range(2):
                    for i, item in enumerate(list_items_failed):
                        dom_object = items[item['idx']]
                        item_info = item['item_info']
                        if item_info: # A few fields failed
                            if item_info['thumbnailUrl'] == None:
                                result = extract_field_from_category_dom_object('thumbnailUrl', dom_object)
                                if result:
                                    item_info['thumbnailUrl'] = result
                                    # print(item_info)
                                    save_item_to_db(item_info)
                                    count += 1
                                    del list_items_failed[i]
                        else: # entire item failed
                            result = extract_data_from_category_dom_object(dom_object, category_id)
                            if result['success']:
                                # print(result['data'])
                                save_item_to_db(result['data'])
                                count += 1
                                del list_items_failed[i]

                # Ignored items still failed after trying again twice.
                list_items_failed = []

        except TimeoutException:
            print("Loading took too much time!")
            items = []

        # page start from 1
        print(f'Done crawling page #{page} of category {category_id}. Total item: {count}')

        if page <= MAXIMUM_PAGE_NUMBER:
            pagination_buttons = driver.find_elements_by_css_selector(CLASS_NAME_PAGINATION_BUTTONS)
            if not pagination_buttons or (pagination_buttons and not pagination_buttons[-1].find_elements_by_css_selector(CLASS_NAME_BUTTON_NEXT_PAGE)):
                print(f'Done crawling category {category_id}, last page: {page}')
                break
            else:
                next_page_url = pagination_buttons[-1].find_element_by_tag_name('a').get_attribute('href')
                url = next_page_url
                # last_page_item_number = len(items)
        else:
            print(f'Done crawling category {category_id}, last page: {page}')
            break

        page += 1

    if not jobs_queue.empty():
        url_from_queue = jobs_queue.get()

        crawl_with_category_url(
            url=url_from_queue, jobs_queue=jobs_queue, driver=driver, is_in_recursive=True)

    if not is_in_recursive:  # Not in recursive, can safely quit browser after all task queue is done
        driver.quit()


def loop_items(driver, urls):
    for url in urls:
        try:
            driver.get(url)

            myElem = WebDriverWait(driver, WAIT_TIME_LOAD_PAGE).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, CLASS_NAME_ITEM_PRICE)))

            no_seller = False
            try:
                WebDriverWait(driver, WAIT_TIME_LOAD_PAGE).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, CLASS_NAME_ITEM_SELLER)))
            except TimeoutException:
                # out of stock and stop selling using the same class name`
                out_of_stock = driver.find_elements_by_css_selector(CLASS_NAME_ITEM_OUT_OF_STOCK)
                if out_of_stock: 
                    no_seller = True
                else:
                    print('Can not find seller. Skip this item')
                    continue

            result = extract_data_from_item_dom_object(driver, url, no_seller)
            if result and result['success']:
                # print(result['data'])
                save_item_to_db(result['data'])
            elif result and not result['success']:
                item_info = result['data']

                failed_field_count = None # init variable
                # Try again three time
                for i in range(3):
                    if item_info:  # A few fields failed
                        failed_field_count = 0  # assign value variable
                        for key in item_info:
                            if item_info[key] is None:
                                failed_field_count += 1
                                if i < 1:
                                    value = extract_field_from_item_dom_object(key=key, dom_object=driver)
                                else:
                                    value = extract_field_from_item_dom_object(key=key, dom_object=driver, is_trying_again=True)

                                if value:
                                    item_info[key] = value
                                    failed_field_count -= 1

                        # Got all fields -> no need to try one more time
                        if not failed_field_count:
                            # print(f'Done after {i+1} times')
                            save_item_to_db(item_info)
                            break
                        elif i == 2 and failed_field_count:  # Means try again third time, start from 0
                            print('Error because of "rating" or "totalReview" field or both')

                    else:  # entire item failed
                        result = extract_data_from_item_dom_object(driver, url, no_seller)
                        if result['success']:
                            # print(result['data'])
                            save_item_to_db(result['data'])

        except TimeoutException:
            print("Loading took too much time!")
        except Exception as err:
            print(str(err))

'''
Function receive a item URLs, crawl items one by one and quit browser.
@route      {{BASE_URL}}/crawl-item
@method     POST
@body       { urls: list[str] }
'''
def crawl_with_item_urls(urls: List[str], jobs_queue: Queue):
    timing_value.init_timing_value()
    store_tracked_items_to_redis()

    options = Options()
    if HEADLESS:
        options.headless = True

    driver = webdriver.Firefox(options=options, firefox_profile=FIREFOX_PROFILE)
    loop_items(driver, urls)

    while not jobs_queue.empty():
        urls_from_queue = jobs_queue.get()

        loop_items(driver, urls_from_queue)

    driver.quit()

def crawl_all_items(start_index, queue, thread_count_at_start):
    timing_value.init_timing_value()
    store_tracked_items_to_redis()

    cates = list(col_category.find())

    for idx, cate in enumerate(cates):
        if (cate['rootId'] in ALLOWED_CATEGORIES_TO_CRAWL or WILL_CRAWL_ALL_CATEGORIES) and idx >= start_index:
            url = cate["categoryUrl"]

            thread_allowed_left = threading.active_count() - thread_count_at_start - 1  # 1 is thread using for calling this function, I guess

            if thread_allowed_left < MAX_THREAD_NUMBER_FOR_CATEGORY:
                (threading.Thread(target=crawl_with_category_url, args=[url, queue, None])).start()
            else:
                queue.put(url)