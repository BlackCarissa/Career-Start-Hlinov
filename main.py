import requests
from bs4 import BeautifulSoup as bs
from Classes.bd import DataBase
from Classes.models import Order, Rates
import logging
import sqlite3


def add_order(date):
  con = DataBase()
  if con.check_date(date)==False:
    Order(con,(date)) 
    CBRF.download_data(date) 
    CBRF.write_in_bd()
  else: print(f'Ошибка: Курс ЦБ РФ от {date} уже есть в базе')

def print_res(date,codes):
  con = sqlite3.connect('bd.db')
  cursor = con.cursor() 
  try:
      print(f'Курс ЦБ РФ на {date}:')
      for code in codes:
        cursor.execute(f"SELECT order_id,ondate,name,scale,rate FROM CURRENCY_ORDER JOIN CURRENCY_RATES on id=order_id WHERE ondate='{date}' AND numeric_code = '{code}'")
        res = cursor.fetchone()
        if res!=None:
          print(f"""
          Номер распоряжения: {res[0]}
          Дата установки курсов: {res[1]}
          Валюта: {res[2]}
          Номинал: {res[3]}
          Курс: {res[4]} RUB""")
  except sqlite3.Error as e:
      print("Ошибка получения из БД "+str(e))


class CBRF():
    def download_data(date):
      url = "https://cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
      body = f'''<?xml version="1.0" encoding="utf-8"?>
      <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
          <GetCursOnDateXML xmlns="http://web.cbr.ru/">
            <On_date>{date}</On_date>
          </GetCursOnDateXML>
        </soap:Body>
      </soap:Envelope>'''
      body = bs(body, features="xml")
      body = body.prettify()
      response = requests.post(url,data=body, headers={"Content-Type":"text/xml","SOAPAction":"http://web.cbr.ru/GetCursOnDateXML"})
      file = open('cbr.xml','w',encoding='utf-8')
      file.write(response.text) 
      file.close()

    def write_in_bd():
      con = DataBase()
      count = con.count_orders()
      fd = open('cbr.xml', 'r',encoding='utf-8') 
      xml_file = fd.read() 
      soup = bs(xml_file,features='lxml') # TO-DO Всеравно вылезает сообщение ою использованиии LXML...
      for tag in soup.findAll("valutecursondate"):
        name = tag.find('vname').text.rstrip()
        numeric_code = tag.find('vcode').text
        alphabetic_code = tag.find('vchcode').text
        scale = int(tag.find('vnom').text)
        rate = tag.find('vcurs').text
        Rates(con,count,name,numeric_code,alphabetic_code,scale,rate)
      fd.close()


date = str(input('Введите дату в формате yyyy-mm-dd: ')) # 2023-04-20
codes = list(map(int, input('Введите коды валют: ').split(","))) # 392,840,978
add_order(date)
RES=print_res(date,codes) 

