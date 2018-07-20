import codecs
import os
import threading
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

import param


def get_detail(driver, link, times=0):
    driver.get(link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')  # timeout?
    try:
        table = soup.find(id='edit')
        title = []
        content = []
        for th in table.find_all('th'):
            title.append(th.getText().strip())
        for td in table.find_all('td'):
            content.append(td.getText().strip())
        return title[1:], content
    except Exception as e:
        if times < 3:
            get_detail(driver, link, times + 1)
        else:
            return None, None


def get_file_content(file):
    """
    读取 txt 文件
    :param file: file path
    :return: an array with file content
    """
    content = []
    with codecs.open(os.getcwd() + '\\' + file, 'r', 'utf-8') as t:
        for line in t:
            content.append(line)
    t.close()
    return content


def read_txt(txt):
    driver = webdriver.Chrome()
    content = get_file_content(txt)
    data = pd.DataFrame()
    for line in content:
        try:
            print(line)
            title, content = get_detail(driver, line)
            title.append('url')
            content.append(line)
            data = data.append(pd.DataFrame(columns=title, data=[content]), ignore_index=True, sort=False)
        except Exception:
            data = data.append(pd.DataFrame(data=[None]), ignore_index=True, sort=False)
            continue
    data.to_excel(txt[:-4] + '.xlsx')


class CrawlDetailThread(threading.Thread):
    def __init__(self, txt):
        threading.Thread.__init__(self)
        self.txt = txt

    def run(self):
        print('starting ' + self.name)
        read_txt(self.txt)


def get_file_pd(path):
    """
    读取 xls 文件
    :param path:
    :return: DataFrame
    """
    return pd.read_excel(os.getcwd() + path, sheet_name='Sheet1')


def get_detail_xls():
    start_time = time.time()
    threads = []
    list_arr = [f for f in os.listdir(os.getcwd()) if f[-3:] == 'txt']
    for txt_file in list_arr:
        thread = CrawlDetailThread(txt_file)
        threads.append(thread)
        thread.start()
    [t.join() for t in threads]
    elapsed_time = time.time() - start_time
    print('all thread end in : ' + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))


def fill_blank(name):
    xls = '\\' + name + '.xlsx'
    txt = '\\' + name + '.txt'
    data = get_file_pd(xls)
    txt_data = get_file_content(txt)
    browser = webdriver.Chrome()
    for line in range(data.shape[0]):
        try:
            store = str(data.iat[line, 0])
            if store == 'nan':
                url = txt_data[line]
                print(line, store, url)
                title, content = get_detail(browser, url)
                title.append('url')
                content.append(url)
                print(title)
                print(content)
                data = pd.DataFrame(data=pd.np.insert(data.values, line, content, axis=0), columns=title)
                data = data.drop([line + 1], axis=0)
        except Exception:
            continue
    data.to_excel(os.getcwd() + xls, index=False)


class RetryThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print('starting ' + self.name)
        fill_blank(self.name)


def retry_xls():
    start_time = time.time()
    threads = []
    list_arr = [f for f in os.listdir(os.getcwd()) if f[-3:] == 'txt']
    for f in list_arr:
        print()
        thread = RetryThread(f[:-4])
        threads.append(thread)
        thread.start()
    [t.join() for t in threads]
    elapsed_time = time.time() - start_time
    print('all thread end in : ' + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))


if __name__ == '__main__':
    # get_detail_xls()
    # retry_xls()
    arr = [f for f in os.listdir(os.getcwd()) if f[-4:] == 'xlsx']
    all_data = []
    with pd.ExcelWriter(param.file_name + '.xlsx') as writer:
        try:
            for xls in arr:
                print(xls)
                data = get_file_pd('\\' + xls)
                all_data.append(data)
                # all_xls = all_xls.append(data, ignore_index=True, sort=False)
        finally:
            # print(all_xls)
            all_xls = pd.concat(all_data)
            all_xls.to_excel(writer, merge_cells=False, index=False)
    writer.close()
