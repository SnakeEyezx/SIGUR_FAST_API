from fastapi import Request, FastAPI
import pyodbc
from pyodbc import Row

app = FastAPI()

connection = pyodbc.connect('') # set your db here
cursor = connection.cursor()
ResponseAllowTrue = {"allow": True, "message": "Добро пожаловать!"}
ResponseAllowFalse = {"allow": False, "message": "Доступ запрещен!"}
ap_links = {"тестовая услуга абонемент": 1}

def decision(name, ap_id):
    if name in ap_links.keys() and ap_id == ap_links.get(name):
        return ResponseAllowTrue
    else:
        return ResponseAllowFalse

def TNG_service_name(khex):
    select_query_string = f'select MENU_ITEMS.NAME1,MENU_ITEMS.MI_ID,subscription_accounting.status,cards.magstripe,cards.card_id,subscription_accounting.card_id as SUB_CARD_ID from MENU_ITEMS,subscription_accounting,cards where subscription_accounting.status = 2 and cards.magstripe = ? and cards.card_id = subscription_accounting.card_id and subscription_accounting.SUBSCRIPTION_MI_ID = MENU_ITEMS.MI_ID;'
    cursor.execute(select_query_string, khex)
    result: Row = cursor.fetchone()
    if result is None:
        return 0
    else:
        return result[0]

def log2db(x):
    try:
        insert_query_string = f"INSERT INTO SIGUR_LOGS(LOG_ID, EVENT_TIME, ACCESS_POINT, DIRECTION, KEY_HEX) VALUES (?, ?, ?, ?, ?);"
        cursor.execute(insert_query_string, x["logId"], x["time"], x["accessPoint"], x["direction"], x["keyHex"])
        print(x["logId"], x["time"], x["accessPoint"], x["direction"], x["keyHex"])
    except pyodbc.Error as error:
        connection.rollback()
        print("Failed to insert record into Oracle database {}".format(error))

@app.post("/")
async def get_body(request: Request):
    req = await request.json()
    work = decision(TNG_service_name(req["keyHex"]), req["accessPoint"])
    return work

@app.post("/event")
async def get_boy(request: Request):
    req = await request.json()
    ResponseArray = []
    for i in req["logs"]:
        log2db(i)
        d = {"confirmedLogId": i["logId"]}
        ResponseArray.append(d)
    return ResponseArray