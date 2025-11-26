# fastapi_dashboard_main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os

app = FastAPI(title="Financial Dashboard")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    重定向到前端页面
    """
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="0;url=/static/index.html" />
    </head>
    <body>
        <p>正在跳转到仪表板...</p>
    </body>
    </html>
    """, status_code=200)

# 导入并注册API路由
from fastapi_dashboard_backend import app as api_app
app.mount("/api", api_app)

if __name__ == "__main__":
    uvicorn.run("fastapi_dashboard_main:app", host="0.0.0.0", port=8090, reload=True)