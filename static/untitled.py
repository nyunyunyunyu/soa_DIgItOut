# -*- encoding: utf-8 -*-


import json
import re
import time
import datetime


rd = open('my_weibo_list.json', 'r')
my_weibo_list = json.loads(rd.read())
rd.close()

week = {'0': [], '1': [], '2': [], '3': [], '4': [], '5': [], '6': []}
timepoint = []
i = 0
for item in my_weibo_list['weibo_list']:
    if not '-' in item['created_at']:
        continue
    s = item['created_at'].encode('utf-8')
    ti = s.split(' ')
    date = ti[0].split('-')
    if len(date)==2:
        w = str(datetime.datetime(int(time.strftime('%Y')), int(date[0]),int(date[1])).strftime("%w"))
    elif len(date)==3:
        w = str(datetime.datetime(int(date[0]),int(date[1]),int(date[2])).strftime("%w"))
    week[ w ].append( ti[1] )
    timepoint.append( [int(w), int(ti[1].split(':')[0])*60+int(ti[1].split(':')[1]) ] )

# for day in week:
    # print len(week[day])

for i in timepoint:
    print i
