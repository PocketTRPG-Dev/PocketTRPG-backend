# 引入Form基类
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, HiddenField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, NumberRange
from flask_wtf.file import FileRequired, FileAllowed
from models import User


class RegistrationForm(FlaskForm):
    username = StringField('用户名  Username', validators=[DataRequired()])
    email = StringField('邮箱地址  Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('输入密码  Input Password', validators=[DataRequired(), Length(min=6, max=20, message='密码应为6-20位')])
    password2 = PasswordField(
        '确认密码  Confirm Password', validators=[DataRequired(), EqualTo('password', message='两次输入密码不相同')])
    invitation_code = StringField('Invitation Code')
    activation_code = StringField('激活码  Activation Code')

    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('该用户名已被注册')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('该邮箱已被注册')


class LoginForm(FlaskForm):
    email = StringField(label='Email Address', validators=[DataRequired(message='用户名不能为空'), Email(message='无效的邮箱地址')])
    password = PasswordField(label='Password',
                             validators=[DataRequired(message='密码不能为空'), Length(min=6, max=20, message='密码应为6-20位')])
    remember_me = BooleanField(label='记住我')
    submit = SubmitField(label='Sign In')


class PostForm(FlaskForm):
    title = StringField('标题', [DataRequired(), Length(max=255)])
    body = TextAreaField('内容', [DataRequired()])
    tag = StringField('标签', [DataRequired(), Length(max=20)])
    state = StringField(label='帖子状态', validators=[DataRequired(), Length(max=20)])
    # categories = SelectField('文章种类', choices=[], coerce=int)
    body_html = HiddenField()
    submit = SubmitField(render_kw={'value': "提交", 'class': 'btn btn-primary pull-right', 'type': 'submit'})


class UpdateFrom(FlaskForm):
    state = StringField('帖子状态', [DataRequired(), Length(max=20)])


class CharacterFromNormal(FlaskForm):
    name = StringField(label='角色名称', validators=[DataRequired(), Length(max=20)])
    features = StringField(label='角色特性', validators=[DataRequired(), Length(max=20)])
    tag = StringField(label='标签', validators=[DataRequired(), Length(max=20)])
    content = TextAreaField(label='内容', validators=[DataRequired()])
    custom = TextAreaField(label='内容', validators=[DataRequired()])


class CreateGameForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    comment = StringField(label='备注', validators=[DataRequired()])
    password = PasswordField(label='房间密码', validators=[DataRequired()])
    num_limit = IntegerField(label='人数限制', validators=[DataRequired(), NumberRange(min=1, max=10)])

    submit = SubmitField(label='Create')


class GamePostForm(FlaskForm):
    speaker = StringField(label='Speaker')
    post = StringField(label='Post', validators=[DataRequired()])
    send_to = StringField(label='Send To')


class JoinGameForm(FlaskForm):
    game_id = IntegerField(label='游戏ID', validators=[DataRequired()])
    password = PasswordField(label='房间密码', validators=[DataRequired()])
    name = StringField(label='角色名称', validators=[DataRequired()])