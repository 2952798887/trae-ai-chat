# 工作流编排对话型应用 API 客户端

## 项目简介

本项目是一个基于工作流编排对话型应用 API 的客户端实现，提供了多种交互方式和工具，方便与AI进行对话交流。

## 文件结构

### 1. `api_client.py`

**功能**：交互式对话客户端

- 实现了与API的基本交互功能
- 支持流式响应和阻塞响应模式
- 提供命令行交互式对话界面
- 支持多轮对话和上下文保持

**使用方法**：
```bash
python api_client.py
```

### 2. `ai_chat.py`

**功能**：AI直接交流工具

- 基于`api_client.py`的增强版
- 自动提取AI回复的实际内容（去除`<think>`标签）
- 支持重复上一次AI的回复
- 提供`get_last_ai_response()`方法获取最后一次AI回复

**使用方法**：
```bash
python ai_chat.py
```

### 3. `ai_response_extractor.py`

**功能**：AI回复提取工具

- 提供`extract_ai_response()`函数
- 专门用于提取AI回复的实际内容，去除`<think>`标签
- 可被其他Python文件导入使用

**使用方法**：
```python
from ai_response_extractor import extract_ai_response

ai_reply = "<think>思考过程</think>实际回复"
actual_response = extract_ai_response(ai_reply)
```

### 4. `chat_window.py`

**功能**：Windows聊天窗口界面（支持AI轮训、管理员发送消息和对话持久化功能）

- 使用tkinter创建GUI界面
- 左侧为对话框区域，右侧为AI用户列表
- 支持点击添加AI用户，自动生成唯一用户ID
- 实现AI用户的无限轮训功能，将上一个AI的回复作为输入传递给下一个AI
- **新增并发轮询功能**：所有AI用户同时进行对话，提高效率
- 提供轮训控制按钮（开始、开始并发、暂停、停止）
- 支持管理员发送消息功能，以"admin"身份在对话中插入消息
- **新增字体大小调整**：可通过按钮放大或缩小字体，适应不同屏幕
- **新增滚动条支持**：聊天内容超过窗口时自动显示滚动条
- **新增消息样式**：发送者名字以蓝色粗体显示，提高可读性
- 实现对话持久化功能，自动将聊天记录保存到文本文件
- 每次停止轮训后再开始时会新建一个聊天文件
- 保持对话上下文的连贯性
- 响应式布局，支持窗口大小调整

**使用方法**：
```bash
python chat_window.py
```

**轮训功能使用步骤**：
1. 点击"添加用户"按钮添加至少2个AI用户
2. 选择轮训模式：
   - 点击"开始轮训"按钮开始AI之间的顺序对话（一个接一个）
   - 点击"开始轮询（并发）"按钮开始AI之间的并发对话（所有AI同时）
3. 观察聊天窗口中AI之间的对话过程
4. 可随时点击"暂停轮训"或"停止轮训"按钮控制轮训过程

**管理员发送消息**：
1. 在输入框中输入消息
2. 点击"发送"按钮
3. 消息将以"admin"身份显示在聊天窗口中
4. 在下一次轮训时，该消息会被包含在对话历史中传递给AI
5. **并发轮询中的admin发言处理**：
   - 如果当前轮有admin发言，会被包含在所有AI的上下文中
   - 如果当前轮没有admin发言，AI只会收到其他AI的发言，不会收到admin的历史发言

**对话持久化**：
- 聊天记录会自动保存到当前目录下的文本文件中
- 文件名格式为"chat_YYYYMMDD_HHMMSS.txt"
- 每次停止轮训后再开始时会新建一个聊天文件
- 暂停轮训后继续使用同一个文件
- **保存机制**：使用追加模式保存，确保所有历史消息都被完整保存，不会丢失旧消息
- **消息顺序**：消息按时间顺序保存，保持对话的连贯性

**打包为可执行文件**：
1. 安装PyInstaller：
   ```bash
   pip install pyinstaller
   ```
2. 打包为可执行文件：
   ```bash
   pyinstaller --onefile --windowed chat_window.py
   ```
3. 可执行文件会生成在`dist`目录中

### 5. `requirements.txt`

**功能**：依赖包管理

- 列出项目所需的Python包
- 用于安装项目依赖

**使用方法**：
```bash
pip install -r requirements.txt
```

## API配置

所有客户端文件都需要配置API密钥才能正常工作。默认API密钥设置在每个文件的主函数部分：

```python
API_KEY = "app-U9MYpOHqM2BU9JC3NSfJUH0j"
USER_ID = "test_user_123"
```

## 依赖项

- `requests` - 用于发送HTTP请求
- `sseclient-py` - 用于处理服务器发送事件（SSE）
- `tkinter` - 用于创建GUI界面（Python标准库）
- `uuid` - 用于生成唯一ID（Python标准库）

## 使用流程

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **配置API密钥**：
   - 在各文件中更新`API_KEY`变量为你的实际API密钥

3. **选择交互方式**：
   - 命令行交互：`python api_client.py`
   - AI直接交流：`python ai_chat.py`
   - GUI界面：`python chat_window.py`

4. **开始对话**：
   - 输入你的问题，按回车键发送
   - 输入`exit`退出对话
   - 在`ai_chat.py`中，输入`last`重复上一次AI的回复

## 注意事项

- API密钥应妥善保管，避免泄露
- 用户名（USER_ID）应保持唯一，用于标识不同用户
- 流式响应模式需要安装`sseclient-py`包
- GUI界面需要Python的tkinter库支持

## 扩展功能

- 消息反馈（点赞/点踩）
- 停止响应
- 语音转文字
- 文字转语音
- 获取应用配置信息
- 获取应用Meta信息

如果需要扩展这些功能，可以参考API文档进行实现。
