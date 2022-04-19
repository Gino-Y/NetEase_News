from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 数据库连接的配置
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
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI

db = SQLAlchemy(app)


class News(db.Model):
    """ 新闻模型 """
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, comment='标题')
    img_url = db.Column(db.String(200), nullable=False, comment='主图地址')
    content = db.Column(db.String(2000), nullable=False, comment='新闻内容')
    is_valid = db.Column(db.Boolean, default=True, comment='逻辑删除')
    is_top = db.Column(db.Boolean, default=False, comment='是否置顶')
    created_at = db.Column(db.DateTime, default=datetime.now(), comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now(), comment='最后修改时间')
    news_type = db.Column(db.Enum('本地', '百家', '娱乐', '军事'), comment='新闻类别')

# 同步模型到数据库
# from app import db
# db.create_all()


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
