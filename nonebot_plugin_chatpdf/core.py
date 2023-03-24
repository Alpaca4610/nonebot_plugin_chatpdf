import io
import nonebot
# import os
# from pathlib import Path

import openai
import faiss
import numpy as np
# import pickle

import requests
import fitz

from tqdm import tqdm
from .config import Config

plugin_config = Config.parse_obj(nonebot.get_driver().config.dict())

if not plugin_config.openai_api_key:
    openai.api_key = ""
else:
    openai.api_key = plugin_config.openai_api_key

if plugin_config.openai_http_proxy:
    openai.proxy = {'http': plugin_config.openai_http_proxy, 'https': plugin_config.openai_http_proxy}


def read_pdf(url):
    response = requests.get(url)
    stream = io.BytesIO(response.content)

    # 用pymupdf来读取pdf文件
    with fitz.open(stream=stream) as pdf:
        content = ""
        for page in pdf:
            # 获取每一页的内容
            texts = page.get_text()
            # 将内容添加到总体文本中
            content += texts

    return content


def create_embeddings(input):
    """Create embeddings for the provided input."""
    result = []
    # limit about 1000 tokens per request
    lens = [len(text) for text in input]
    query_len = 0
    start_index = 0
    tokens = 0

    def get_embedding(input_slice):
        embedding = openai.Embedding.create(model="text-embedding-ada-002", input=input_slice)
        return [(text, data.embedding) for text, data in zip(input_slice, embedding.data)], embedding.usage.total_tokens

    for index, l in tqdm(enumerate(lens)):
        query_len += l
        if query_len > 4096:
            ebd, tk = get_embedding(input[start_index:index + 1])
            query_len = 0
            start_index = index + 1
            tokens += tk
            result.extend(ebd)

    if query_len > 0:
        ebd, tk = get_embedding(input[start_index:])
        tokens += tk
        result.extend(ebd)
    return result, tokens


def create_embedding(text):
    """Create an embedding for the provided text."""
    embedding = openai.Embedding.create(model="text-embedding-ada-002", input=text)
    return text, embedding.data[0].embedding


class QA:
    def __init__(self, event_id, url) -> None:

        texts = read_pdf(url)
        str_buf = io.StringIO(texts)
        texts = str_buf.readlines()
        texts = [text.strip() for text in texts if text.strip()]

        data_embe, tokens = create_embeddings(texts)

        # 存储文件
        # pickle.dump(data_embe, open(tmpfile, 'wb'))

        print("文本消耗 {} tokens".format(tokens))

        d = 1536
        index = faiss.IndexFlatL2(d)
        embe = np.array([emm[1] for emm in data_embe])
        data = [emm[0] for emm in data_embe]
        index.add(embe)
        self.index = index
        self.data = data

    def generate_ans(self, query):
        embedding = create_embedding(query)
        context = self.get_texts(embedding[1], limit=10)
        answer = self.completion(query, context)
        return answer, context

    def get_texts(self, embeding, limit):
        _, text_index = self.index.search(np.array([embeding]), limit)
        context = []
        for i in list(text_index[0]):
            context.extend(self.data[i:i + 5])
        # context = [self.data[i] for i in list(text_index[0])]
        return context

    def completion(self, query, context):
        """Create a completion."""
        lens = [len(text) for text in context]

        maximum = 3000
        for index, l in enumerate(lens):
            maximum -= l
            if maximum < 0:
                context = context[:index + 1]
                print("超过最大长度，截断到前", index + 1, "个片段")
                break

        text = "\n".join(f"{index}. {text}" for index, text in enumerate(context))
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {'role': 'system',
                 'content': f'你是一个有帮助的AI文章助手，从下文中提取有用的内容进行回答，不能回答不在下文提到的内容，相关性从高到底排序：\n\n{text}'},
                {'role': 'user', 'content': query},
            ],
        )
        print("使用的tokens：", response.usage.total_tokens)
        return response.choices[0].message.content

    def get_ans(self, query):
        answer, context = self.generate_ans(query)
        print("回答如下\n\n")
        print(answer.strip())

        return answer

