import urllib.request as request
from urllib.parse import urlparse
from urllib.parse import urlsplit
response=request.urlopen('http://www.yc.cn/pet/gougou')
# print(response.read().decode('utf-8'))
result=urlsplit('http://www.baidu.com/index.html;user?id=5#comment')
print(result)
