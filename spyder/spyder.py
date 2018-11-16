import csv
import http.client
import random
import socket
import time

import pymysql
import requests
from bs4 import BeautifulSoup


def getContent(url,data=None):
    header={
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip,deflate,sdch',
            'Accept-language':'zh-CN,zh;q=0.8',
            'Connection':'keep-alive',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.235'
            }
    timeout = random.choice(range(80,180))
    while True:
        try:
            rep = requests.get(url,headers=header,timeout=timeout)
            rep.encoding = 'utf-8'
            break
        except socket.timeout as e:
            print('time out:',e)
            time.sleep(random.choice(range(5,10)))

        except socket.error as e:
            print('error:',e)
            time.sleep(random.choice(range(5,10)))

        except http.client.BadStatusLine as e:
            print('bad status line:',e)
            time.sleep(random.choice(range(5,10)))

        except http.client.IncompleteRead as e:
            print("incomplete read:",e)
            time.sleep(random.choice(range(5,10)))
    print('request success')
    return rep.text

def getData(html_context):
    final = []
    bs = BeautifulSoup(html_context,"html.parser")
    body = bs.body
    data =body.find('div',{'id':'7d'})
    ul = data.find('ul')
    li = ul.find_all('li')

    for day in li:
        temp = []
        date = day.find('h1').string
        temp.append(date)
        inf = day.find_all('p')
        weather = inf[0].string
        temp.append(weather)
        temperature_highest = inf[1].find('span').string
        temperature_lower = inf[1].find('i').string
        temp.append(temperature_lower)
        temp.append(temperature_highest)
        final.append(temp)
    print('get data success')
    return final

def writeData(data,name):
    with open(name,'a',errors='ignore',newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(data)
    print('write_csv success')

def createTable():
    db = pymysql.connect('localhost','root','mobstazinc','weather')
    cursor = db.cursor()
    cursor.execute('select version()')
    data = cursor.fetchone()
    print("database version:%s" %data)

    cursor.execute("drop table if exists weather")

    sql = """CREATE TABLE WEATHER (
             w_id int(8) not null primary key auto_increment, 
             w_date  varchar(20) NOT NULL ,
             w_detail  varchar(30),
             w_temperature_low varchar(10),
             w_temperature_high varchar(10)) DEFAULT CHARSET=utf8"""
    cursor.execute(sql)

    db.close()
    print('create table success')

def insertData(datas):
    db = pymysql.connect("localhost",'root','mobstazinc','weather')
    cursor = db.cursor()

    try:
        cursor.executemany('insert into weather(w_id,w_date,w_detail,w_temperature_low, w_temperature_high) value(null,%s,%s,%s,%s)',datas)
        db.commit()
    except Exception as e:
        print('insert error'+e)

    db.close()
    print('insert data success')

if __name__=='__main__':
    url = 'http://www.weather.com.cn/weather/101210101.shtml'
    html = getContent(url)
    result = getData(html)
    writeData(result,'D:/pythonsrc/file/weather.csv')
    #createTable()
    insertData(result)
    print('success')




























        