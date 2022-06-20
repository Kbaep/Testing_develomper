from time import sleep
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from services import currency_value_in_rub, send_msg
import datetime
import psycopg2
from config import host, user, password, db_name, api_json_google

try:
    # connect to exist database
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT version();"
        )

        print(f"Server version: {cursor.fetchone()}")

    # create a table or connect
    with connection.cursor() as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS testing(
           id INT,
           order_id INT,
           delivery_time VARCHAR ,
           cost_usa INT,
           cost_rub INT,
           delay TEXT NOT NULL DEFAULT 'Нет',
           delivered TEXT NOT NULL DEFAULT 'Нет'
           );
        """)

        connection.commit()
        print("[INFO] Table connect successfully")

except Exception as _ex:
    print("[INFO] Error while working with PostgreSQL", _ex)


def check_table(data):
    with connection.cursor() as cursor:
        for row in data:
            cursor.execute("SELECT * FROM testing WHERE id = %s", (row['№'],))

            db_order = cursor.fetchall()
            if len(db_order) != 0:
                if db_order[0][1] != row['заказ №'] or db_order[0][2] != row['срок поставки'] or db_order[0][3] != row[
                    'стоимость,$']:
                    cursor.execute(
                        "UPDATE testing SET order_id = %s, delivery_time = %s, cost_usa = %s, cost_rub = %s WHERE id = %s",
                        (row['заказ №'], row['срок поставки'], row['стоимость,$'],
                         currency_value_in_rub(row['стоимость,$'], row['срок поставки']), row['№'],))
                    connection.commit()
            elif len(db_order) == 0:
                cursor.execute("INSERT INTO testing VALUES(%s, %s, %s, %s, %s ,%s ,%s );",
                               (row['№'], row['заказ №'], row['срок поставки'], row['стоимость,$'],
                                currency_value_in_rub(row['стоимость,$'], row['срок поставки']), 'Нет', 'Нет'))
                connection.commit()


def checking_extra_lines(data):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM testing")
        all_table = cursor.fetchall()
        if len(all_table) > len(data):
            for row in range(len(data), len(all_table)):
                cursor.execute("DELETE FROM testing WHERE id = %s", (all_table[row][0],))
                connection.commit()


def send_telegram():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM testing WHERE delay = %sAND delivered = %s", ('Нет', 'Нет',))
        all_table = cursor.fetchall()
        for i in all_table:
            if datetime.datetime.strptime(i[2], '%d.%m.%Y') < datetime.datetime.now():
                pass
                send_msg(f'Прошёл срок по поставке {i[0]}заказа № {i[1]}, плановая дата поставки {i[2]}')
                cursor.execute(
                    "UPDATE testing SET delay = %s WHERE id = %s",
                    ('Да', i[0],))
                connection.commit()


if __name__ == '__main__':
    while True:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(api_json_google, scope)
        client = gspread.authorize(creds)
        sheet = client.open("тестовое").sheet1
        data = sheet.get_all_records()
        check_table(data)
        checking_extra_lines(data)
        send_telegram()
        sleep(600)
