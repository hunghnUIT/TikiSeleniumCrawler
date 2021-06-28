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
CRAWLER_ID = '00'
TIKI = 'tiki'
REDIS_TRACKED_ITEMS_HASH_NAME = 'trackedItems-tiki'
RECEIVE_NOTIFICATION_SERVICE_ADDRESS = 'http://10.255.255.8:5050/notify-for-item' # param: itemId=...., newPrice=..., platform=...
A_DAY_IN_MS = 86400000 # = 24hrs
REDIS_REPRESENTATIVE_TRUE_VALUE = 1
HEADLESS = True
FIREFOX_PROFILE = firefox_profile
MAX_THREAD_NUMBER_FOR_ITEM = 2
MAX_THREAD_NUMBER_FOR_CATEGORY = 5

# After receiving crawling message
ALLOWED_CATEGORIES_TO_CRAWL = {
    1789: 'Điện thoại máy tính bảng',
    1815: 'Phụ kiện thiết bị số',
    1846: 'Laptop - Thiết bị IT',
}
WILL_CRAWL_ALL_CATEGORIES = False

# Settings for crawler
TIME_BETWEEN_CRAWLING_IN_HOUR = 8

WAIT_TIME_LOAD_PAGE = 3 # seconds
NUMBER_PARTS_PAGE_HEIGHT = 7 # Assuming an page have this number of part corresponding to its height 

# configs about crawling items by category
CLASS_NAME_CARD_ITEM = '.product-item' # card component contains all item's info
CLASS_NAME_NAME_ITEM = '.name span' # For CSS selector
CLASS_NAME_PRICE = '.price-discount__price' # string 5.800.000  # discount or not still use this class name
CLASS_NAME_RATING = '.average' # old class: '.rating__average' # Get attribute width * 5 <=> rating
CLASS_NAME_REVIEW_NUMBER = '.styles__StyledQtySold-sc-732h27-2.bQsmEJ' # old class '.review' # NOTE Update 28/6/2021 Tiki replaced rating count by total sold so I'm temporary using "sold" for totalReview
CLASS_NAME_PAGINATION_BUTTONS = '.Pagination__Root-cyke21-0 li' # CSS selector
CLASS_NAME_THUMBNAIL = '.thumbnail img' # CSS selector
CLASS_NAME_BUTTON_NEXT_PAGE = '.tikicon.icon-arrow-back' # CSS selector
MAXIMUM_PAGE_NUMBER = 208
LOAD_ITEM_SLEEP_TIME = 0.3 # second

# configs about crawling item by item detail
CLASS_NAME_ITEM_PRICE = '.product-price__current-price'
CLASS_NAME_ITEM_NAME = 'h1[class=title]' # CSS selector
CLASS_NAME_ITEM_REVIEW_DIV = '.indexstyle__Review-qd1z2k-3.hqeXws'
CLASS_NAME_ITEM_RATING = 'div > div > div:nth-child(2)' # this inside review_div
CLASS_NAME_ITEM_TOTAL_REVIEW = 'a[class=number]'
CLASS_NAME_ITEM_IMAGE = '.style__ProductImagesStyle-sc-1e5ea5s-0 .PictureV2__StyledWrapImage-tfuu67-0 img' # CSS Selector
CLASS_NAME_ITEM_CATEGORY_ID = '.breadcrumb-item'
CLASS_NAME_ITEM_SELLER = 'div[data-view-id="pdp_store_seller.follow"]'
CLASS_NAME_ITEM_OUT_OF_STOCK = '.style__StyledNotiMessage-sc-18zbm1q-0.hFMOJQ'