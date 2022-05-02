from datetime import datetime

from flask import (Flask,
                   render_template,
                   abort,
                   redirect,
                   flash,
                   request,
                   url_for)
import config
from cache import NewsCache
from forms import NewsForm, CommentForm
from models import mysqlDB, mongoDB, News, Comments

app = Flask(__name__)

app.config.from_object(config.DB)

mysqlDB.init_app(app)
mongoDB.init_app(app)


@app.route('/')
def index():
    """ 首页 """
    # news_list = News.query.filter(News.is_valid == True, News.is_top == True).all()
    cache_obj = NewsCache()
    news_list = cache_obj.get_index_news()
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
                is_top=form.is_top.data,
                news_type=form.news_type.data
            )
            mysqlDB.session.add(news_obj)
            mysqlDB.session.commit()
            # 缓存新闻信息
            if news_obj.is_top:
                cache_obj = NewsCache()
                cache_obj.set_index_news()
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
            mysqlDB.session.add(news_obj)
            mysqlDB.session.commit()
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
        mysqlDB.session.add(news_obj)
        mysqlDB.session.commit()
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


@app.route('/admin/comment/')
@app.route('/admin/comment/<int:page>/')
def admin_comment(page=1):
    """ 后台管理-评论管理 """
    # 每页放5条数据
    page_size = 5
    page_data = Comments.objects.all()
    page_data = page_data.paginate(page=page, per_page=page_size)
    return render_template('admin/comments.html',
                           page_data=page_data)


@app.route('/admin/comment/delete/<string:pk>/', methods=['POST'])
def comment_delete(pk):
    """ 逻辑删除评论 """
    if request.method == 'POST':
        comment_obj = Comments.objects.filter(id=pk).first()
        # 评论不存在
        if comment_obj is None:
            return 'no'
        # 评论已经被删除掉了
        if not comment_obj.is_valid:
            return 'no'
        comment_obj.is_valid = False
        comment_obj.save()
        return 'yes'
    return 'no'


if __name__ == '__main__':
    app.run()
