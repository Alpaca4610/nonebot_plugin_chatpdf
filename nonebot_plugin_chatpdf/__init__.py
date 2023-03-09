from pathlib import Path
import shutil
import nonebot
import os
import asyncio

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (Message, MessageSegment)
from nonebot.adapters.onebot.v11 import MessageEvent

from .ChatSession import file2embedding, get_ans

try:
    api_key = nonebot.get_driver().config.openai_api_key
except:
    api_key = ""

try:
    http_proxy = nonebot.get_driver().config.openai_http_proxy
except:
    http_proxy = ""

if http_proxy != "":
    os.environ["http_proxy"] = http_proxy
    os.environ["https_proxy"] = http_proxy

data = {}

embedding_folder = Path() / "data" / "nonebot-plugin-chatpdf" / "embedding"
result_folder = Path() / "data" / "nonebot-plugin-chatpdf" / "result"


def delete_file(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)


delete_file(result_folder)
delete_file(embedding_folder)

Path(result_folder).mkdir(parents=True, exist_ok=True)
Path(embedding_folder).mkdir(parents=True, exist_ok=True)

start_request = on_command("/start", block=True, priority=1)


@start_request.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    if api_key == "":
        await start_request.finish(MessageSegment.text("请先配置openai_api_key"), at_sender=True)

    data[event.get_session_id()] = ""

    delete_file(os.path.join(result_folder, event.get_session_id()))
    delete_file(os.path.join(embedding_folder, event.get_session_id()))

    await start_request.finish(MessageSegment.text("chatpdf开始记录，请发送/add ，后接文本内容添加文档。/stop命令停止"), at_sender=True)


add_request = on_command("/add", block=True, priority=1)


@add_request.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    if api_key == "":
        await add_request.finish(MessageSegment.text("请先配置openai_api_key"))

    content = msg.extract_plain_text() + "\n"
    if content == "" or content is None:
        await add_request.finish(MessageSegment.text("内容不能为空！"))

    if event.get_session_id() not in data:
        await add_request.finish(MessageSegment.text("请先使用/start命令开始！"))

    data[event.get_session_id()] += content
    await add_request.finish(MessageSegment.text("添加成功！"), at_sender=True)


stop_request = on_command("/stop", block=True, priority=1)


@stop_request.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    if api_key == "":
        await add_request.finish(MessageSegment.text("请先配置openai_api_key"))

    stop_request.send(MessageSegment.text("开始分析......"))
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, file2embedding, event.get_session_id(), data[event.get_session_id()])
    except Exception as error:
        data[event.get_session_id()] = ""
        await stop_request.finish(str(error))

    data[event.get_session_id()] = ""
    await stop_request.finish(MessageSegment.text("文章分析完成！"), at_sender=True)


chatpdf_request = on_command("/chat_pdf", block=True, priority=1)


@chatpdf_request.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    question = msg.extract_plain_text()
    # ans = get_ans(event.get_session_id(),question)
    loop = asyncio.get_event_loop()

    try:
        ans = await loop.run_in_executor(None, get_ans, event.get_session_id(), question)
    except Exception as error:
        await stop_request.finish(str(error))
    await stop_request.finish(MessageSegment.text(ans), at_sender=True)


delete_request = on_command("/delete_all", block=True, priority=1)


@delete_request.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    delete_file(result_folder)
    delete_file(embedding_folder)
    await delete_request.finish(MessageSegment.text("全部删除文件缓存成功！"), at_sender=True)


