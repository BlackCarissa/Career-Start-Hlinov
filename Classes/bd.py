from genericpath import exists
import sqlite3
import os
import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename = "main.log",
    format = "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
    encoding = "UTF-8"
    )



class DataBase:
    path = os.path.abspath("bd.db")
    def __init__(self, create_base = False):
        if not exists(self.path): # если базы нет -> создать файл
            create_base = True
        self.__db = sqlite3.connect(self.path) # подключаем базу
        self.__db.row_factory = sqlite3.Row
        self.__cur = self.__db.cursor() # подключаем курсор
        if create_base: # создаем базу методом сreate_db, если ее нет
            self.create_db()
    def __del__(self): 
        self.__db.close()

    def create_db(self): # создание базы
        try:
            with sqlite3.connect("bd.db") as con:
                cur = con.cursor()
                cur.execute("""CREATE TABLE IF NOT EXISTS CURRENCY_ORDER  (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        ondate TEXT UNIQUE NOT NULL

                    )""")
                cur.execute("""CREATE TABLE IF NOT EXISTS CURRENCY_RATES (
                        order_id INT,
                        name TEXT NOT NULL,
                        numeric_code TEXT NOT NULL,
                        alphabetic_code TEXT NOT NULL,
                        scale INT NOT NULL,
                        rate TEXT NOT NULL,
                        FOREIGN KEY (order_id) REFERENCES CURRENCY_ORDER(id)
                    )""")
                con.commit()
            logging.info('База данных успешно создана')
        except sqlite3.Error as error:
            logging.error("Ошибка при работе с SQLite", error)
 
    def save(self, object, params):
        try:
            if isinstance(params, str):
                self.__cur.execute(f"INSERT OR IGNORE INTO {object.table} VALUES(null,'{params}')")
                self.__db.commit()
                logging.info('Добавлена новая запись в таблицу CURRENCY_ORDER')
            else: 
                qr = "?," * len(params)
                self.__cur.execute(f"INSERT OR IGNORE INTO {object.table} VALUES({qr[:-1]})", params)
                self.__db.commit()
                logging.info('Добавлена новая запись в таблицу CURRENCY_RATES')
        except sqlite3.Error as e:
            logging.error(f'Ошибка добавления записи в бд: {e}')
            return False
        return self.__cur.lastrowid
    
    def count_orders(self):
        number_of_rows = self.__cur.execute("SELECT * FROM CURRENCY_ORDER")
        self.__db.commit()
        return len(number_of_rows.fetchall())
    
    def check_date(self,date):
        try:
            self.__cur.execute(f"SELECT id FROM CURRENCY_ORDER WHERE ondate ='{date}'")
            res = self.__cur.fetchone()
            if res!=None:
                logging.error(f'Ошибка: Курс ЦБ РФ от {date} уже есть в базе') 
                return True
            else:
                logging.info(f'Загрузка курса ЦБ РФ от {date}')
                return False
        except sqlite3.Error as e:
            logging.error("Ошибка получения из БД "+str(e))

