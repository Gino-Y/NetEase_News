from datetime import datetime

from flask import (Flask,
                   render_template,
                   abort,
                   redirect,
                   flash,
                   request)
from flask_sqlalchemy import SQLAlchemy

from forms import NewsForm

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
app.config['SECRET_KEY'] = '123123'

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


'''
同步模型到数据库
Console执行
from app import db
db.create_all()
'''


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
                           news_list=news_list)


@app.route('/detail/<int:pk>/')
def detail(pk):
    """ 新闻详情页 """
    new_obj = News.query.get(pk)
    # 新闻是否已经被删除
    if not new_obj.is_valid:
        abort(404)
    return render_template('detail.html',
                           new_obj=new_obj)


@app.route('/admin/')
@app.route('/admin/<int:page>/')
def admin(page=1):
    """ 后台管理-新闻首页 """
    page_size = 3
    # offset = (page - 1) * page_size
    # page_data = News.query.limit(page_size).offset(offset)
    page_data = News.query.paginate(page=page, per_page=page_size)
    return render_template('admin/index.html',
                           page_data=page_data)


@app.route('/admin/news/add/', methods=['GET', 'POST'])
def news_add():
    """ 新增新闻 """
    # 手动关闭CSRF保护
    # form = NewsForm(csrf_enabled=False)
    form = NewsForm()
    if form.validate_on_submit():
        news_obj = News(
            title=form.title.data,
            content=form.content.data,
            img_url=form.img_url.data,
            news_type=form.news_type.data
        )
        db.session.add(news_obj)
        db.session.commit()
        print('新增成功')
        flash('新增新闻成功', 'success')
        return redirect('/admin/')
    else:
        print('表单没有通过验证', form.errors)
        flash('您的表单中还有错误，请修改', 'danger')
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
            db.session.add(news_obj)
            db.session.commit()
            flash('新闻修改成功', 'success')
            return redirect('/admin/')
        else:
            flash('您的表单中还有错误，请修改', 'danger')
    return render_template('admin/update.html', form=form)


if __name__ == '__main__':
    app.run()
