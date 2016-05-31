# soa_DIgItOut
Dig It Out Project
## Environment Requirement
MongoDB
PyMongo
## interface of the spider:
spider(inputid)
###input:
	userid
###output:
	output {
		'info_dict':{
			'name':'AnthonyWang',
			'home':'浙江 温州',
			'sex':'男'
		},
		'weibo_list':[
			{
				'text':'今天好高兴',
				'source':'iphone 5s',
				'location_name':'瑞安·锦湖街区',
				'location_lon':'120.62851',
				'location_lat':'27.79679',
				'created_at':'04-29 17:25',
				'pics_list':[
					'thumbnail_pic': url1,
					'bmiddle_pic': url2,
					'original_pic': url3
				]
			}
		]
	}

一些注意事项：

location中对check-in的地址信息还没正确考虑，发微博自带的地址可以找到经纬度。（不过需要自己找cookie才行）

created_at有时候会是10分钟前这种情况。

text中经常会有html的一些类似于\<span\>这种的东西。

cookie每次需要更新

直接运行spider.py可以查看得到的微博结果

## interface of the image_detect:
get_grouping_result(weibo)
weibo是spider的结果
### output:
(group, face_info)
group是一个list，例如
\[\[a1,a2\],\[a3,a4\]\]
\[a1,a2\]是同一个人的脸的编号
脸的相关信息可以在face_info中找到
http://www.faceplusplus.com.cn/detection_detect/