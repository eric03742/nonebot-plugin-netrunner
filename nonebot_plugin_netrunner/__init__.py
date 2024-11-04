import nonebot
import os
import re

from meilisearch import Client
from meilisearch.index import Index
from nonebot import logger
from nonebot.plugin import PluginMetadata
from nonebot.plugin.on import on_regex, on_command
from nonebot.rule import to_me, is_type
from nonebot.adapters.onebot.v11 import Event, Message, MessageSegment, PRIVATE_FRIEND, GROUP, GroupMessageEvent

from .config import Config

# 插件的元数据

__plugin_meta__ = PluginMetadata(
    name="Netrunner 矩阵潜袭卡查",
    description="识别群聊消息中的《矩阵潜袭》卡名并展示卡片信息",
    usage="在聊天记录中使用 【】 或 [[]] 引用卡名即可。",
    type="application",
    homepage="https://github.com/eric03742/nonebot-plugin-netrunner",
    supported_adapters={"~onebot.v11"},
    extra={},
)

# 配置

driver = nonebot.get_driver()
conf = nonebot.get_plugin_config(Config)
index: Index

@driver.on_startup
async def connect_database():
    global index
    host = conf.netrunner_database_host
    port = conf.netrunner_database_port
    token = conf.netrunner_database_master_key
    client = Client(f'http://{host}:{port}', token)
    logger.info(f'connect to meilisearch: {client.is_healthy()}')
    index = client.get_index('netrunner')


# 管理员命令，用于检查服务可用性

ping = on_command("ping", rule=to_me(), permission=PRIVATE_FRIEND, priority=10)

@ping.handle()
async def ping_handler(event: Event):
    user = event.get_user_id()
    if not user in driver.config.superusers:
        return

    await ping.send(message="pong")

# 群聊卡查消息命令

runner = on_regex(r"【(.+?)】", re.IGNORECASE, rule=is_type(GroupMessageEvent), permission=GROUP, priority=10)

@runner.handle()
async def runner_handler(event: Event):
    words: list[str] = re.compile(r"【(.+?)】").findall(event.get_message().extract_plain_text())
    if not words:
        return

    for w in words:
        callback = index.search(w, {
            'sort': ['code:desc']
        })

        if not callback:
            await runner.send('数据库异常！')
            continue

        result = callback['hits']

        if not result or len(result) <= 0:
            await runner.send(f'没有找到与 {w} 有关的卡牌！')
            continue

        card = result[0]
        card_code = card['code']
        card_link = f'https://netrunnerdb.com/en/card/{card_code}'
        card_name = card['cn_title']
        if len(card_name) <= 0:
            card_name = card['title']
        card_word = card['cn_keywords']
        if len(card_word) <= 0:
            card_word = card['keywords']
        card_text = card['cn_text']
        if len(card_text) <= 0:
            card_text = card['text']

        info = f'{card_link}\n「{card_name}」：{card_word}\n{card_text}'
        address = os.path.join(conf.netrunner_resources_dir, f'{card_code}.png')
        img = f'file://{address}'
        msg = Message.template("{}\n{}").format(
            MessageSegment.text(info),
            MessageSegment.image(img)
        )
        await runner.send(msg)
