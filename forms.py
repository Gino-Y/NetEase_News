from flask_wtf import FlaskForm
from wtforms import (StringField,
                     SubmitField,
                     TextAreaField,
                     SelectField,
                     DateField,
                     BooleanField,
                     HiddenField)
from wtforms.validators import DataRequired, Length, ValidationError

NEWS_TYPE_CHOICES = (
        ('本地', '本地'),
        ('百家', '百家'),
        ('军事', '军事'),
        ('娱乐', '娱乐'),
    )


def validate_content(form, field):
    """
    验证公用方法：可供多个表单类使用
    :param form: form表单对象
    :param field: 需要验证的某一列
    """
    value = field.data
    if len(value) <= 50:
        raise ValidationError("新闻内容长度不能少于50个字符2")
    return field


class NewsForm(FlaskForm):
    """ 新闻表单 """
    title = StringField(label='新闻标题', validators=[
                            DataRequired("请输入标题"),
                            Length(min=20, max=200, message='新闻标题的长度在20-200之间')
                        ],
                        description="请输入标题",
                        render_kw={"class": "form-control"})
    content = TextAreaField(label='新闻内容', validators=[DataRequired("请输入内容"), validate_content],
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

    # def validate_content(self, field):
    #     """
    #     验证新闻内容
    #     :return:
    #     """
    #     value = field.data
    #     if len(value) <= 50:
    #         raise ValidationError("新闻内容长度不能少于50个字符")
    #     return field


class CommentForm(FlaskForm):
    """ 评论表单 """
    object_id = HiddenField(label='关联的新闻', validators=[DataRequired("新闻ID不能为空")])
    reply_id = HiddenField(label='关联回复')
    content = TextAreaField(label='评论内容', validators=[DataRequired("请输入内容"),
                            Length(min=5, max=200, message='评论内容在5-200之间')],
                            description="请输入内容",
                            render_kw={"class": "form-control", "rows": 5})
    submit = SubmitField(label='提交评论',
                         render_kw={'class': 'btn btn-info'})