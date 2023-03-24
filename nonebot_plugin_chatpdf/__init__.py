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


from .core import QA

try:
    api_key = nonebot.get_driver().config.openai_api_key
except:
    api_key = ""

data = {}


# embedding_folder = Path() / "data" / "nonebot-plugin-chatpdf" / "embeddings"


def delete_file(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)


# delete_file(result_folder)
# delete_file(embedding_folder)
#
# Path(result_folder).mkdir(parents=True, exist_ok=True)
# Path(embedding_folder).mkdir(parents=True, exist_ok=True)


pdf_request = on_command("/start", block=True, priority=1)


@pdf_request.handle()
async def _(event: GroupMessageEvent):
    pdf_file_request = on_notice(temp=True, expire_time=timedelta(minutes=1))
    id = event.get_session_id()

    data[id] = ""

    @pdf_file_request.handle()
    async def _(event: GroupUploadNoticeEvent):
        await pdf_request.send(MessageSegment.text("分析中，请稍等......"), at_sender=True)

        data[id] = QA(id, event.file.url)

        await pdf_request.finish(MessageSegment.text("现在，你可以向我提问有关于该文章的问题了"), at_sender=True)

    await pdf_request.finish(MessageSegment.text("请上传需要分析的pdf文件"), at_sender=True)


pdf_chat_request = on_command("/chat_pdf", block=True, priority=1)


@pdf_chat_request.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if event.get_session_id() not in data:
        await pdf_chat_request.finish(MessageSegment.text("请先使用/start命令开始！"))
    question = msg.extract_plain_text()
    await pdf_request.finish(MessageSegment.text(data[event.get_session_id()].get_ans(question)), at_sender=True)


delete_request = on_command("/delete_all", block=True, priority=1)


@delete_request.handle()
async def _():
    # delete_file(result_folder)
    # delete_file(embedding_folder)
    data = {}
    await delete_request.finish(MessageSegment.text("全部删除文件缓存成功！"), at_sender=True)


delete_user_request = on_command("/delete_my", block=True, priority=1)


@delete_user_request.handle()
async def _(event: MessageEvent):
    # delete_file(os.path.join(result_folder, event.get_session_id()))
    # delete_file(os.path.join(embedding_folder, event.get_session_id()))
    data[event.get_session_id()] = ""
    await delete_user_request.finish(MessageSegment.text("成功删除你在该群的缓存文件！"), at_sender=True)
