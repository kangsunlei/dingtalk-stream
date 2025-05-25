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
├── .env.example             # 环境变量配置模板
└── README.md                # 项目说明文档
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 复制环境变量示例文件并修改

```bash
cp .env.example .env
```

2. 在`.env`文件中填入您的钉钉应用凭证

```
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
LOG_LEVEL=INFO
```

## 运行

```bash
python app.py
```

## 功能说明

本应用实现了以下功能：

- **通用消息处理**：处理所有钉钉消息请求
- **智能内容识别**：自动识别天气查询等特定类型的请求
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
