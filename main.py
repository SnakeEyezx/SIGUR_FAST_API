from fastapi import Request, FastAPI
import pyodbc
from pyodbc import Row

app = FastAPI()

connection = pyodbc.connect('')  # set your db here
cursor = connection.cursor()
ResponseAllowTrue = {"allow": True, "message": "Добро пожаловать!"}
ResponseAllowFalse = {"allow": False, "message": "Доступ запрещен!"}
ap_links = {"тестовая услуга абонемент": 1}


def decision(name, ap_id):
    if name in ap_links.keys() and ap_id == ap_links.get(name):
        return ResponseAllowTrue
    else:
        return ResponseAllowFalse


def name_of_service(x):
    select_query_string = f'select MENU_ITEMS.NAME1 from MENU_ITEMS,subscription_accounting,cards where subscription_accounting.status = 2 and cards.magstripe = ? and cards.card_id = subscription_accounting.card_id and subscription_accounting.SUBSCRIPTION_MI_ID = MENU_ITEMS.MI_ID;'
    cursor.execute(select_query_string, x)
    result: Row = cursor.fetchone()
    if result is None:
        return 0
    else:
        return result[0]


def log2db(x):
    try:
        insert_query_string = f"INSERT INTO SIGUR_LOGS(LOG_ID, EVENT_TIME, ACCESS_POINT, DIRECTION, KEY_HEX) VALUES (?, ?, ?, ?, ?);"
        cursor.execute(insert_query_string, x["logId"], x["time"], x["accessPoint"], x["direction"], x["keyHex"])
    except pyodbc.Error as error:
        connection.rollback()
        print("Failed to insert record into Oracle database {}".format(error))


@app.post("/")
async def get_body(request: Request):
    req = await request.json()
    work = decision(name_of_service(req["keyHex"]), req["accessPoint"])
    return work


@app.post("/event")
async def get_boy(request: Request):
    async def get_boy(request: Request):
    req = await request.json()
    log2db(req["logs"][0])
    resp = {"confirmedLogId": req["logs"][0]["logId"]}
    return resp
