from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from app import app
from exts import db
from models import *


# 初始化管理器
manager = Manager(app)

# 初始化 migrate
# 两个参数一个是 Flask 的 app，一个是数据库 db
migrate = Migrate(app, db)

#
manager.add_command("server", Server())
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()