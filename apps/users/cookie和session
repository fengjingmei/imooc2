1. 每个请求在headers或者url的参数中加上username
    安全性
2. 每个请求在headers或者url的参数中加上username和password
    安全性

3. 给用户一串随机字符串(令牌)，字符串满足几个条件，session
    1. 够随机
    2. 这个字符串是由服务器生成的
    3. 这个字符串需要和用户对应起来


1. 登录的过程(django)

	1. 查询用户
	2. login的逻辑
		1. 先将用户的基本信息组成json，然后加密生成加密的session字符串
		2. 随机生成一串长的字符，叫做sessionid
		3. 将sessionid和session值绑定在一起保存到数据库中
		4. 将sessionid写入到cookie中
		5. 返回请求给浏览器

2. 浏览器

	1. 拿到文本发现里面在cookie中写入了sessionid
	2. 将cookie中的所有值(key:value)形式，写入到本地存储(文件)
	3. 后续的针对该网站的所有请求都会代码cookie

3. django是如何确定某个请求是否登录？

	1. 拦截器拦截所有的请求
	2. 在拦截器中发现了在cookie中的sessionid后，通过该sessionid查询到session，从session中解析出用户的id，通过id查询到用户
	3. 给每个request都设置一个属性-user
