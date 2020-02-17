import json
import random, string
import markdown
import re

from flask import session

from exts import db
from models import GamePost, Card_normal

a = string.digits + string.ascii_letters


def get_key(Activation_Code_length=16):
    key = ''
    for i in range(1, Activation_Code_length + 1):
        key += random.choice(a)
        if i % 4 == 0 and i != Activation_Code_length:
            key += '-'
    return key


def post_process(post, current_user_id):
    post = _chose_character(post, current_user_id)
    post = _view_character_list(post, current_user_id)
    post = _r(post)

    post = command_roll_dice(post)
    post = command_strong(post)
    post = command_help(post)
    post = command_red(post)
    post = command_roll_fate(post)
    post = command_markdown(post)
    post = command_emoticon(post)
    post = command_img(post)
    post = command_s(post)
    return post


def command_help(post):
    pattern = '.help'
    matchObj = re.match(pattern, post, re.M | re.I)
    # Match
    if matchObj is not None:
        # with open('doc.html', 'r') as f:
        #     data = f.read()
        data = "<p>使用<kbd>.help</kbd>查询快捷命令使用说明</p>" \
               "<p><kbd>隐藏发言</kbd>只有发言者、接收者和游戏创建者可以看到</p>" \
               "<p>使用<kbd>.strong #content</kbd>命令加粗<kbd>#content</kbd>发言</p>" \
               "<p>使用<kbd>.red #content</kbd>命令改变<kbd>#content</kbd>字体颜色为红色</p>" \
               "<p>使用<kbd>.s #content</kbd>命令使用删除线装饰<kbd>#content</kbd>发言</p>" \
               "<p>使用<kbd>.markdown #content</kbd>命令使用Markdown修饰<kbd>#content</kbd>发言</p>" \
               "<HR>" \
               "<p>使用<kbd>.rd</kbd>或者<kbd>.r4d6</kbd>进行快捷投骰</p>" \
               "<p>使用<kbd>.fateDice #num</kbd>投num个命运骰</p>" \
               "<p>使用<kbd>.list</kbd>查看当前用户所有的角色列表，使用<kbd>.login #角色名</kbd>登陆目标角色信息</p>" \
               "<p>使用<kbd>.r #属性名</kbd>对预设置的属性进行快捷检定</p>" \
               "<HR>" \
               "<p>使用<kbd>.emo smile</kbd>使用麻将脸表情</p>"
        return data
    return post


def command_markdown(post):
    pattern = '.markdown'
    matchObj = re.match(pattern, post, re.M | re.I)
    # Match
    if matchObj is not None:
        content = post[10:]
        content = markdown.markdown(content)
        return content
    # Not Match
    return post


def command_emoticon(post):
    pattern = '.emo'
    matchObj = re.match(pattern, post, re.M | re.I)
    # Match
    if matchObj is not None:
        icon_id = post.split(' ')[1]
        if icon_id == 'smile':
            content = '<a href="https://sm.ms/image/MKAW4svJZ8kt7Pi" target="_blank"><img src="https://i.loli.net/2020/01/30/MKAW4svJZ8kt7Pi.gif" ></a>'
        elif icon_id == 'cry':
            content = '<a href="https://sm.ms/image/sUzuK1H2dDcepoP" target="_blank"><img src="https://i.loli.net/2020/01/30/sUzuK1H2dDcepoP.gif" ></a>'
        elif icon_id == 'bear':
            content = '<a href="https://sm.ms/image/6apOHQUw83G4E27" target="_blank"><img src="https://i.loli.net/2020/01/30/6apOHQUw83G4E27.gif" ></a>'
        elif icon_id == 'angry':
            content = '<a href="https://sm.ms/image/uUegDiHNMpn6Qzx" target="_blank"><img src="https://i.loli.net/2020/01/30/uUegDiHNMpn6Qzx.gif" ></a>'
        elif icon_id == 'tongue':
            content = '<a href="https://sm.ms/image/sGvRyIt7N9JfpQn" target="_blank"><img src="https://i.loli.net/2020/01/30/sGvRyIt7N9JfpQn.gif" ></a>'
        elif icon_id == 'awsl':
            content = '<a href="https://sm.ms/image/IRzUZo91OWJfany" target="_blank"><img src="https://i.loli.net/2020/01/30/IRzUZo91OWJfany.gif" ></a>'
        elif icon_id == 'shy':
            content = '<a href="https://sm.ms/image/hG1JbH7y58XSr3W" target="_blank"><img src="https://i.loli.net/2020/01/30/hG1JbH7y58XSr3W.gif" ></a>'
        return content
        # Not Match
    return post


def command_img(post):
    pattern = '.img'
    matchObj = re.match(pattern, post, re.M | re.I)
    # Match
    if matchObj is not None:
        content = post[5:]
        content = '<img src = "' + content +'" height = "200" width = "200" />'
        return content
    # Not Match
    return post


def command_red(post):
    pattern = '.red'
    matchObj = re.match(pattern, post, re.M | re.I)
    # Match
    if matchObj is not None:
        content = post.split(' ')[1:]
        content = decorator_red(' '.join(content))
        return content
    # Not Match
    return post


def command_s(post):
    pattern = '.s '
    matchObj = re.match(pattern, post, re.M | re.I)
    # Match
    if matchObj is not None:
        content = post[3:]
        content = decorator_s(' '.join(content))
        return content
    # Not Match
    return post


def command_strong(post):
    pattern = '.strong'
    matchObj = re.match(pattern, post, re.M | re.I)
    # Match
    if matchObj is not None:
        content = post.split(' ')[1:]
        content = decorator_strong(' '.join(content))
        return content
    # Not Match
    return post


def command_roll_fate(post):
    pattern = '.fateDice'
    matchObj = re.match(pattern, post, re.M | re.I)
    # Match
    if matchObj is not None:
        result = 0
        dice_list = []
        num = post.split(' ')[1]
        for i in range(int(num)):
            dice = random.randint(-1, 1)
            dice_list.append(dice)
            result += dice
        dice_list = ', '.join(str(i) for i in dice_list)
        info = decorator_kbd(post) + ' = ' + dice_list + ' = ' + decorator_strong(str(result))
        return info
    return post


def command_roll_dice(post):
    # Roll Dice
    pattern = '.r\d*d\d*'
    matchObj = re.match(pattern, post, re.M | re.I)
    # Match
    if matchObj is not None:
        # 分割post语句
        seg = post.split(' ')
        com = seg[0][2:]
        # 提取符合正则表达的部分
        cal = matchObj.group(0)[2:]
        # 有content后缀
        if len(seg) > 1:
            content = seg[1:]
        else:
            content = ''

        # 处理默认骰子缩写
        if cal[0] == 'd':
            cal = '1' + cal
        if cal[-1] == 'd':
            cal = cal + '100'

        num = int(cal.split('d')[0])
        dice = int(cal.split('d')[1])

        result, _ = roll_dice(num=num, dice=dice)
        dice_list = '[' + ', '.join(str(i) for i in _) + ']'

        if com[:2] == 'd':
            com = '1d100' + com[3:]
        # 处理bonus
        bonus = ''
        oper = ''
        # 判断是否存在bonus
        if len(cal) == len(com):
            pass
        elif len(cal) > len(com):
            return "Command Error, Please Use .help to check Fast Commands."
        else:
            bonus = com[len(cal):]
            oper = bonus[0]
            bonus = bonus[1:]
        if len(bonus) is not 0 and len(oper) is not 0:
            if oper is '+':
                result += int(bonus)
            elif oper is '-':
                result -= int(bonus)
            elif oper is '*':
                result *= int(bonus)
            elif oper is '/':
                result /= int(bonus)
            else:
                return "Command Error, Please Use .help to check Fast Commands."
        return decorator_kbd(com) + ' = ' + decorator_strong(dice_list) + oper + bonus + ' = ' + str(
            result) + " " + decorator_strong(decorator_brown(str(content)))
        # Not Match
    return post


def decorator_kbd(post):
    return '<kbd>' + post + '</kbd>'


def decorator_strong(post):
    return '<strong>' + post + '</strong>'


def decorator_red(post):
    return "<font color='red'>" + post + '</font>'


def decorator_brown(post):
    return "<font color='#B22222'>" + post + '</font>'


def decorator_s(post):
    return "<s>" + post + '</s>'


def roll_dice(num=1, dice=100, bonus=0):
    result = 0
    dice_list = []
    for i in range(num):
        dice = random.randint(1, dice)
        result += dice
        dice_list.append(dice)
    result += bonus
    return result, dice_list


def delete_game(game):
    db.session.delete(game)
    gp = GamePost.query.filter(GamePost.game_id == game.game_id).all()
    for item in gp:
        db.session.delete(item)
    db.session.commit()


# Jinja2 global function
def jinja2_roll_dice(post):
    # Roll Dice
    pattern = '.r\d*d\d*'
    matchObj = re.match(pattern, post, re.M | re.I)
    # Match
    if matchObj is not None:
        # 分割post语句
        seg = post.split(' ')
        com = seg[0][2:]
        # 提取符合正则表达的部分
        cal = matchObj.group(0)[2:]
        # 有content后缀
        if len(seg) > 1:
            content = seg[1:]
        else:
            content = ''

        # 处理默认骰子缩写
        if cal[0] == 'd':
            cal = '1' + cal
        if cal[-1] == 'd':
            cal = cal + '100'

        num = int(cal.split('d')[0])
        dice = int(cal.split('d')[1])

        result, _ = roll_dice(num=num, dice=dice)
        dice_list = '[' + ', '.join(str(i) for i in _) + ']'

        if com[:2] == 'd':
            com = '1d100' + com[3:]
        # 处理bonus
        bonus = ''
        oper = ''
        # 判断是否存在bonus
        if len(cal) == len(com):
            pass
        elif len(cal) > len(com):
            return "Command Error, Please Use .help to check Fast Commands."
        else:
            bonus = com[len(cal):]
            oper = bonus[0]
            bonus = bonus[1:]
        if len(bonus) is not 0 and len(oper) is not 0:
            if oper is '+':
                result += int(bonus)
            elif oper is '-':
                result -= int(bonus)
            elif oper is '*':
                result *= int(bonus)
            elif oper is '/':
                result /= int(bonus)
            else:
                return "Command Error, Please Use .help to check Fast Commands."
        info = com + '=' + str(result)
        return info
        # Not Match
    return post


# Show Character_list
def _view_character_list(post, current_user_id):
    pattern = '.list'
    matchObj = re.match(pattern, post, re.M | re.I)
    # Match
    if matchObj is not None:
        cards = Card_normal.query.filter(Card_normal.user_id == int(current_user_id)).all()
        list = []
        for item in cards:
            list.append(item.name)
        if list:
            return str(list)
        else:
            return '角色列表查询失败'
    # Not Match
    return post


def _chose_character(post, current_user_id):
    pattern = '.login'
    matchObj = re.match(pattern, post, re.M | re.I)
    # Match
    if matchObj is not None:
        name = post.split(' ')[1]
        card = Card_normal.query.filter(Card_normal.user_id == int(current_user_id), Card_normal.name == name).first()
        if card:
            data = json.loads(card.data)
            for key in data:
                session[key] = data.get(key)
                print(key)
                print(data.get(key))
            session['name'] = card.name
            session['card_data'] = card.data
            return '角色 ' + decorator_strong(card.name) + ' (' + card.features + ') ' + '登陆成功'
        else:
            return '角色查询失败'
    # Not Match
    return post


def _r(post):
    pattern = '.r '
    matchObj = re.match(pattern, post, re.M | re.I)
    # Match
    if matchObj is not None:
        com = post[3:]
        print(com)
        if session.get(com):
            post = session.get(com)
            print(post)
            return command_roll_dice(post)
    return post


def func(key, card):
    js = json.loads(card.data)
    return command_roll_dice(js.get(key))
