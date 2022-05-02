from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_mongoengine import MongoEngine
from mongoengine.fields import (IntField,
                                StringField,
                                BooleanField,
                                ObjectIdField,
                                DateTimeField)
mysqlDB = SQLAlchemy()
mongoDB = MongoEngine()


class News(mysqlDB.Model):
    """ 新闻模型 """
    __tablename__ = 'news'
    id = mysqlDB.Column(mysqlDB.Integer, primary_key=True)
    title = mysqlDB.Column(mysqlDB.String(200), nullable=False, comment='标题')
    img_url = mysqlDB.Column(mysqlDB.String(200), nullable=False, comment='主图地址')
    content = mysqlDB.Column(mysqlDB.String(2000), nullable=False, comment='新闻内容')
    is_valid = mysqlDB.Column(mysqlDB.Boolean, default=True, comment='逻辑删除')
    is_top = mysqlDB.Column(mysqlDB.Boolean, default=False, comment='是否置顶')
    created_at = mysqlDB.Column(mysqlDB.DateTime, default=datetime.now(), comment='创建时间')
    updated_at = mysqlDB.Column(mysqlDB.DateTime, default=datetime.now(), comment='最后修改时间')
    news_type = mysqlDB.Column(mysqlDB.Enum('本地', '百家', '娱乐', '军事'), comment='新闻类别')

    def get_comments(self):
        """评论列表"""
        # TODO 借用于分页的方式来实现
        queryset = Comments.objects.filter(object_id=self.id, is_valid=True)
        return queryset

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'img_url': self.img_url,
            'content': self.content,
            'news_type': self.news_type,
            'created_at': self.created_at.strftime('%Y-%m-%d'),
        }


class Comments(mongoDB.Document):
    """ 评论的ODM模型 """
    # 新闻（对象）ID，评论内容，逻辑删除、评论回复的ID，评论ID, 新增时间，修改时间
    object_id = IntField(required=True, verbose_name='关联的对象（新闻的ID）')
    content = StringField(required=True, max_length=2000, verbose_name='评论的内容')
    is_valid = BooleanField(default=True, verbose_name='是否有效')
    reply_id = ObjectIdField(verbose_name='回复评论的ID')
    created_at = DateTimeField(default=datetime.now(), verbose_name='创建时间')
    updated_at = DateTimeField(default=datetime.now(), verbose_name='最后修改时间')

    meta = {
        # 所存放的集合
        'collection': 'comments',
        # 排序规则：是否有效（有效的在前）、发布的时间倒序
        'ordering': ['-is_valid', '-created_at']
    }

    @property
    def news_obj(self):
        """新闻的对象"""
        return News.query.get(self.object_id)

    def __str__(self):
        return f'Comments: {self.content}'
