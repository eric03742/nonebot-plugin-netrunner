import re
import httpx
import asyncio

from nonebot.adapters import Bot, Event
from nonebot.params import T_State
from nonebot.plugin import PluginMetadata
from nonebot.plugin.on import on_regex
from nonebot.rule import to_me

from nonebot.adapters import MessageSegment

__plugin_meta__ = PluginMetadata(
    name="Netrunner 矩阵潜袭卡查",
    description="识别群聊信息中的卡名并展示卡片信息",
    usage="在聊天记录中使用 【】 或 [[]] 引用卡名即可。",
    type="application",
    homepage="https://github.com/eric03742/nonebot-plugin-netrunner",
    extra={},
)

runner = on_regex(r"\[\[(.+?)\]\]", re.IGNORECASE, to_me())
delay = 0.5

@runner.handle()
async def runner_handler(bot: Bot, event: Event, state: T_State):
    words: list[str] = re.compile(r"\[\[(.+?)]]").findall(str(event.get_message()))
    if not words:
        return

    for w in words:
        res = httpx.get(f"https://api-preview.netrunnerdb.com/api/v3/public/cards?filter[search]={w}")
        if res.status_code != httpx.codes.OK:
            await runner.send("与 NetrunnerDB 的通信失败，可能是网络原因，请稍后再试！")
        else:
            raw = res.json()
            info = ''
            try:
                if isinstance(raw, dict):
                    data = raw.get('data')
                    if isinstance(data, list) and len(data) > 0:
                        card = data[0]
                        attribute = card['attributes']
                        info = f"{attribute['title']}: {attribute['text']}"
            except KeyError as err:
                info = 'NetrunnerDB 返回的数据格式出错！'
            finally:
                if len(info) > 0:
                    await runner.send(info)
                else:
                    await runner.send(f'没有找到与 {w} 有关的卡牌！')
                await asyncio.sleep(delay)
