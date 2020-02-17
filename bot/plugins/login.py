from nonebot import on_command, CommandSession
from models import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from FlaskWeb.config import DB_URI

# Database Config
# HOSTNAME = '127.0.0.1'
# PORT = '3306'
# DATABASE = 'Pocket'
# USERNAME = 'root'
# PASSWORD = 'h1951116'
# DB_URI = 'mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)

# Create SqlAlchemy engine
engine = create_engine(DB_URI)

# Create Session
Session = sessionmaker(bind=engine)
sess = Session()


@on_command('login', only_to_me=False)
async def login(session: CommandSession):
    user_id = str(session.ctx['user_id'])
    user = sess.query(User).filter_by(qq=user_id).first()
    if user:
        username = user.username
        await session.send('用户 ' + username + ' 登录成功.')
    else:
        await session.send('用户查询失败.')

# async def get_user(user_id):
#
#     username = user.username
#     return username
