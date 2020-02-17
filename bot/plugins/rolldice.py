from nonebot import on_command, CommandSession
import random


@on_command('rd', only_to_me=False)
async def rollDice(session: CommandSession):
    state = session.get('state')
    rd_send = await get_rollDice()
    await session.send(state + " " + rd_send)


@rollDice.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
            # 例如用户可能发送了：天气 南京
            session.state['state'] = stripped_arg
        else:
            session.state['state'] = ""
        return

    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    session.state[session.current_key] = stripped_arg


@on_command('rd100', only_to_me=False)
async def rollDice(session: CommandSession):
    state = session.get('state')
    rd_send = await get_rollDice100()
    await session.send(state + " " + rd_send)


@rollDice.args_parser
async def _d100(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
            # 例如用户可能发送了：天气 南京
            session.state['state'] = stripped_arg
        else:
            session.state['state'] = ""
        return

    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    session.state[session.current_key] = stripped_arg


async def get_rollDice():
    result = 'd20 = ' + str(random.randint(1, 20))
    return result


async def get_rollDice100():
    result = 'd100 = ' + str(random.randint(1, 100))
    return result



