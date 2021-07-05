import math
from re import split
import time
from typing import List

conventions = {
    "k": 1000,
    "m": 1000000,
}


def get_item_id(url: str) -> int:
    # E.g: https://tiki.vn/dien-thoai-iphone-12-pro-max-128gb-hang-chinh-hang-p70771651.html?src=ss-organic
    url = url[0:url.find('.html')] # Remove tail after ".html"
    splitted_url_by_dash = url.split('-')

    return int((splitted_url_by_dash[-1]).replace('p', ''))


'''
**@return** int number which is current category id 
'''
def proccess_category_url(url: str) -> int:
    if url.find('?') > -1 and 'search' not in url:
        url = url[0:url.find('?')]
    splitted_by_slash = url.split('/')
    category_id = splitted_by_slash[-1].replace('c', '')
    return int(category_id)


def convert_string_to_int(string: str) -> int:
    string = string.replace('₫', '')
    string = string.replace('+', '')
    number = 0
    if not string.isdigit():
        unit = ''
        if string[-1].isalpha():
            unit = string[-1]
            string = string.replace(unit, '')
        string = string.replace('.', '')
        string = string.replace(",", '.')
        if unit:
            number = float(string) * conventions[unit]
        else:
            number = string
    else:
        number = string
    if isinstance(number, str):
        number = number.strip()
    return int(number)


def calculate_rating(percent: str) -> float:
    rating = 0.0

    # width: 94%; or width: 94%
    p = percent.replace('width:', '')
    if '%;' in percent:
        p = p.replace('%;', '')
    else:
        p = p.replace('%', '')
    rating += round((float(p.strip()) * 5)/100, 1)

    return rating

def get_total_review(review: str) -> int:
    # (Xem 11 đánh giá)
    review = review.replace('(Xem ', '')
    review = review.replace(' đánh giá)', '')
    return int(review)

def get_current_time_in_ms() -> int:
    return round(time.time() * 1000)


def process_item_price(price: str) -> int:
    price = price.split('-')
    return convert_string_to_int(price[0])


def extract_background_image_url(dom_object: object) -> str:
    # background-image: url("https://cf.tiki.vn/file/ee5e00f2460509388cd01a23fa8115bf"); background-size: contain; background-repeat: no-repeat;
    string = dom_object.get_attribute('style')
    start = string.find('url("') + 5 # 5 characters in url("
    end = string.find('")')
    return string[start: end]

def map_extract_image_url(arr:List[object]) -> List[str]:
    res = []
    for el in arr:
        res.append(el.get_attribute('src'))
    return res

def to_human_readable_time_format(timestamp: int):
    hour = math.floor(timestamp / 3600) % 24
    min = math.floor(timestamp / 60) % 60
    sec = math.floor(timestamp) % 60
    result = ''

    if hour:
        result += f'{hour} {"hours" if hour > 1 else "hour"}'

    if min:
        if result:
            result += ' '
        result += f'{min} {"minutes" if min > 1 else "minute"}'

    if sec:
        if result:
            result += ' '
        result += f'{sec} {"seconds" if sec > 1 else "second"}'
    return result