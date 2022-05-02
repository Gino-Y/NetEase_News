import redis, json
from flask import current_app

from models import News


class BaseRedisConnection(object):
    def __init__(self):
        # 从配置文件读取redis相关的配置
        redis_config = current_app.config['REDIS_SETTINGS']
        pool = redis.ConnectionPool(
            **redis_config
        )
        self.conn = redis.Redis(
            connection_pool=pool
        )

    def __del__(self):
        """ 关闭连接 """
        print('开始关闭连接')
        try:
            self.conn.close()
        except Exception as e:
            print(e)

    def delete(self, key):
        """
        删除键值对
        :param key: key
        :return:
        """
        return self.conn.delete(key)


class NewsCache(BaseRedisConnection):

    def set_index_news(self):
        """ 缓存首页热点新闻信息 """
        queryset = News.query.filter(News.is_valid == True, News.is_top == True).all()
        news_list = []
        for item in queryset:
            print(item)
            news_list.append(item.to_dict())
        key = current_app.config['INDEX_NEWS_KEY']
        data = {
            key: news_list
        }
        result = self.conn.set(key, json.dumps(data))
        print('缓存完成：', result)
