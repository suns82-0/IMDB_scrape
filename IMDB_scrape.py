#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 19:07:52 2019

@author: xsun43
"""

import pymysql
#%%
import time 
from bs4 import BeautifulSoup
import requests
import random
import re
from requests.exceptions import RequestException
import csv
import os
import sys
#%%
print(sys.argv[0])
print("__file Output:",__file__)
#%%
def get_agent():
    '''
    模拟header的user-agent字段，
    返回一个随机的user-agent字典类型的键值对
    '''
    agents = ['Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
              'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv,2.0.1) Gecko/20100101 Firefox/4.0.1',
              'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
              'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
              'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)']
    fakeheader = {}
    fakeheader['User-agent'] = agents[random.randint(0, len(agents))]
    return fakeheader
#%%
def get_proxy():
    '''
    简答模拟代理池
    返回一个字典类型的键值对，
    '''
    proxy = ["http://116.211.143.11:80",
             "http://183.1.86.235:8118",
             "http://183.32.88.244:808",
             "http://121.40.42.35:9999",
             "http://222.94.148.210:808"]
    fakepxs = {}
    fakepxs['http'] = proxy[random.randint(0, len(proxy))]
    return fakepxs
#%%
def get_html(url):
    try:
        r = requests.get(url, timeout=30)
        print(r.headers)
        r.raise_for_status
        r.encoding = r.apparent_encoding

        return r.status_code
    except:
        return "Someting Wrong！"
#%%
def get_top250_movies_list():
    url = "http://www.imdb.com/chart/top"
    id_pattern = re.compile(r'(?<=tt)\d+(?=/?)')
#    headers = {'User-Agent':get_agent()}
    try:
        response = requests.get(url,timeout = 10)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            movies = soup.find("tbody",{"class":"lister-list"})
            for movie in movies.findAll("tr"):
                poster = movie.find("td",{"class":"posterColumn"})
                score = poster.find("span",{"name":"ir"})["data-value"]
                movie_link = movie.find("td",{"class":"titleColumn"}).find('a')["href"]
                year_str = movie.find("td",{"class":"titleColumn"}).text
                year_pattern = re.compile('\d{4}')
                year = int(year_pattern.search(year_str).group())
                id_pattern = re.compile(r'(?<=tt)\d+(?=/?)')
                movie_id = int(id_pattern.search(movie_link).group())
                movie_name = movie.select_one('.titleColumn').select_one('a').string

                yield {
                    'movie_id': movie_id,
                    'movie_name': movie_name,
                    'year': year,
                    'movie_link': movie_link,
                    'movie_rate': float(score)
                }
        else:
            print("Error when request URL")
    except RequestException:
        print("Request Failed")
        return None
#%%
for item in get_top250_movies_list():
    print(item["movie_name"])
#%%
csvFile = open("files/test.csv", 'w+')
try:
    writer = csv.writer(csvFile)
    for movie in get_top250_movies_list():
        writer.writerow((movie["movie_id"],movie["movie_name"],movie["year"],movie["movie_link"],movie["movie_rate"]))

finally:
    csvFile.close()
#%%
def get_movie_detail_data(movie_data):
    url = "http://www.imdb.com" + movie_data['movie_link']
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            # Parse Director's info
            director = soup.find("div",{"class":"credit_summary_item"})
            person_link = director.find('a')['href']
            director_name = director.find('a').text
            id_pattern = re.compile(r'(?<=nm)\d+(?=/?)')
            person_id = int(id_pattern.search(person_link).group())
            movie_data['director_id'] = person_id
            movie_data['director_name'] = director_name
            store_director_data_in_csv(movie_data)
#            store_director_data_in_db(movie_data)
            #parse Cast's data
            cast = soup.find("table",{"class":"cast_list"}).findAll("tr",{"class":["even","odd"]})
            for actor in get_cast_data(cast):
                store_actor_data_to_csv(actor, movie_data)
        else:
            print("GET url of movie Do Not 200 OK!")
    except RequestException:
        print("Get Movie URL failed!")
        return None

#%%
def store_director_data_in_csv(movie):
    csvFile = open("files/director.csv", 'a')
    try:
        writer = csv.writer(csvFile)
#        for movie in get_top250_movies_list():
        writer.writerow((movie["director_id"],movie["director_name"]))

    finally:
        csvFile.close()
#%%
def get_cast_data(cast):
    for actor in cast:
        actor_data = actor.find("td",{"class":"primary_photo"}).findNext("td")
        person_link = actor_data.a['href']
        id_pattern = re.compile(r'(?<=nm)\d+(?=/)')
        person_id = int(id_pattern.search(person_link).group())
        actor_name = actor_data.text.strip()
        yield {
            'actor_id': person_id,
            'actor_name': actor_name
        }

#%%
def store_actor_data_to_csv(actor):
    csvFile = open("..\\files\\actors.csv", 'w+')
    try:
        writer = csv.writer(csvFile)
#        for movie in get_top250_movies_list():
        writer.writerow((actor["actor_id"],actor["actor_name"]))

    finally:
        csvFile.close()

#%%
url = "https://www.imdb.com/title/tt0111161/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=e31d89dd-322d-4646-8962-327b42fe94b1&pf_rd_r=RPNKQ36PJV1M91QFD63Q&pf_rd_s=center-1&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_tt_1"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
cast = soup.find("table",{"class":"cast_list"}).findAll("tr",{"class":["even","odd"]})

for actor in get_cast_data(cast):
    store_actor_data_to_csv(actor)
#%%
#for movie in get_top250_movies_list():
#    get_movie_detail_data(movie)
#%%
def main():
    start = time.time()
    try:
        for movie in get_top250_movies_list():
#            store_movie_data_to_db(movie)
            get_movie_detail_data(movie)
    finally:
        csvFile.close()
    end = time.time()
    lastTime = int(end-start)
    print("Cost time: {} seconds".format(lastTime))


if __name__ == '__main__':
    main()