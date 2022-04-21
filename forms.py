from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    """
    新闻表单
    """
    title = StringField(label='新闻标题',
                        description='请输入标题',
                        validators=[DataRequired('请输入标题')])

    submit = SubmitField('提交')
