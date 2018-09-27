# QQWry
纯真IP数据库解析

# 使用

	from qqwry import IPLoader

	ip = IPLoader('../qqwry.dat')
	ip_info = ip.get_ip_address_info('114.114.114.114')
	

# 正确的数据返回JSON格式

	{
		"code": 0, 
		"data": {
			"info": "南京信风网络科技有限公司GreatbitDNS服务器", 
			"ip": "114.114.114.114", 
			"location": "江苏省南京市"
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