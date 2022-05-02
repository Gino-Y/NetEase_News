class DB(object):
    """项目配置文件"""
    # mysql数据库连接的配置
    HOST = '47.241.35.150'
    PORT = '3306'
    DATABASE = 'netease_news'
    USERNAME = 'root'
    PASSWORD = 'Kadfgo53254G'
    DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".format(username=USERNAME,
                                                                                            password=PASSWORD,
                                                                                            host=HOST,
                                                                                            port=PORT,
                                                                                            db=DATABASE)
    SQLALCHEMY_DATABASE_URI = DB_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = '123123'

    # mongoDB数据库连接的配置
    # 通过mongoDB_SETTINGS配置MongoEngine
    MONGODB_SETTINGS = {
        'db': 'netease_news',
        'host': '47.241.35.150',
        'port': 27017,
        'connect': True,
        'username': 'admin',
        'password': '123456',
        'authentication_source': 'admin'
    }

    REDIS_SETTINGS = {
        'db': 2,
        'host': 'localhost',
        'port': 6379,
        'max_connections': 20,
        # 自动进行结果的转换
        'decode_responses': True
    }
    # 首页新闻缓存的KEY
    INDEX_NEWS_KEY = 'index_news_key'

