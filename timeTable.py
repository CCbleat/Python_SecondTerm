import requests
import re
import prettytable


def get_print_timetable(data):
    url = 'http://59.77.226.32/logincheck.asp'
    # use session to keep session between serve and client
    session = requests.Session()
    session.headers.update({
        'Referer': 'http://jwch.fzu.edu.cn/login.aspx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66'
    })
    # post method
    res = session.post(url=url, data=data, timeout=5)
    # keep login status and jump to the timeTable page
    # using regexp to get the url of the timeTable page
    pattern_url = re.compile("top\\.aspx\\?id=(.*?)..noresize", re.S)
    url_id = re.findall(pattern_url, res.text)[0]
    time_table_url = 'http://59.77.226.35/right.aspx?id=' + url_id
    # get method
    time_table = session.get(url=time_table_url, timeout=5)
    # use regexp to extract messages
    pattern_time_table = re.compile("#9A1B1B.>(.*?)</font>", re.S)
    course = re.findall(pattern_time_table, time_table.text)
    # Create table and print it
    time_table = prettytable.PrettyTable()
    time_table.field_names = ["星期一", "星期二", "星期三", "星期四", "星期五"]
    time_table.add_row(course[0:5])
    time_table.add_row(course[5:10])
    time_table.add_row(course[10:15])
    time_table.add_row(course[15:20])
    time_table.add_row(course[20:25])
    time_table.add_row(course[25:30])
    time_table.add_row(course[30:35])
    time_table.add_row(course[35:40])
    time_table.align = 'l'
    time_table.padding_width = 5
    print(time_table)


def main():
    s_id = input("账号")
    s_password = input("密码")
    data = {
        'muser': s_id,
        'passwd': s_password
    }
    get_print_timetable(data)


main()
