import codecs
import threading
import time

from bs4 import BeautifulSoup
from selenium import webdriver

import param


def get_id(href):
    return (href.split('?')[1].strip().replace(' ', '%20'))[:-1]


def get_detail_links(driver, url, times=0):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')  # timeout?
    try:
        table = soup.find(id='list')
        links = []
        for tr in table.find_all('tr'):
            if tr.get('ondblclick'):
                parameter = get_id(tr['ondblclick'])
                links.append(param.detail_prefix + parameter)
                print(param.detail_prefix + parameter)
        return links
    except Exception:
        if times < 3:
            get_detail_links(driver, url, times + 1)
        else:
            return None


def get_links(arr):
    driver = webdriver.Chrome()
    fail = []
    with codecs.open(param.file_name + '_link_' + str(arr[0]) + '-' + str(arr[1]) + '.txt', 'wb',
                     encoding='utf-8') as fp:
        for i in range(arr[0], arr[1]):
            try:
                links = get_detail_links(driver, param.get_list_link(i))
                for l in links:
                    fp.write(l + '\n')
            except Exception:
                fp.write(i.__str__() + ' fail \n')
                fail.append(i)
            continue
        fp.close()
    print(str(arr[0]) + '-' + str(arr[1]) + ' finish with ' + fail.__len__().__str__() + ' fail')


class CrawlLinkThread(threading.Thread):
    def __init__(self, arr):
        threading.Thread.__init__(self)
        self.arr = arr

    def run(self):
        print('starting ' + self.name)
        get_links(self.arr)


def get_all_detail_link():
    start_time = time.time()
    threads = []
    while param.page < param.count:
        end = param.page + param.step if param.page + param.step < param.count else param.count
        print([param.page, end])
        thread = CrawlLinkThread([param.page, end])
        threads.append(thread)
        thread.start()
        param.page += param.step
    [t.join() for t in threads]
    elapsed_time = time.time() - start_time
    print('all thread end in : ' + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))


if __name__ == '__main__':
    get_all_detail_link()
