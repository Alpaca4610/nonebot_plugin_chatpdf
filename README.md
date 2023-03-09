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
- 将需要分析的论文/阅读材料分次发送给机器人，机器人可以对其进行存储分析，然后你可以向其提问有关文章内容、文章概要、对于文章的思考等问题
- 本插件参考了[chatpdf-minimal-demo
：chatpdf 的最小实现，和文章对话 ](https://github.com/postor/chatpdf-minimal-demo) 和[How to Code a Project like ChatPDF?](https://postor.medium.com/how-to-code-a-project-like-chatpdf-e40441cb4168)
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
  pip install nonebot-plugin-chatgpt-turbo
  ```

# 配置文件

在Bot根目录下的.env文件中追加如下内容：

```
OPENAI_API_KEY = key
```

可选内容：
```
OPENAI_HTTP_PROXY = "http://127.0.0.1:8001"    # 设置代理解决OPENAI的网络问题
```


# 使用方法

- /start (使用该命令启动chatpdf文章分析功能)
- /add (启动之后，在该命令后面添加文章的内容，由于QQ的发送字数限制，可能需要将文章分成若干个可以发送的片段，然后依次使用该命令发送)
- /stop (文章添加完成之后，使用该命令告知机器人，机器人开始分析文章并使用OpenAI的API生成embedding文件)
- /chat_pdf (文章分析完成后，使用该命令后面接需要提问的关于文章的问题，机器人会给出答案)
- /delete_all (删除所有缓存文件)

# 注意事项
- 分析过程中会在机器人的data文件夹下产生embedding缓存文件，注意缓存占用
- 每次调用/start命令时，都会清除调用者以前的embedding缓存文件
- 插件加载时会删除所有用户的embedding缓存文件
