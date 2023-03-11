import hashlib
import json
import os.path
import time
import urllib
from pathlib import Path

import nonebot
import numpy as np
import openai

try:
    api_key = nonebot.get_driver().config.openai_api_key
except:
    api_key = ""

try:
    http_proxy = nonebot.get_driver().config.openai_http_proxy
except:
    http_proxy = ""

try:
    time_limit = nonebot.get_driver().config.openai_api_limit
except:
    time_limit = "True"


if http_proxy != "":
    openai.proxy = {'http': http_proxy, 'https': http_proxy}

openai.api_key = api_key

COMPLETIONS_MODEL = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-ada-002"
CONTEXT_TOKEN_LIMIT = 3500


def get_embedding(text: str, event_id: str, model: str = EMBEDDING_MODEL):
    folder = Path() / "data" / "nonebot-plugin-chatpdf" / "embedding" / event_id
    Path(folder).mkdir(parents=True, exist_ok=True)
    tmpfile = os.path.join(folder, hashlib.md5(text.encode('utf-8')).hexdigest() + ".json")
    if os.path.isfile(tmpfile):
        with open(tmpfile, 'r', encoding='UTF-8') as f:
            return json.load(f)
    
    if time_limit == "True" :
        time.sleep(0.1)
    
    result = openai.Embedding.create(
        model=model,
        input=text
    )

    with open(tmpfile, 'w', encoding='utf-8') as handle2:
        json.dump(result["data"][0]["embedding"], handle2, ensure_ascii=False, indent=4)

    return result["data"][0]["embedding"]


def file2embedding(event_id: str, url):
    embeddings = []
    sources = []

    folder = Path() / "data" / "nonebot-plugin-chatpdf" / "result" / event_id
    Path(folder).mkdir(parents=True, exist_ok=True)

    with urllib.request.urlopen(url) as response:
        content = response.read().decode()
        # print(content)
    for source in content.split('\n'):
        if source.strip() == '':
            continue
        embeddings.append(get_embedding(source, event_id))
        sources.append(source)

    tmppath = os.path.join(folder, 'result.json')

    with open(tmppath, 'w', encoding='utf-8') as handle2:
        json.dump({"sources": sources, "embeddings": embeddings}, handle2, ensure_ascii=False, indent=4)


def text2embedding(event_id: str, contents=""):
    embeddings = []
    sources = []
    content = contents

    folder = Path() / "data" / "nonebot-plugin-chatpdf" / "result" / event_id
    Path(folder).mkdir(parents=True, exist_ok=True)
    for source in content.split('\n'):
        if source.strip() == '':
            continue
        embeddings.append(get_embedding(source, event_id))
        sources.append(source)

    tmppath = os.path.join(folder, 'result.json')

    with open(tmppath, 'w', encoding='utf-8') as handle2:
        json.dump({"sources": sources, "embeddings": embeddings}, handle2, ensure_ascii=False, indent=4)


def vector_similarity(x, y):
    """
    Returns the similarity between two vectors.
    
    Because OpenAI Embeddings are normalized to length 1, the cosine similarity is the same as the dot product.
    """
    return np.dot(np.array(x), np.array(y))


def order_document_sections_by_query_similarity(query: str, embeddings, event_id):
    """
    Find the query embedding for the supplied query, and compare it against all of the pre-calculated document embeddings
    to find the most relevant sections. 
    
    Return the list of document sections, sorted by relevance in descending order.
    """
    query_embedding = get_embedding(query, event_id)

    document_similarities = sorted([
        (vector_similarity(query_embedding, doc_embedding), doc_index) for doc_index, doc_embedding in
        enumerate(embeddings)
    ], reverse=True, key=lambda x: x[0])

    return document_similarities


async def ask(question: str, embeddings, sources, event_id):
    ordered_candidates = order_document_sections_by_query_similarity(question, embeddings, event_id)
    ctx = ""
    for candi in ordered_candidates:
        next = ctx + " " + sources[candi[1]]
        if len(next) > CONTEXT_TOKEN_LIMIT:
            break
        ctx = next
    if len(ctx) == 0:
        return ""

    prompt = "".join([
        u"基于上下文回答以下问题\n\n"
        u"上下文：" + ctx + u"\n\n"
                        u"问题：" + question + u"\n\n"
                                            u"答案："
    ])

    completion = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo",
                                                     messages=[{"role": "user", "content": prompt}])
    return [prompt, completion.choices[0].message.content]


async def get_ans(event_id: str, question: str):
    folder = Path() / "data" / "nonebot-plugin-chatpdf" / "result" / event_id

    tmppath = os.path.join(folder, 'result.json')
    if os.path.isfile(tmppath):
        with open(tmppath, 'r', encoding='UTF-8') as f:
            obj = json.load(f)
            [prompt, answer] = await ask(question, obj["embeddings"], obj["sources"], event_id)

        return answer

    return "还未生成embeding！"
