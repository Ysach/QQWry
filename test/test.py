# -*- coding:utf-8 -*-
# __author:    "Farmer"
# date:   2018/9/27
from qqwry import IPLoader

ip = IPLoader('../qqwry.dat')
ip_info = ip.get_ip_address_info('114.114.114.114')
with open('test.json', 'r+') as f:
    f.write(ip_info)

print ip_info
