# soa_DIgItOut
Dig It Out Project
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
				'location':'温州外滩大厦',
				'created_at':'04-29 17:25',
				'thumbnail_pic': url1,
				'bmiddle_pic': url2,
				'original_pic': url3
			}
		]
	}
	
一些注意事项：

location可能会有些问题，有时候会不一定是这个人发表微博的地址。

created_at有时候会是10分钟前这种情况。

text中经常会有html的一些类似于\<span\>这种的东西。

cookie每次需要更新

直接运行spider.py可以查看得到的微博结果
