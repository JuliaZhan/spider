import requests
import re
import json
import csv

with open('breeds.csv','w') as f:
    writer = csv.writer(f)
    writer.writerow(['firstWord', 'name'])
    for i in range(32):
        url='http://www.yc.cn/api/searchPetData.do?petRaceId=1&pageSize=8&pageNum='+str(i+1)
        response=requests.get(url)
        res = response.text[1:-1]
        dic = json.loads(res)
        for pet in dic['list']:
            writer.writerow([pet['fisrtWord'], pet['name']])
            # print(pet['fisrtWord']+pet['name'])
            # f.write(json.dumps(pet['fisrtWord']+pet['name'],ensure_ascii=False,)+'\n')

