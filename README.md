# QQWry
纯真IP数据库解析qqwry.dat库文件。
QQWry IP数据库 纯真版收集了包括中国电信、中国移动、中国联通、长城宽带、聚友宽带等 ISP 的最新准确 IP 地址数据。IP数据库每5天更新一次，需要定期更新最新的IP数据库。

# 使用

	from qqwry import IPLoader

	ip = IPLoader('qqwry.dat')
	ip_info = ip.get_ip_address_info('114.114.114.114')
	
# Django使用

	Django通过request.GET.get()得到的字符是Unicode，范例如下：
	```
	def index(request):
    ip_dict = dict({"code": "", "data": {"ip": "", "info": "", "location": ""}})
    if request.method == "GET":
		ip = request.GET.get('ip', None)
        if ip is None:
            ip_dict["code"] = 0
            ip_dict["data"]["info"] = "请输入正确的KEY值或者非空的值,如:http://x.x.x.x?ip=8.8.8.8"

            return HttpResponse(json.dumps(ip_dict, indent=4, ensure_ascii=False))
        ip_info = IPLoader("QQWry/qqwry.dat").get_ip_address_info(ip.encode('utf-8'))
        return HttpResponse(ip_info)
    if request.method == "POST":
        ip = request.POST.get('ip', None)
        if ip is None:
            ip_dict["code"] = 0
            ip_dict["data"]["info"] = "请输入正确的KEY值或者非空的值,如:http://x.x.x.x?ip=8.8.8.8"

            return HttpResponse(json.dumps(ip_dict, indent=4, ensure_ascii=False))
        ip_info = IPLoader("QQWry/qqwry.dat").get_ip_address_info(ip.encode('utf-8'))
        return HttpResponse(ip_info)
	```
# 正确的数据返回JSON内容如下

	{
		"code": 0, 
		"data": {
			"info": "南京信风网络科技有限公司GreatbitDNS服务器", 
			"ip": "114.114.114.114", 
			"location": "江苏省南京市"
		}
	}

## 或者
	{
		"code": 0, 
		"data": {
			"info": "电信", 
			"ip": "1.2.127.28", 
			"location": "广东省"
		}
	}
# 错误返回的JSON格式

	{
		"code": 1,
		"data": {
			"info": "请输入合法的IP",
			"ip": "114.114.114.L",
			"location": ""
		}
	}

# 线上API接口地址
## API: https://www.ruyione.com/api/
## 使用 GET方法
	https://www.ruyione.com/api/?ip=1.1.1.1
## 使用 POST 方法
	curl https://www.ruyione.com/api/ -X POST -d "ip=1.1.1.1"

# 纯真数据库格式
	QQWry.Dat的格式如下:

	+----------+
	|  文件头  |  (8字节)
	+----------+
	|  记录区  | （不定长）
	+----------+
	|  索引区  | （大小由文件头决定）
	+----------+

	文件头：4字节开始索引偏移值+4字节结尾索引偏移值

	记录区： 每条IP记录格式 ==> IP地址[国家信息][地区信息]

	   对于国家记录，可以有三种表示方式：

		   字符串形式(IP记录第5字节不等于0x01和0x02的情况)，
		   重定向模式1(第5字节为0x01),则接下来3字节为国家信息存储地的偏移值
		   重定向模式(第5字节为0x02),
	   
	   对于地区记录，可以有两种表示方式： 字符串形式和重定向

	   最后一条规则：重定向模式1的国家记录后不能跟地区记录

	索引区： 每条索引记录格式 ==> 4字节起始IP地址 + 3字节指向IP记录的偏移值

	   索引区的IP和它指向的记录区一条记录中的IP构成一个IP范围。查询信息是这个
	   范围内IP的信息
	   
# 感谢

* 纯真数据库提供者： http://www.cz88.net/fox/ipdat.shtml