import asyncio
import io
import os
import shutil
from datetime import timedelta
from pathlib import Path
import requests

import nonebot
from nonebot import on_command, on_notice
from nonebot.adapters.onebot.v11 import (Message, MessageSegment)
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, GroupMessageEvent, GroupUploadNoticeEvent
from nonebot.params import CommandArg

from .ChatSession import file2embedding, get_ans
from .gpt_reader.pdf_reader import PaperReader, BASE_POINTS

try:
    api_key = nonebot.get_driver().config.openai_api_key
except:
    api_key = ""

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

# start_request = on_command("/start", block=True, priority=1)


# @start_request.handle()
# async def _(event: MessageEvent, msg: Message = CommandArg()):
#     if api_key == "":
#         await start_request.finish(MessageSegment.text("请先配置openai_api_key"), at_sender=True)

#     data[event.get_session_id()] = ""

#     delete_file(os.path.join(result_folder, event.get_session_id()))
#     delete_file(os.path.join(embedding_folder, event.get_session_id()))

#     await start_request.finish(MessageSegment.text("chatpdf开始记录，请发送/add ，后接文本内容添加文档。/stop命令停止"), at_sender=True)


# add_request = on_command("/add", block=True, priority=1)


# @add_request.handle()
# async def _(event: MessageEvent, msg: Message = CommandArg()):
#     if api_key == "":
#         await add_request.finish(MessageSegment.text("请先配置openai_api_key"))

#     content = msg.extract_plain_text() + "\n"
#     if content == "" or content is None:
#         await add_request.finish(MessageSegment.text("内容不能为空！"))

#     if event.get_session_id() not in data:
#         await add_request.finish(MessageSegment.text("请先使用/start命令开始！"))

#     data[event.get_session_id()] += content
#     await add_request.finish(MessageSegment.text("添加成功！"), at_sender=True)


# stop_request = on_command("/stop", block=True, priority=1)


# @stop_request.handle()
# async def _(event: MessageEvent, msg: Message = CommandArg()):
#     if api_key == "":
#         await add_request.finish(MessageSegment.text("请先配置openai_api_key"))

#     stop_request.send(MessageSegment.text("开始分析......"))
#     loop = asyncio.get_event_loop()
#     try:
#         await loop.run_in_executor(None, text2embedding, event.get_session_id(), data[event.get_session_id()])
#     except Exception as error:
#         data[event.get_session_id()] = ""
#         await stop_request.finish(str(error))

#     data[event.get_session_id()] = ""
#     await stop_request.finish(MessageSegment.text("文章分析完成！"), at_sender=True)

pdf_request = on_command("/start", block=True, priority=1)


@pdf_request.handle()
async def _(event: GroupMessageEvent):
    pdf_file_request = on_notice(temp=True, expire_time=timedelta(minutes=1))
    id = event.get_session_id()

    data[id] = ""

    @pdf_file_request.handle()
    async def _(event: GroupUploadNoticeEvent):
        await pdf_request.send(MessageSegment.text("分析中，请稍等......"), at_sender=True)
        response = requests.get(event.file.url)

        with io.BytesIO(response.content) as f:
            session = PaperReader(api_key, points_to_focus=BASE_POINTS)
            data[id] = session
            summary = session.read_pdf_and_summarize(f)

        await pdf_request.finish(MessageSegment.text(summary + "现在，你可以向我提问有关于改文章的问题了"), at_sender=True)

    await pdf_request.finish(MessageSegment.text("请上传需要分析的pdf文件"), at_sender=True)


pdf_chat_request = on_command("/chat_pdf", block=True, priority=1)


@pdf_chat_request.handle()
async def _(bot: Bot, event: GroupMessageEvent, msg: Message = CommandArg()):
    question = msg.extract_plain_text()
    await pdf_request.finish(MessageSegment.text(data[event.get_session_id()].question(question)), at_sender=True)


txt_chat_request = on_command("/chat_txt", block=True, priority=1)


@txt_chat_request.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    question = msg.extract_plain_text()
    loop = asyncio.get_event_loop()

    try:
        ans = await get_ans(event.get_session_id(), question)

    except Exception as error:
        await txt_chat_request.finish(str(error))
    await txt_chat_request.finish(MessageSegment.text(ans), at_sender=True)


delete_request = on_command("/delete_all", block=True, priority=1)


@delete_request.handle()
async def _():
    delete_file(result_folder)
    delete_file(embedding_folder)
    data = {}
    await delete_request.finish(MessageSegment.text("全部删除文件缓存成功！"), at_sender=True)


delete_user_request = on_command("/delete_my", block=True, priority=1)


@delete_user_request.handle()
async def _(event: MessageEvent):
    delete_file(os.path.join(result_folder, event.get_session_id()))
    delete_file(os.path.join(embedding_folder, event.get_session_id()))
    data[event.get_session_id()] = ""
    await delete_user_request.finish(MessageSegment.text("成功删除你在该群的缓存文件！"), at_sender=True)


txt_request = on_command("/txt", block=True, priority=1)


@txt_request.handle()
async def test_(bot: Bot, msg: Message = CommandArg()):
    file_request = on_notice(temp=True, expire_time=timedelta(minutes=1))

    @file_request.handle()
    async def _(event: GroupUploadNoticeEvent):
        # logger.info(event.file.url)
        await file_request.send(MessageSegment.text("分析中，请稍等......"), at_sender=True)
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, file2embedding, event.get_session_id(), event.file.url)
        except Exception as error:
            data[event.get_session_id()] = ""
            await file_request.finish(str(error))

        data[event.get_session_id()] = ""
        await file_request.finish(MessageSegment.text("文章分析完成！"), at_sender=True)

    await txt_request.finish(MessageSegment.text("请上传需要分析的txt文件"), at_sender=True)
