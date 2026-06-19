import os
import yaml
import asyncio
import json
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Pixelle-Video Pro Web")

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.yaml"
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


# 初始化默认配置
def init_config():
    if not CONFIG_FILE.exists():
        default_cfg = {
            "API_PROVIDER": "openai_compatible",
            "API_CONFIGS": {
                "openai_compatible": {
                    "api_base": "https://api.your-provider.com/v1",
                    "api_key": "sk-your-api-key-here",
                    "model": "video-enhance-pro-v2",
                    "timeout": 300
                },
                "local": {
                    "api_base": "http://127.0.0.1:7860/api/v1/video",
                    "api_key": "local-no-key",
                    "model": "local-enhance-model",
                    "timeout": 600
                }
            },
            "FEATURE_FLAGS": {
                "enable_8k_upscale": True,
                "enable_frame_interp": True,
                "enable_color_fix": True
            }
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(default_cfg, f, allow_unicode=True)


def read_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


init_config()


@app.get("/", response_class=HTMLResponse)
async def get_home():
    with open(BASE_DIR / "templates" / "index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/config")
async def get_config():
    return read_config()


class ConfigUpdate(BaseModel):
    api_provider: str
    api_base: str
    api_key: str
    model: str


@app.post("/api/config")
async def update_config(cfg: ConfigUpdate):
    config = read_config()
    config["API_PROVIDER"] = cfg.api_provider
    if cfg.api_provider not in config["API_CONFIGS"]:
        config["API_CONFIGS"][cfg.api_provider] = {}
    config["API_CONFIGS"][cfg.api_provider].update({
        "api_base": cfg.api_base,
        "api_key": cfg.api_key,
        "model": cfg.model
    })
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True)
    return {"status": "success", "message": "配置已更新"}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="未检测到文件")
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return {"filename": file.filename, "filepath": str(file_path)}


@app.websocket("/ws/process")
async def ws_process(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        req = json.loads(data)
        filename = req.get("filename")
        features = req.get("features", {})
        input_path = UPLOAD_DIR / filename
        output_path = OUTPUT_DIR / f"pro_{filename}"
        if not input_path.exists():
            await websocket.send_json({"status": "error", "message": "文件不存在"})
            return
        # 模拟视频处理流程与进度推送
        steps = [
            ("初始化环境与 API 接口", 10),
            ("提取视频帧序列", 20),
        ]
        if features.get("enable_8k_upscale"):
            steps.append(("执行 8K 无损放大", 40))
        if features.get("enable_frame_interp"):
            steps.append(("执行 AI 智能补帧 (60FPS)", 60))
        if features.get("enable_color_fix"):
            steps.append(("执行色彩与曝光校正", 80))
        steps.append(("封装视频与音频流", 95))
        steps.append(("处理完成", 100))
        for step_name, progress in steps:
            await websocket.send_json({"status": "processing", "step": step_name, "progress": progress})
            await asyncio.sleep(1.5)  # 模拟处理耗时
        # 模拟生成输出文件
        with open(output_path, "wb") as f:
            f.write(b"dummy_video_data")
        await websocket.send_json({
            "status": "completed",
            "progress": 100,
            "download_url": f"/api/download/pro_{filename}"
        })
    except WebSocketDisconnect:
        print("客户端断开连接")
    except Exception as e:
        await websocket.send_json({"status": "error", "message": str(e)})


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件未找到")
    return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
