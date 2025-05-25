# 钉钉通过模式助手应用

这是一个使用 Python 开发的钉钉通过模式助手应用示例。通过模式允许您自定义处理用户的查询，并返回定制化的回复。

## 项目结构

```
├── app.py                    # 主应用入口
├── config.py                 # 配置管理模块
├── logger.py                 # 日志配置模块
├── exceptions.py             # 自定义异常类
├── client_manager.py         # 钉钉Stream客户端管理器
├── handlers/                 # 消息处理器模块
│   ├── __init__.py
│   └── universal_message_handler.py  # 通用消息处理器
├── requirements.txt          # 依赖包列表
├── .env                      # 环境变量配置文件
└── README.md                # 项目说明文档
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 创建环境变量配置文件

```bash
touch .env
```

2. 在`.env`文件中填入您的钉钉应用凭证和千问 API 密钥

```
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
LOG_LEVEL=INFO
DASHSCOPE_API_KEY=your_dashscope_api_key_here
```

配置说明：

- `CLIENT_ID`: 钉钉应用的客户端 ID，长度不能小于 5 个字符
- `CLIENT_SECRET`: 钉钉应用的客户端密钥，长度不能小于 5 个字符
- `LOG_LEVEL`: 日志级别，可选值：DEBUG, INFO, WARNING, ERROR, CRITICAL
- `DASHSCOPE_API_KEY`: 千问 API 密钥，用于图片文字识别

## 运行

```bash
python app.py
```

## 功能说明

本应用实现了以下功能：

- **通用消息处理**：处理所有钉钉消息请求
- **图片文字识别**：
  - 自动检测消息中的图片链接
  - 使用千问 API 识别图片中的文字
  - 支持 jpg、jpeg、png、gif 格式的图片
- **详细日志记录**：
  - 同时输出到控制台和文件
  - 日志文件按日期自动分割
  - 记录时间、日志级别、模块名、行号等信息
- **完善的错误处理**：
  - 配置验证
  - 客户端生命周期管理
  - 异常捕获和日志记录

## 代码架构特点

### 1. 配置管理 (config.py)

- 使用 `dataclass` 管理配置
- 支持从环境变量加载配置
- 提供配置验证功能：
  - 必填字段检查
  - 字段长度验证
  - 日志级别验证
  - 环境变量文件检查

### 2. 日志系统 (logger.py)

- 支持同时输出到控制台和文件
- 日志文件按日期自动分割
- 详细的日志格式，包含：
  - 时间戳
  - 日志级别
  - 模块名
  - 行号
  - 消息内容

### 3. 客户端管理 (client_manager.py)

- 完整的客户端生命周期管理
- 类型注解支持
- 异常处理和日志记录
- 处理器注册机制

### 4. 错误处理

- 自定义异常类型
- 分层的异常处理机制
- 详细的错误日志记录

## 开发说明

### 添加新的处理器

1. 在 `handlers/` 目录下创建新的处理器文件
2. 继承 `dingtalk_stream.GraphHandler` 基类
3. 实现 `process` 方法
4. 在 `client_manager.py` 中注册新的处理器

### 日志查看

- 控制台日志：直接查看终端输出
- 文件日志：查看 `logs` 目录下的日志文件，格式为 `app_YYYYMMDD.log`

## 注意事项

1. 确保 `.env` 文件存在且包含必要的配置
2. 确保 `CLIENT_ID` 和 `CLIENT_SECRET` 长度不小于 5 个字符
3. 日志文件会自动创建在 `logs` 目录下
4. 使用图片文字识别功能需要配置千问 API 密钥
