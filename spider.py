import requests, re, json
from requests.exceptions import RequestException
from multiprocessing import Pool
from urllib import request
import os
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from lxml import etree

_headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
}

### Request
def get_one_page_urllib_request(url):
    try:
        req = request.Request(url, headers=_headers)
        res = request.urlopen(req)
        if res.status == 200:
            return res.read().decode('utf-8')
        return None
    except BaseException as e:
        print(url, e)
        return None

def get_one_page_urllib_opener(url):
    try:
        req = request.Request(url, headers=_headers)
        opener = request.build_opener()
        res = opener.open(req)
        if res.status == 200:
            return res.read().decode('utf-8')
        return None
    except BaseException as e:
        print(url, e)
        return None

def get_one_page_requests(url):
    try:
        response = requests.get(url, headers=_headers)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException as e:
        print(url, e)
        return None

### Parser
def parse_one_page_re(html):
    pattern = re.compile(r'<dd>.*?board-index.*?>(\d+)</i>'
                        +r'.*?data-src="(.*?)"'
                        +r'.*?name"><a.*?>(.*?)</a>'
                        +r'.*?star">(.*?)</p>'
                        +r'.*?releasetime">(.*?)</p>'
                        +r'.*?integer">(.*?)</i>'
                        +r'.*?fraction">(.*?)</i>.*?</dd>', re.DOTALL)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5] + item[6]
        }

def parse_one_page_bs4(html):
    html_soup = BeautifulSoup(html, 'lxml')
    dd_list = html_soup.select('dd')
    for dd in dd_list:
        # index = dd.find(class_='board-index').string ## type:bs4.element.NavigableString
        index = dd.select('.board-index')[0].get_text() ## type:str
        # print(type(index))
        # image = dd.find(class_='board-img')['data-src'] ## type:str
        image = dd.select('.board-img')[0].attrs['data-src'] ## type:str
        # print(type(image))
        title = dd.find(class_='name').a.string
        # title = dd.select('.name a')[0].get_text()
        actor = dd.select('.star')[0].get_text().strip()[3:]
        time = dd.select('.releasetime')[0].get_text().strip()[5:]
        score = dd.select('.score')[0].get_text().strip()
        yield {
            'index': index,
            'image': image,
            'title': title,
            'actor': actor,
            'time': time,
            'score': score
        }

def parse_one_page_pq(html):
    doc = pq(html)
    dd_items = doc('dd').items()
    for dd in dd_items:
        index = dd('.board-index').text()
        # index = dd.find('.board-index').text()
        image = dd('.board-img').attr('data-src')
        title = dd('.name a').text()
        actor = dd('.star').text().strip()[3:]
        time = dd('.releasetime').text().strip()[5:]
        score = dd('.score').text().strip()
        yield {
            'index': index,
            'image': image,
            'title': title,
            'actor': actor,
            'time': time,
            'score': score
        }

def parse_one_page_xpath(html):
    html = etree.HTML(html)
    dd_list = html.xpath('//dd')
    for dd in dd_list:
        index = dd.xpath('i')[0].text
        image = dd.xpath('a/img[2]/@data-src')[0]
        title = dd.xpath('.//p[@class="name"]/a')[0].text
        actor = dd.xpath('.//p[@class="star"]')[0].text.strip()[3:]
        time = dd.xpath('.//p[@class="releasetime"]')[0].text.strip()[5:]
        score = dd.xpath('.//i[@class="integer"]')[0].text.strip() + dd.xpath('.//i[@class="fraction"]')[0].text.strip()
        yield {
            'index': index,
            'image': image,
            'title': title,
            'actor': actor,
            'time': time,
            'score': score
        }


### Storage
def write_to_file(content):
    with open('result.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()

def save_image(image_url, title):
    images_dir = './images/'
    if not os.path.exists(images_dir):
        os.mkdir(images_dir)

    request.urlretrieve(image_url, images_dir+title+'.png')

    # content = requests.get(image_url).content
    # with open('images/'+title+'.png', 'wb') as f:
    #     f.write(content)
    #     f.close()

def main(offset):
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page_requests(url)
    if html:
        for item in parse_one_page_re(html):
            index = item['index']
            title = item['title']
            image_url = item['image']
            save_image(image_url, index+'_'+title)
            write_to_file(item)

if __name__ == '__main__':
    pool = Pool()
    pool.map(main, [i * 10 for i in range(10)])
    pool.close()
    pool.join()

    # for i in range(10):
    #     main(i * 10)

    # url = 'http://maoyan.com/board/4'
    # html = get_one_page_urllib_opener(url)
    # items = parse_one_page_xpath(html)
    # for item in items:
    #     print(item)