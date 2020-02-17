import json
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify
from flask_admin.contrib.sqla import ModelView

import config
from exts import db
from models import User, Card_Pf, Card_normal, Article, ActivationCode, Game, GamePost, Badge, Map
from forms import PostForm, LoginForm, RegistrationForm, CharacterFromNormal, CreateGameForm, GamePostForm, JoinGameForm

from flask_mail import Mail, Message
from flask_admin import Admin
from flask_login import current_user, login_user, LoginManager, logout_user, login_required

from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import expose

import pymysql

from utils import get_key, post_process, delete_game, jinja2_roll_dice
pymysql.install_as_MySQLdb()

from flask_pagedown import PageDown
import markdown

# from flask_socketio import SocketIO, emit


class BaseModelView(ModelView):
    can_delete = True  # disable model deletion
    page_size = 50  # the number of entries to display on the list view
    can_view_details = True

    @expose('/admin/')
    def user(self):
        return self.render('user.html')

    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))


# Activation Mode
Activation_mode = True

# Create and Initial app
app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

# Initial SocketIO
# socketio = SocketIO(app)

# Jinja2 global function
app.add_template_global(jinja2_roll_dice, 'jinja2_roll_dice')

# Create and Initial mail
mail = Mail(app)


# Create and Initial loginManager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Access denied.'
login_manager.init_app(app)


# Create and Initial admin
admin = Admin(app, name='控制台', template_mode='bootstrap3')
admin.add_view(BaseModelView(User, db.session, name='用户管理', category='User'))
admin.add_view(BaseModelView(Card_Pf, db.session, name='Pathfinder', category='Card'))
admin.add_view(BaseModelView(Card_normal, db.session, name='Normal', category='Card'))
admin.add_view(BaseModelView(Article, db.session, name='Article'))
admin.add_view(BaseModelView(Game, db.session, name='Games'))
admin.add_view(BaseModelView(ActivationCode, db.session, name='激活码管理'))
admin.add_view(BaseModelView(Badge, db.session, name='徽章管理'))


# Create pagedown instance
pagedown = PageDown()
pagedown.init_app(app)



@app.route('/')
def home():
    return render_template('home.html', year=datetime.now().year, title='PocketTRPG')


@app.route('/index')
@login_required
def index():
   if current_user.is_anonymous:
       flash('Please login first.')
       return redirect(url_for('login'))
   else:
       user_id = current_user.get_id()
       card_list = []

       card = Card_normal.query.filter(Card_normal.user_id == user_id).all()
       for item in card:
           card = {'name': item.name, 'features': item.features, 'tag': item.tag, 'content': item.content,
                   'card_id': item.card_id}
           card_list.append(card)
       return render_template('index.html', title='Index', year=datetime.now().year, card_list=card_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
   # 创建表单对象, 如果是post请求，前端发送了数据，flask会把数据在构造form对象的时候，存放到对象中
   form = LoginForm()

   if request.method == 'POST':
       # 判断form中的数据是否合理
       # 如果form中的数据完全满足所有的验证器，则返回真，否则返回假
       if form.validate_on_submit():
           # 表示验证合格
           # 提取数据
           email = form.email.data
           password = form.password.data
           remember = form.remember_me.data

           user = User.query.filter(User.email == email).first()
           if user:
               if check_password_hash(user.password_hash, password):
                   session['user_id'] = user.user_id
                   curr_user = user

                   # 通过Flask-Login的login_user方法登录用户
                   login_user(curr_user)

                   if remember:
                       session.permanent = True
                   return redirect(url_for('home'))
               else:
                   flash('密码错误，请检查密码')
           else:
               flash('用户不存在')
       else:
           if len(form.email.errors) is not 0:
               flash(form.email.errors[0])
           elif len(form.password.errors) is not 0:
               flash(form.password.errors[0])

   # GET 请求
   return render_template('login.html', year=datetime.now().year, form=form, title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
   # 创建表单对象, 如果是post请求，前端发送了数据，flask会把数据在构造form对象的时候，存放到对象中
   form = RegistrationForm()

   if request.method == 'POST':
       # 根据验证模式进行激活码验证
       if Activation_mode:
           activation_code = form.activation_code.data
           # 验证激活码
           code = ActivationCode.query.filter(ActivationCode.code == activation_code).first()
           if not code:
               flash('验证码不存在')
               return render_template('register.html', year=datetime.now().year, form=form, title='Registry')
           if code.used:
               flash('验证码已失效')
               return render_template('register.html', year=datetime.now().year, form=form, title='Registry')
           else:
               code.used = True

       # 判断form中的数据是否合理
       # 如果form中的数据完全满足所有的验证器，则返回真，否则返回假
       if form.validate_on_submit():
           # 表示验证合格
           # 提取数据
           username = form.username.data
           email = form.email.data
           password1 = form.password.data

           user = User()
           user.email = email
           user.username = username
           user.password_hash = generate_password_hash(password1)
           user.role = 'User'
           user.user_ip_address = request.remote_addr

           # db.session.commit 后同时进行激活码核销
           db.session.add(user)
           db.session.commit()
           session['user_email'] = email
           return redirect(url_for('send_mail'))
       else:
           if len(form.username.errors) is not 0:
               flash(form.username.errors[0])
           elif len(form.email.errors) is not 0:
               flash(form.email.errors[0])
           elif len(form.password.errors) is not 0:
               flash(form.password.errors[0])
           elif len(form.password2.errors) is not 0:
               flash(form.password2.errors[0])
           elif len(form.activation_code.errors) is not 0:
               flash(form.activation_code.errors[0])
   # GET 请求
   return render_template('register.html', year=datetime.now().year, form=form, title='Registry')


@app.route('/logout')
def logout():
   logout_user()
   # session['user_id'].pop()
   return redirect(url_for('home'))


@app.route('/user_info/<user_id>')
def user_info(user_id):
   if current_user.get_id() == user_id:
       user = User.query.filter(User.user_id == user_id).first()
       return render_template('user_info.html', user=user)
   flash('用户只能访问自己的个人资料')
   return redirect(url_for('index'))


@app.route('/characters/', methods=['GET', 'POST'])
@login_required
def character():
   if request.method == 'GET':
       return render_template('character.html', year=datetime.now().year)
   else:
       name = request.form.get('name')
       features = request.form.get('features')

       card = Card_Pf()
       card.user_id = current_user.get_id()
       card.name = name
       card.features = features
       card.tag = 'Pathfinder'

       user = User.query.filter(User.user_id == card.user_id).first()
       update_num = user.num_card + 1
       res = db.session.query(User).filter(User.user_id == card.user_id).update({"num_card": update_num})
       db.session.add(card)
       db.session.commit()
       return redirect(url_for('index'))


@app.route('/edit_card_normal/', methods=['GET', 'POST'])
@login_required
def edit_normal():
   form = CharacterFromNormal()
   if request.method == 'GET':
       return render_template('edit_card_normal.html', year=datetime.now().year, form=form)
   else:
       card = Card_normal()
       card.user_id = current_user.get_id()
       card.name = form.name.data
       card.features = form.features.data
       card.content = form.content.data
       card.data = '{' + form.custom.data + '}'
       card.tag = 'Normal'

       user = User.query.filter(User.user_id == card.user_id).first()
       update_num = user.num_card + 1
       res = db.session.query(User).filter(User.user_id == card.user_id).update({"num_card": update_num})
       db.session.add(card)
       db.session.commit()
       return redirect(url_for('index'))


@app.route('/save_normal_card/<name>/<features>/<content>/<card_id>')
@login_required
def save_normal_card(name, features, content, card_id):
   card = Card_normal.query.filter(Card_normal.card_id == card_id).first()
   card.name = name
   card.features = features
   card.content = content
   db.session.commit()
   return redirect(url_for('index'))


@app.route('/delete_normal_card/<card_id>')
@login_required
def delete_normal_card(card_id):
   card = Card_normal.query.filter(Card_normal.card_id == card_id).first()
   db.session.delete(card)
   db.session.commit()
   flash('角色已删除')
   return redirect(url_for('index'))


@app.route('/show_card_normal/<card_id>')
@login_required
def show_normal(card_id):
   card = Card_normal.query.filter(Card_normal.card_id == card_id).first()
   content = card.content
   if int(current_user.get_id()) == card.user_id or card.public:
       content = markdown.markdown(content)
       if card.data:
           data = json.loads(card.data)
       else:
           data = 0
       return render_template('show_card_normal.html', year=datetime.now().year, title=card.name, content=content,
                              card=card, data=data)
   else:
       flash('用户信息核对错误')
       return redirect(url_for('index'))


@app.route('/create_game', methods=['GET', 'POST'])
@login_required
def create_game():
   form = CreateGameForm()
   if request.method == 'POST':
       if form.validate_on_submit():
           game = Game()
           game.title = form.title.data
           game.comment = form.comment.data
           game.password = form.password.data
           game.member_limit = form.num_limit.data
           game.author_id = current_user.get_id()

           db.session.add(game)
           print('Error1')
           user = User.query.filter(User.user_id == current_user.get_id()).first()
           print('Error2')
           user.games.append(game)
           print('Error3')
           db.session.commit()

           flash('创建成功')
       else:
           if len(form.title.errors) is not 0:
               flash(form.title.errors[0])
           elif len(form.comment.errors) is not 0:
               flash(form.comment.errors[0])
           elif len(form.password.errors) is not 0:
               flash(form.password.errors[0])
   # GET 请求
   return render_template('create_game.html', year=datetime.now().year, form=form, title='Create New Game')


@app.route('/view_games_list')
@login_required
def view_games_list():
   if current_user.is_anonymous:
       flash('Please login first.')
       return redirect(url_for('login'))
   user = User.query.filter(User.user_id == current_user.get_id()).first()
   games_list = user.games
   return render_template('view_games_list.html', title='Game List', year=datetime.now().year, games_list=games_list)


@app.route('/view_game/<game_id>/<group>', methods=['GET', 'POST'])
@login_required
def view_game(game_id, group=1):
   game_id = int(game_id)
   # 获取game对象
   game = Game.query.filter(Game.game_id == game_id).first()
   # 获取post_list对象
   post_list = GamePost.query.filter(GamePost.game_id == game_id, GamePost.group_id == group).order_by(
       GamePost.post_id.desc()).all()
   users = game.users
   val = False
   for item in users:
       if item.user_id == int(current_user.get_id()):
           val = True
   if val:
       current_user_id = int(current_user.get_id())
       current_user_username = current_user.get_username()
       form = GamePostForm()
       # POST 请求
       if request.method == 'POST':
           if form.validate_on_submit():
               gp = GamePost()
               if len(form.speaker.data) is not 0:
                   gp.speaker = form.speaker.data
                   session['name'] = form.speaker.data
               else:
                   if session.get('name'):
                       gp.speaker = session.get('name')
                   else:
                       gp.speaker = 'Speaker'
               if len(form.send_to.data) is not 0:
                   gp.send_to = form.send_to.data
               # 建立新的GamePost对象
               gp.content = post_process(form.post.data, current_user_id=current_user_id)
               gp.author_id = current_user_id
               gp.game_id = game.game_id
               gp.group_id = group
               # 游戏长度增加
               game.length += 1

               db.session.add(gp)
               db.session.commit()
               return redirect(url_for('view_game', game_id=game_id, group=group))
       # GET 请求
       return render_template('view_game.html', year=datetime.now().year, form=form, title=game.title, game=game,
                              group=group, post_list=post_list, current_user_id=current_user_id,
                              username=current_user.get_username(), current_user_username=current_user_username)
   else:
       flash('进入游戏失败')
       return redirect(url_for('join_game'))


# SocketIO 路由监听
# @socketio.on('server_response', namespace='/test')
# def update_gameposts(game_id, group):
#     post_list = GamePost.query.filter(GamePost.game_id == game_id, GamePost.group_id == group).order_by(
#         GamePost.post_id.desc()).all()
#     emit('response', {'post_list': post_list})
#     time.sleep(5)


@app.route('/add_game_post/<author_id>/<post>/<game>/<group>/<send_to>/')
@login_required
def add_game_post(author_id, post, game, group, send_to):
   gp = GamePost()

   # 建立新的GamePost对象
   gp.send_to = send_to
   gp.content = post
   gp.author_id = author_id
   gp.game_id = game.game_id
   gp.group_id = group
   # 游戏长度增加
   game.length += 1

   db.session.add(gp)
   db.session.commit()
   return redirect(url_for('view_game', game_id=game.game_id, group=group))


@app.route('/add_game_group/<game_id>/<user_id>')
@login_required
def add_game_group(game_id, user_id):
   num_limit = 10
   game = Game.query.filter(Game.game_id == game_id).first()
   if game.num_group < num_limit:
       if int(user_id) == game.author_id:
           game.num_group += 1
           db.session.commit()
       else:
           flash('增加频道需要创建者权限')
   else:
       flash('频道数量过多，创建失败')
   return redirect(url_for('view_game', game_id=game_id, group=1))


@app.route('/join_game/', methods=['GET', 'POST'])
@login_required
def join_game():
   form = JoinGameForm()
   # POST 请求
   if request.method == 'POST':
       # 验证Form
       if form.validate_on_submit():
           game = Game.query.filter(Game.game_id == form.game_id.data).first()
           if game:
               if game.validate_password(form.password.data):
                   if game.num_member < game.member_limit:
                       user = User.query.filter(User.user_id == int(current_user.get_id())).first()
                       user.games.append(game)
                       game.users.append(user)
                       game.num_member += 1
                       db.session.commit()
                       session['name'] = form.name.data
                       flash('已加入游戏： ' + game.title)
                       return redirect(url_for('view_games_list'))
                   else:
                       flash('房间已满')
                       return redirect(url_for('join_game'))
               else:
                   flash('密码错误')
                   return redirect(url_for('join_game'))
           else:
               flash('游戏不存在')
               return redirect(url_for('join_game'))
   # GET 请求
   return render_template('join_game.html', year=datetime.now().year, form=form, title='Join Game')


@app.route('/exit_game/<game_id>')
@login_required
def exit_game(game_id):
   user_id = int(current_user.get_id())
   # Search
   user = User.query.filter(User.user_id == user_id).first()
   game = Game.query.filter(Game.game_id == game_id).first()
   # Remove
   game.users.remove(user)
   game.num_member -= 1
   if game.num_member == 0:
       delete_game(game)
   db.session.commit()
   flash('已退出游戏:  ' + game.title)
   return redirect(url_for('view_games_list'))


@app.route('/change_game_state/<game_id>&<state>')
@login_required
def change_game_state(game_id, state):
   game = Game.query.filter(Game.game_id == game_id).first()
   game.state = state
   db.session.commit()
   return redirect(url_for('view_game', game_id=game_id, group=1))


@app.route('/delete_own_game/<game_id>')
@login_required
def delete_own_game(game_id):
   game = Game.query.filter(Game.game_id == game_id).first()
   delete_game(game)
   flash('已退出游戏:  ' + game.title)
   return redirect(url_for('view_games_list'))


@app.route('/public_games')
@login_required
def public_games():
   games_list = Game.query.filter(Game.state == "Open").limit(10)
   return render_template('public_games.html', title='Public Games', games_list=games_list)


@app.route('/view_map/<map_id>')
def view_map(map_id):
   map = Map.query.filter(Map.map_id == map_id).first()
   if map.data:
       print(map.data)
       data = json.loads(map.data)
       print(data)
   else:
       data = 0
   return render_template('view_map.html', title=map.game.title, map=map, data=data)


@app.route('/document/')
def doc():
   return render_template('document.html', year=datetime.now().year)


@app.route('/mail')
def send_mail():
   # email = session.get('user_email')
   # msg = Message('Register Success!',
   #               sender=('PocketCharacters', 'pocketcharacter@163.com'),
   #               recipients=[email])
   # msg.html = '<h1>Hello Player</h1>' \
   #            '<p>Welcome to join PocketCharacter and Create your online TRPG Role Cards.</p>'
   # mail.send(msg)
   flash('确认邮件已发送')
   return redirect(url_for('login'))


@app.route('/article')
def article():
   # flash('模块装修中')
   article_num = 10
   article_list = Article.query.order_by(Article.create_time.desc()).limit(article_num)
   return render_template('article.html', year=datetime.now().year, title='Articles', article_list=article_list)


@app.route('/publish', methods=['GET', 'POST'])
@login_required
def publish():
   # 创建表单对象, 如果是post请求，前端发送了数据，flask会把数据在构造form对象的时候，存放到对象中
   form = PostForm()
   if request.method == 'POST':
       # 判断form中的数据是否合理
       if form.validate_on_submit():
           article = Article()
           article.content = form.body.data
           article.title = form.title.data
           article.author_id = current_user.get_id()
           article.tag = form.tag.data

           db.session.add(article)
           db.session.commit()
           flash('提交成功，返回讨论区')
           return redirect(url_for('article'))
       else:
           if len(form.body.errors) is not 0:
               flash('Body' + form.body.errors[0])
           if len(form.title.errors) is not 0:
               flash('Title' + form.title.errors[0])
       # GET 请求
   return render_template('publish.html', year=datetime.now().year, title='Publish', form=form)


@app.route('/detail/<article_id>', methods=['GET', 'POST'])
def detail(article_id):
   article = Article.query.filter(Article.article_id == article_id).first()
   content = article.content
   content = markdown.markdown(content)
   current_user_id = current_user.get_id()
   if current_user.is_anonymous:
       pass
   else:
       current_user_id = int(current_user_id)
   return render_template('detail.html', year=datetime.now().year, title=article.title, article=article,
                          content=content, current_user_id=current_user_id)


@app.route('/change_state/<article_id>&<state>')
def change_article_state(article_id, state):
   article = Article.query.filter(Article.article_id == article_id).first()
   article.state = state
   db.session.commit()
   return redirect(url_for('detail', article_id=article_id))


@app.route('/mods')
def mods():
   flash('模块装修中')
   return redirect(url_for('home'))


# 生成激活码
@app.route('/GenerateAC/')
@login_required
def generate_ac(num=10):
   num = int(num)
   for i in range(num):
       code = get_key()
       check = ActivationCode.query.filter(ActivationCode.code == code).first()
       if check:
           pass
       else:
           ac = ActivationCode()
           ac.code = code
           db.session.add(ac)
           db.session.commit()
   flash('Generate %d Activation Codes' % num)
   return redirect(url_for('home'))


# 提取激活码
@app.route('/GetAC/')
@login_required
def get_ac():
   code = ActivationCode.query.filter(ActivationCode.used == 0).first()
   flash(code.code)
   return redirect(url_for('home'))


@app.context_processor
def login_context_processor():
   if current_user.is_anonymous:
       return {}
   user_id = current_user.get_id()
   if user_id:
       user = User.query.filter(User.user_id == user_id).first()
       if user:
           return {'user': user}


@login_manager.user_loader
def load_user(user_id):
   user = User.query.filter(User.user_id == user_id).first()
   if user is not None:
       curr_user = User()
       curr_user.user_id = user_id
       curr_user.role = user.role
       curr_user.username = user.username

       return curr_user


if __name__ == '__main__':
   # socketio.run(app)
   app.run()
