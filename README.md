# soa_DIgItOut
Dig It Out Project
## Environment Requirement
MongoDB
PyMongo
## interface of the spider:
crawl(inputid)
###input:
	userid
###output:
	output (
	latest,
	{
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
				'pics':[
					'thumbnail_pic': url1,
					'bmiddle_pic': url2,
					'original_pic': url3
				]
			}
		]
	}
	)

一些注意事项：

latest表示数据是否是最新的（即是否返回了缓存数据）

location中对check-in的地址信息还没正确考虑，发微博自带的地址可以找到经纬度。（不过需要自己找cookie才行）

created_at有时候会是10分钟前这种情况。

text中经常会有html的一些类似于\<span\>这种的东西。

cookie每次需要更新

直接运行spider.py可以查看得到的微博结果

## interface of the image_detect:
get_grouping_result(weibo, need_update)
weibo是spider的结果, need_update是crawl返回的latest，表示是否要重新进行聚类
### output:
(group, face_info)
group是一个list，例如
\[\[a1,a2\],\[a3,a4\]\]
\[a1,a2\]是同一个人的脸的编号
脸的相关信息可以在face_info中找到
http://www.faceplusplus.com.cn/detection_detect/