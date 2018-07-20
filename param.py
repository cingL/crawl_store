# start page
import math

page = 1
page_size = 100
total = 5511
step = 10
count = math.ceil(total / page_size) + 1
# link of detail
detail_prefix = 'http://218.60.146.218:8080/lndb/yp/ypLsLicenceActionWZ!show.do?'
file_name = '辽宁省药监局药店'


def get_list_link(num):
    """
    link of list
    :param num: page number
    """
    return 'http://218.60.146.218:8080/lndb/yp/ypLsLicenceActionWZ!listWZ.do?queryBean.pn=' + num.__str__() + '&queryBean.pageSize=' + page_size.__str__()
