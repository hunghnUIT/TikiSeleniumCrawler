CRAWLER_ID = '00'
CRAWLER_NAME = f'tiki_html_crawler_{CRAWLER_ID}'

from services.config import get_config
#region Firefox Profile
from selenium import webdriver
firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference("network.http.pipelining", True)
firefox_profile.set_preference("network.http.proxy.pipelining", True)
firefox_profile.set_preference("network.http.pipelining.maxrequests", 8)
firefox_profile.set_preference("content.notify.interval", 500000)
firefox_profile.set_preference("content.notify.ontimer", True)
firefox_profile.set_preference("content.switch.threshold", 250000)
firefox_profile.set_preference("browser.cache.memory.capacity", 65536) # Increase the cache capacity.
firefox_profile.set_preference("browser.startup.homepage", "about:blank")
firefox_profile.set_preference("reader.parse-on-load.enabled", False) # Disable reader, we won't need that.
firefox_profile.set_preference("browser.pocket.enabled", False) # Duck pocket too!
firefox_profile.set_preference("loop.enabled", False)
firefox_profile.set_preference("browser.chrome.toolbar_style", 1) # Text on Toolbar instead of icons
firefox_profile.set_preference("browser.display.show_image_placeholders", False) # Don't show thumbnails on not loaded images.
firefox_profile.set_preference("browser.display.use_document_colors", False) # Don't show document colors.
firefox_profile.set_preference("browser.display.use_document_fonts", 0) # Don't load document fonts.
firefox_profile.set_preference("browser.display.use_system_colors", True) # Use system colors.
firefox_profile.set_preference("browser.formfill.enable", False) # Autofill on forms disabled.
firefox_profile.set_preference("browser.helperApps.deleteTempFileOnExit", True) # Delete temprorary files.
firefox_profile.set_preference("browser.shell.checkDefaultBrowser", False)
firefox_profile.set_preference("browser.startup.homepage", "about:blank")
firefox_profile.set_preference("browser.startup.page", 0) # blank
firefox_profile.set_preference("browser.tabs.forceHide", True) # Disable tabs, We won't need that.
firefox_profile.set_preference("browser.urlbar.autoFill", False) # Disable autofill on URL bar.
firefox_profile.set_preference("browser.urlbar.autocomplete.enabled", False) # Disable autocomplete on URL bar.
firefox_profile.set_preference("browser.urlbar.showPopup", False) # Disable list of URLs when typing on URL bar.
firefox_profile.set_preference("browser.urlbar.showSearch", False) # Disable search bar.
firefox_profile.set_preference("extensions.checkCompatibility", False) # Addon update disabled
firefox_profile.set_preference("extensions.checkUpdateSecurity", False)
firefox_profile.set_preference("extensions.update.autoUpdateEnabled", False)
firefox_profile.set_preference("extensions.update.enabled", False)
firefox_profile.set_preference("general.startup.browser", False)
firefox_profile.set_preference("plugin.default_plugin_disabled", False)
# firefox_profile.set_preference("permissions.default.image", 2) # Image load disabled again <== this cause img src of item not shown
#endregion

# Global variable
TIKI = 'tiki'
REDIS_TRACKED_ITEMS_HASH_NAME = 'trackedItems-tiki'
RECEIVE_NOTIFICATION_SERVICE_ADDRESS = 'http://10.255.255.8:5050/notify-for-item' # param: itemId=...., newPrice=..., platform=...
A_DAY_IN_MS = 86400000 # = 24hrs
REDIS_REPRESENTATIVE_TRUE_VALUE = 1
HEADLESS = eval((get_config('headless', 'true')).title())
FIREFOX_PROFILE = firefox_profile
MAX_THREAD_NUMBER_FOR_ITEM = int(get_config('max_thread_number_for_item', '2'))
MAX_THREAD_NUMBER_FOR_CATEGORY = int(get_config('max_thread_number_for_category', '5'))

# After receiving crawling message
ALLOWED_CATEGORIES_TO_CRAWL = {
    1789: 'Điện thoại máy tính bảng',
    1815: 'Phụ kiện thiết bị số',
    1846: 'Laptop - Thiết bị IT',
}
WILL_CRAWL_ALL_CATEGORIES = False

# Settings for crawler
TIME_BETWEEN_CRAWLING_IN_HOUR = int(get_config('time_between_crawling_in_hour', '8'))

WAIT_TIME_LOAD_PAGE = int(get_config('wait_time_load_page', '3')) # seconds
NUMBER_PARTS_PAGE_HEIGHT = 7 # Assuming an page have this number of part corresponding to its height 

# configs about crawling items by category
CLASS_NAME_CARD_ITEM = get_config('class_name_card_item', '.product-item') # card component contains all item's info
CLASS_NAME_NAME_ITEM = get_config('class_name_name_item', '.name span')
CLASS_NAME_PRICE = get_config('class_name_price', '.price-discount__price') # string 5.800.000  # discount or not still use this class name
CLASS_NAME_RATING = get_config('class_name_rating', '.average') # old class: '.rating__average' # Get attribute width * 5 <=> rating
CLASS_NAME_REVIEW_NUMBER = get_config('class_name_review_number', '.styles__StyledQtySold-sc-732h27-2.bQsmEJ') # old class '.review' # NOTE Update 28/6/2021 Tiki replaced rating count by total sold so I'm temporary using "sold" for totalReview
CLASS_NAME_PAGINATION_BUTTONS = get_config('class_name_pagination_buttons', '.Pagination__Root-cyke21-0 li')
CLASS_NAME_THUMBNAIL = get_config('class_name_thumbnail', '.thumbnail img')
CLASS_NAME_BUTTON_NEXT_PAGE = get_config('class_name_button_next_page', '.tikicon.icon-arrow-back')
MAXIMUM_PAGE_NUMBER = 208
LOAD_ITEM_SLEEP_TIME = 0.3 # second

# configs about crawling item by item detail
CLASS_NAME_ITEM_PRICE = get_config('class_name_item_price', '.product-price__current-price')
CLASS_NAME_ITEM_NAME = get_config('class_name_item_name', 'h1[class=title]')
CLASS_NAME_ITEM_REVIEW_DIV = get_config('class_name_item_review_div', '.indexstyle__Review-qd1z2k-3.hqeXws')
CLASS_NAME_ITEM_RATING = get_config('class_name_item_rating', 'div > div > div:nth-child(2)') # this inside review_div
CLASS_NAME_ITEM_TOTAL_REVIEW = get_config('class_name_item_total_review', 'a[class=number]')
CLASS_NAME_ITEM_IMAGE = get_config('class_name_item_image', '.style__ProductImagesStyle-sc-1e5ea5s-0 .PictureV2__StyledWrapImage-tfuu67-0 img') 
CLASS_NAME_ITEM_CATEGORY_ID = get_config('class_name_item_category_id', '.breadcrumb-item')
CLASS_NAME_ITEM_SELLER = get_config('class_name_item_seller', 'div[data-view-id="pdp_store_seller.follow"]')   
CLASS_NAME_ITEM_OUT_OF_STOCK = get_config('class_name_item_out_of_stock', '.style__StyledNotiMessage-sc-18zbm1q-0.hFMOJQ')