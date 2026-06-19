# Pixelle-Video Pro 网页版

纯网页版、免安装、跨设备的 AI 视频增强处理应用。采用前后端分离架构，通过 WebSocket 实现实时进度追踪，支持界面亮/暗色模式切换，并可通过网页端动态配置 API 接口。

## 功能特性

- **8K 无损放大**：将低分辨率视频超分至 8K
- **AI 智能补帧**：提升视频帧率至 60FPS
- **色彩与曝光校正**：自动优化画面色彩与曝光
- **拖拽上传**：支持点击或拖拽视频文件上传
- **实时进度**：WebSocket 实时推送处理进度
- **暗色模式**：一键切换亮色/暗色主题
- **动态 API 配置**：网页端直接配置 API 提供商和密钥

## 目录结构

```
pixelle_web/
├── app.py             # FastAPI 后端服务
├── config.yaml        # 动态 API 配置文件
├── requirements.txt   # Python 依赖
├── .gitignore
├── README.md
└── templates/
    └── index.html     # 前端网页版界面
```

## 快速开始

### 环境要求

- Python 3.10+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
python app.py
```

### 访问应用

打开浏览器访问 **http://127.0.0.1:8000** 即可使用完整功能。

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 前端页面 |
| `/api/config` | GET | 获取当前配置 |
| `/api/config` | POST | 更新 API 配置 |
| `/api/upload` | POST | 上传视频文件 |
| `/ws/process` | WebSocket | 视频处理（实时进度） |
| `/api/download/{filename}` | GET | 下载处理后的视频 |

## 技术栈

- **后端**：FastAPI + Uvicorn + WebSocket + PyYAML
- **前端**：Tailwind CSS + 原生 JavaScript
- **配置**：YAML 动态配置文件

## License

MIT
