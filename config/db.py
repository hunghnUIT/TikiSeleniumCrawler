# import motor.motor_asyncio
import pymongo

client = pymongo.MongoClient(
    "mongodb://localhost:27017", serverSelectionTimeoutMS=10000
    )

try:
    info = client.server_info()
    db_tiki = client['TIKI']
    col_item = db_tiki['ItemsTiki']
    col_item_price = db_tiki['ItemPriceTiki']
    col_category = db_tiki['CategoriesTiki']
    db_user = client['USER']
    col_tracked_item = db_user['TrackedItemsTiki']
    db_server = client['SERVER']
    col_config = db_server['Configs']
except Exception:
    print("Unable to connect to the server.")