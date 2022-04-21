from flask_wtf import FlaskForm
from wtforms import (StringField,
                     SubmitField,
                     TextAreaField,
                     SelectField,
                     DateField,
                     BooleanField)
from wtforms.validators import DataRequired

NEWS_TYPE_CHOICES = (
        ('本地', '本地'),
        ('百家', '百家'),
        ('军事', '军事'),
        ('娱乐', '娱乐'),
    )


class NewsForm(FlaskForm):
    """ 新闻表单 """
    title = StringField(label='新闻标题', validators=[DataRequired("请输入标题")],
                        description="请输入标题",
                        render_kw={"class": "form-control"})
    content = TextAreaField(label='新闻内容', validators=[DataRequired("请输入内容")],
                            description="请输入内容",
                            render_kw={"class": "form-control", "rows": 5})
    news_type = SelectField('新闻类型',
                            choices=NEWS_TYPE_CHOICES,
                            render_kw={'class': 'form-control'})
    img_url = StringField(label='新闻图片',
                          description='请输入图片地址',
                          default='/static/img/news/new1.jpg',
                          render_kw={'required': 'required', 'class': 'form-control'})
    is_top = BooleanField(label='是否置顶')
    submit = SubmitField(label='提交',
                         render_kw={'class': 'btn btn-info'})
