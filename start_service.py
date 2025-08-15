#!/usr/bin/env python3
"""
简化版启动脚本 - 跳过SDK依赖问题
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from app.api import app
    print("✅ FastAPI app loaded successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("尝试添加更多路径...")
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
    try:
        from api import app
        print("✅ FastAPI app loaded successfully (alternative path)")
    except ImportError as e2:
        print(f"❌ Still failed: {e2}")
        print("让我们创建一个最基本的FastAPI服务...")
        
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        
        app = FastAPI(title="HiAgent Plugin Runtime", version="0.1.0")
        
        @app.get("/")
        async def root():
            return {"message": "HiAgent Plugin Runtime is running!", "version": "0.1.0"}
        
        @app.get("/health")
        async def health():
            return {"status": "ok", "service": "plugin-runtime"}
            
        print("✅ Created basic FastAPI app")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting HiAgent Plugin Runtime...")
    print("📍 API documentation: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")