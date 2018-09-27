# -*- coding:utf-8 -*-
# __author:    "Farmer"
# date:   2018/9/25
import socket
import logging
from struct import pack, unpack
import json


# 将整数的IP转换成IP号段，例如（18433024 ---> 1.25.68.0）
def convert_int_ip_to_string(ip_int):
    return socket.inet_ntoa(pack('I', socket.htonl(ip_int)))


# IP 转换为 整数
def convert_string_ip_to_int(str_ip):
    try:
        ip = unpack('I', socket.inet_aton(str_ip))[0]
    except Exception as e:
        # 如果IP不合法返回 None
        logging.info(e)
        return None
    # ((ip >> 24) & 0xff) | ((ip & 0xff) << 24) | ((ip >> 8) & 0xff00) | ((ip & 0xff00) << 8)
    else:
        return socket.ntohl(ip)


# 转换字符
def convert_str_to_utf8(gbk_str):
    try:
        return unicode(gbk_str, 'gbk').encode('utf-8')
    except Exception as e:
        # 当字符串解码失败，并且最一个字节值为'\x96',则去掉它，再解析
        logging.info(e)
        if gbk_str[-1] == '\x96':
            try:
                return unicode(gbk_str[:-1], 'gbk').encode('utf-8') + '?'
            except Exception as e:
                logging.info(e)
                pass

        return 'None'


# 获取offset 值
def get_offset(buffer_string):
        return unpack('I', buffer_string + '\0')[0]


class IPLoader(object):

    def __init__(self, file_name):
        self.file_name = file_name
        self.db_buffer = None
        self.open_db()
        (self.idx_start, self.idx_end, self.idx_count) = self._get_index()

    def open_db(self):
        if not self.db_buffer:
            self.db_buffer = open(self.file_name, 'rb')
        return self.db_buffer

    def _get_index(self):
        """
        读取数据库中IP索引起始和结束偏移值
        """
        self.db_buffer.seek(0)
        # 文件头 8个字节，4字节开始索引偏移值+4字节结尾索引偏移值
        index_str = self.db_buffer.read(8)
        start, end = unpack('II', index_str)
        count = (end - start) // 7 + 1
        return start, end, count

    def read_ip(self, offset):
        """
        读取ip值（4字节整数值）
        返回IP值
        """
        if offset:
            self.db_buffer.seek(offset)

        buf = self.db_buffer.read(4)
        return unpack('I', buf)[0]

    def get_offset(self, offset):
        if offset:
            self.db_buffer.seek(offset)

        buf = self.db_buffer.read(3)
        return unpack('I', buf + '\0')[0]

    def get_string(self, offset):
        """
        读取原始字符串（以"\0"结束）
        返回元组：字符串
        """
        if offset == 0:
            return 'None'

        flag = self.get_mode(offset)

        if flag == 0:
            return 'None'

        elif flag == 2:
            offset = self.get_offset(offset + 1)
            return self.get_string(offset)

        self.db_buffer.seek(offset)

        ip_string = ''
        while True:
            ch = self.db_buffer.read(1)
            if ch == b'\0':
                break
            ip_string += ch

        return ip_string

    def get_mode(self, offset):
        # 偏移指针位置
        self.db_buffer.seek(offset)
        c = self.db_buffer.read(1)
        if not c:
            return 0
        return ord(c)

    def get_mode_offset(self):
        buf = self.db_buffer.read(3)
        return get_offset(buf)

    def get_ip_record(self, offset):
        # 移动指针位置
        self.db_buffer.seek(offset)

        # 获取mode
        mode = ord(self.db_buffer.read(1))

        if mode == 1:
            mode_1_offset = self.get_mode_offset()
            mode_ip_location = self.get_string(mode_1_offset)
            mode_1 = self.get_mode(mode_1_offset)
            if mode_1 == 2:
                mode_ip_info = self.get_string(mode_1_offset + 4)
            else:
                mode_ip_info = self.get_string(mode_1_offset + len(mode_ip_location) + 1)

        elif mode == 2:

            mode_ip_location = self.get_string(self.get_mode_offset())
            mode_ip_info = self.get_string(offset + 4)

        else:
            mode_ip_location = self.get_string(offset)
            mode_ip_info = self.get_string(offset + len(mode_ip_location) + 1)

        return mode_ip_location, mode_ip_info

    def find_ip_index(self, ip, left, right):
        if right - left <= 1:
            return left

        middle = (left + right) / 2
        offset = self.idx_start + middle * 7

        new_ip = self.read_ip(offset)

        if ip < new_ip:
            return self.find_ip_index(ip, left, middle)
        else:
            return self.find_ip_index(ip, middle, right)

    # 获取IP地址信息, code = 0 正确返回， code = 1 错误返回
    def get_ip_address_info(self, ip):
        ip_dict = dict({"code": "", "data": {"ip": ip, "info": "", "location": ""}})
        ip = convert_string_ip_to_int(ip)
        if ip is None:
            ip_dict['code'] = 1
            ip_dict["data"]['info'] = '请输入合法的IP'
            return json.dumps(ip_dict, ensure_ascii=False)
        ip_dict['code'] = 0
        # ip 偏移
        ip_offset = self.find_ip_index(ip, 0, self.idx_count - 1)
        idx_offset = self.idx_start + ip_offset * 7
        address_offset = self.get_offset(idx_offset + 4)
        (location, info) = self.get_ip_record(address_offset + 4)
        ip_dict["data"]['location'] = convert_str_to_utf8(location)
        ip_dict["data"]['info'] = convert_str_to_utf8(info)
        # 不加 ensure_ascii=False
        # 输出的结果是{"info": "\u8054\u901a", "location": "\u5e7f\u4e1c\u7701\u6df1\u5733\u5e02"}
        return json.dumps(ip_dict, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    q = IPLoader('qqwry.dat')
    ip_info = q.get_ip_address_info('1.4.0.255')
    print ip_info
