<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-chatpdf

</div>

# 介绍

- 本插件灵感来源于最近很火的[chatpdf](https://www.chatpdf.com)。
- 将需要分析的论文/阅读材料上传到群文件，或者分次发送给机器人，机器人可以对其进行存储分析，然后你可以向其提问有关文章内容、文章概要、对于文章的思考等问题
- 本插件参考和使用了项目[ChatGPT-Paper-Reader](https://github.com/talkingwallace/ChatGPT-Paper-Reader)
  和[How to Code a Project like ChatPDF?](https://postor.medium.com/how-to-code-a-project-like-chatpdf-e40441cb4168)中的代码

# 效果

![Alt](./img/img1.jpg)
![Alt](./img/img2.jpg)

# 安装

* 手动安装
  ```
  git clone https://github.com/Alpaca4610/nonebot_plugin_chatpdf.git
  ```

  下载完成后在bot项目的pyproject.toml文件手动添加插件：

  ```
  plugin_dirs = ["xxxxxx","xxxxxx",......,"下载完成的插件路径/nonebot-plugin-chatpdf"]
  ```
* 使用 pip
  ```
  pip install nonebot-plugin-chatpdf
  ```

# 配置文件

在Bot根目录下的.env文件中追加如下内容：

```
OPENAI_API_KEY = key
```

可选内容：

```
OPENAI_HTTP_PROXY = "http://127.0.0.1:8001"    # 设置代理解决OPENAI的网络问题
OPENAI_API_LIMIT = True     # 降低生成embedding时向OpenAI发送请求的频率，提高embedding生成的成功率。默认开启，改为False关闭。免费版API建议开启。
```

# 使用方法

如果设置了nonebot全局触发前缀，需要在下面的命令前加上设置的前缀。

### 使用方式1：上传需要分析的pdf文件到群文件中

- /start (使用该命令以上传pdf文件的方式启动chatpdf文章分析功能)
- 在一分钟内，上传需要分析的pdf文件到群文件中，分析完成后会返回成功信息
- /chat_pdf (文章分析完成后，使用该命令后面接需要提问的关于文章的问题，机器人会给出答案)
- /delete_all (删除所有缓存文件)
- /delete_my （删除用户在本群的缓存文件）

### 使用方式2：上传需要分析的txt文件到群文件中

- /txt (使用该命令以上传文件的方式启动chatpdf文章分析功能)
- 在一分钟内，上传需要分析的txt文件到群文件中，机器人会对其进行分析并使用OpenAI的API生成embedding文件，分析完成后会返回成功信息
- /chat_txt (文章分析完成后，使用该命令后面接需要提问的关于文章的问题，机器人会给出答案)
- /delete_all (删除所有缓存文件)
- /delete_my （删除用户在本群的缓存文件）

# 注意事项

- 使用txt分析的过程中会在机器人的data文件夹下产生embedding缓存文件，注意缓存占用
- 每次调用/start命令时，都会清除调用者以前的分析缓存
- 插件加载时会删除所有用户的embedding缓存文件
