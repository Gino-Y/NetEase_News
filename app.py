from datetime import datetime

from flask import (Flask,
                   render_template,
                   abort,
                   redirect,
                   flash,
                   request,
                   url_for)
from flask_sqlalchemy import SQLAlchemy
from flask_mongoengine import MongoEngine
from mongoengine.fields import (IntField,
                                StringField,
                                BooleanField,
                                ObjectIdField,
                                DateTimeField)


from forms import NewsForm, CommentForm

app = Flask(__name__)

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
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SECRET_KEY'] = '123123'

# mongodb数据库连接的配置
# 通过MONGODB_SETTINGS配置MongoEngine
app.config['MONGODB_SETTINGS'] = {
        'db': 'netease_news',
        'host': '47.241.35.150',
        'port': 27017,
        'connect': True,
        'username': 'admin',
        'password': '123456',
        'authentication_source': 'admin'
    }


# db = SQLAlchemy(app)
mysqldb = SQLAlchemy()
mysqldb.init_app(app=app)
mongodb = MongoEngine()
mongodb.init_app(app=app)


class News(mysqldb.Model):
    """ 新闻模型 """
    __tablename__ = 'news'
    id = mysqldb.Column(mysqldb.Integer, primary_key=True)
    title = mysqldb.Column(mysqldb.String(200), nullable=False, comment='标题')
    img_url = mysqldb.Column(mysqldb.String(200), nullable=False, comment='主图地址')
    content = mysqldb.Column(mysqldb.String(2000), nullable=False, comment='新闻内容')
    is_valid = mysqldb.Column(mysqldb.Boolean, default=True, comment='逻辑删除')
    is_top = mysqldb.Column(mysqldb.Boolean, default=False, comment='是否置顶')
    created_at = mysqldb.Column(mysqldb.DateTime, default=datetime.now(), comment='创建时间')
    updated_at = mysqldb.Column(mysqldb.DateTime, default=datetime.now(), comment='最后修改时间')
    news_type = mysqldb.Column(mysqldb.Enum('本地', '百家', '娱乐', '军事'), comment='新闻类别')


class Comments(mongodb.Document):
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
        'collection': 'netease_news',
        # 排序规则：是否有效（有效的在前）、发布的时间倒序
        'ordering': ['is_valid', '-created_at']
    }

    def __str__(self):
        return f'Comments: {self.content}'


@app.route('/')
def index():
    """ 首页 """
    news_list = News.query.filter(News.is_valid == True, News.is_top == True).all()
    return render_template('index.html',
                           news_list=news_list)


@app.route('/cat/<news_type>/')
def cat(news_type):
    """ 新闻分类页 """
    news_list = News.query.filter(News.news_type == news_type, News.is_valid == True).all()
    return render_template('cat.html',
                           news_list=news_list,
                           news_type=news_type)


@app.route('/detail/<int:pk>/')
def detail(pk):
    """ 新闻详情页 """
    new_obj = News.query.get(pk)
    form = CommentForm(data={'object_id': pk})
    if new_obj is None:
        abort(404)
    # 新闻是否已经被删除
    if not new_obj.is_valid:
        abort(404)
    return render_template('detail.html',
                           new_obj=new_obj,
                           form=form)


@app.route('/admin/')
@app.route('/admin/<int:page>/')
def admin(page=1):
    """ 后台管理-新闻首页 """
    page_size = 3
    # offset = (page - 1) * page_size
    # page_data = News.query.limit(page_size).offset(offset)
    title = request.args.get('title', '')
    page_data = News.query.filter_by(is_valid=True)
    # 根据标题进行模糊搜索
    if title:
        page_data = page_data.filter(News.title.contains(title))
    page_data = page_data.paginate(page=page, per_page=page_size)
    return render_template('admin/index.html',
                           page_data=page_data,
                           title=title)


@app.route('/admin/news/add/', methods=['GET', 'POST'])
def news_add():
    """ 新增新闻 """
    # 手动关闭CSRF保护
    # form = NewsForm(csrf_enabled=False)
    form = NewsForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            news_obj = News(
                title=form.title.data,
                content=form.content.data,
                img_url=form.img_url.data,
                news_type=form.news_type.data
            )
            mysqldb.session.add(news_obj)
            mysqldb.session.commit()
            print('新增成功')
            flash('新增成功', 'success')
            return redirect(url_for('admin'))
        else:
            flash('您的表单中还有错误，请修改', 'danger')
            print('表单没有通过验证', form.errors)
    return render_template('admin/add.html',
                           form=form)


@app.route('/admin/news/update/<int:pk>/', methods=['GET', 'POST'])
def news_update(pk):
    """ 修改新闻 """
    news_obj = News.query.get(pk)
    if not news_obj.is_valid:
        abort(404)
    form = NewsForm(obj=news_obj)
    if request.method == 'POST':
        if form.validate_on_submit():
            news_obj.title = form.title.data
            news_obj.content = form.content.data
            news_obj.img_url = form.img_url.data
            news_obj.news_type = form.news_type.data
            news_obj.is_top = form.is_top.data
            news_obj.updated_at = datetime.now()
            mysqldb.session.add(news_obj)
            mysqldb.session.commit()
            flash('新闻修改成功', 'success')
            return redirect(url_for('admin'))
        else:
            flash('您的表单中还有错误，请修改', 'danger')
    return render_template('admin/update.html', form=form)


@app.route('/admin/news/delete/<int:pk>/', methods=['POST'])
def news_delete(pk):
    """ 逻辑删除新闻 """
    if request.method == 'POST':
        news_obj = News.query.get(pk)
        # 新闻不存在
        if news_obj is None:
            return 'no'
        # 新闻已经被删除掉了
        if not news_obj.is_valid:
            return 'no'
        news_obj.is_valid = False
        mysqldb.session.add(news_obj)
        mysqldb.session.commit()
        return 'yes'
    return 'no'


@app.route('/comment/<int:news_id>/add/', methods=['POST'])
def comment_add(news_id):
    """ 新增评论 """
    new_obj = News.query.get(news_id)
    form = CommentForm(data={'object_id': news_id})
    if request.method == 'POST':
        if form.validate_on_submit():
            comment_obj = Comments(
                content=form.content.data,
                object_id=news_id
            )
            reply_id = form.reply_id.data
            if reply_id:
                comment_obj.reply_id = reply_id
            comment_obj.save()
            print('评论成功')
            flash('评论成功', 'success')
            return redirect(url_for('detail', pk=news_id))
        else:
            flash('您的表单中还有错误，请修改', 'danger')
            print('表单没有通过验证', form.errors)
    return render_template('detail.html',
                           form=form,
                           new_obj=new_obj)
