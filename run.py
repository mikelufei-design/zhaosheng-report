import uvicorn
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 50)
    print("  招生智能体系统")
    print("  Agent Workflow System")
    print("=" * 50)
    print()
    print("  启动服务器中...")
    print("  打开浏览器访问: http://127.0.0.1:8080")
    print()
    print("  按 Ctrl+C 停止服务器")
    print()
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True, log_level="info")
