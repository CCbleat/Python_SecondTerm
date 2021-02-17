import requests
import time
from urllib.parse import urljoin
# from bs4 import BeautifulSoup
# it is strange when I use BeautifulSoup, so I use XPath to instead
from lxml import etree
import re
import pymysql

# every page has several child url
def get_page_parent(offset):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66',
        'Host': 'news.fzu.edu.cn',
        'Referer': 'http://news.fzu.edu.cn/html/fdyw/16.html'
    }
    parent_url = 'http://news.fzu.edu.cn/html/fdyw/' + str(offset) + '.html'
    parent_response = requests.get(url=parent_url, headers=headers)
    if parent_response.status_code == 200:
        return parent_response.text
    else:
        return parent_response.status_code

#get child url from parent html
def guide_parent_to_child(html_one):
    # soup = BeautifulSoup(html1.text,'lxml')
    html_one = etree.HTML(html_one)
    set_child_html = html_one.xpath('//*[@id="main"]/div[2]/div[2]/ul/li/a/@href')
    for item in set_child_html:
        child_url = urljoin('http://news.fzu.edu.cn/html/fdyw/1.html', item)  # merge links
        get_page_child(child_url)  # to grab date_time, author, headline, read_count and main_text

# get html from child url
def get_page_child(child_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66',
        'Host': 'news.fzu.edu.cn',
        'Referer': 'http://news.fzu.edu.cn/html/fdyw/16.html'
    }
    child_response = requests.get(url=child_url, headers=headers)
    parse_message(child_response)


# get 发布⽇期，作者，标题，阅读数以及正⽂
def parse_message(html2):
    # title
    pattern_title = re.compile('<title>(.*?)-福州大学新闻网</title>')
    title_news = re.findall(pattern_title, html2)
    print(" 标题: ", title_news, end='')

    # date
    pattern_date = re.compile('<span.id..fbsj.>(.*?)</span>', re.S)
    date_news = re.findall(pattern_date, html2)
    print("日期: ", date_news, end='')

    # author
    pattern_author = re.compile('<span id="author">(.*?)</span>', re.S)
    author_news = re.findall(pattern_author, html2)
    print(" 作者: ", author_news, end='')

    # read_count
    pattern_read_count_url = re.compile('interFace/getDocReadCount.do.id.(.*?)..timeout', re.S)
    read_count_url_id = re.findall(pattern_read_count_url, html2)
    read_count_url = 'http://news.fzu.edu.cn//interFace/getDocReadCount.do?id=' + read_count_url_id[0]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66',
        'Host': 'news.fzu.edu.cn',
        'Referer': 'http://news.fzu.edu.cn/html/fdyw/16.html'
    }
    read_count_page = requests.get(url=read_count_url, headers=headers)
    pattern_read_count = re.compile('.*', re.S)
    read_count = re.findall(pattern_read_count, read_count_page.text)[0]
    print(" 阅读量: ", read_count)

    # detail_content
    html2 = etree.HTML(html2)
    detail_content = html2.xpath('//*[@id="news_content_display"]/p//text()')
    detail_content = "".join(detail_content)
    print("正文:\n", detail_content)

    sql = 'insert into fdyw_2020(title_news, date_news, author_news, read_count, detail_content) values(%s, %s, %s, %s, %s)'
    cursor.execute(sql, (title_news, date_news, author_news, read_count, detail_content))
    db.commit()


if __name__ == '__main__':
    # create database
    db = pymysql.connect(host='localhost', user='root', password='haomima66A', port=3306, db='fdyw_2020')
    cursor = db.cursor()
    # verify if there exist the table
    cursor.execute("drop table if EXISTS fdyw_2020")

    # create database table
    sql_createTb = """CREATE TABLE fzu_new (
                         id INT NOT NULL AUTO_INCREMENT,
                         title_news CHAR(60),
                         date_news CHAR(20),
                         author_news CHAR(40),
                         read_count int,
                         detail_content TEXT,
                         PRIMARY KEY(id))
                         """
    cursor.execute(sql_createTb)
# use for loop to grab 4 pages of fdyw
    for i in range(4):
        html1 = get_page_parent(i + 3)
        guide_parent_to_child(html1)
        time.sleep(10)
