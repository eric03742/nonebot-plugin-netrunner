from nonebot.rule import to_me
from nonebot.plugin import on_command, PluginMetadata
from nonebot.adapters import Message
from nonebot.params import CommandArg


__plugin_meta__ = PluginMetadata(
    name="Netrunner 矩阵潜袭卡查",
    description="识别群聊信息中的卡名并展示卡片信息",
    usage="在聊天记录中使用 【】 或 [[]] 引用卡名即可。",
    type="application",
    homepage="https://github.com/eric03742/nonebot-plugin-netrunner",
    extra={},
)


weather = on_command("天气", rule=to_me())

@weather.handle()
async def weather_handler(arg: Message = CommandArg()):
    location = arg.extract_plain_text()
    if location:
        await weather.finish(f"今天 {location} 的天气是...")
    else:
        await weather.finish("请输入地名")
