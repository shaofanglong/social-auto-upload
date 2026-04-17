from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
LOCAL_CHROME_PATH = ""   # change me necessary！ for example C:/Program Files/Google/Chrome/Application/chrome.exe
LOCAL_CHROME_HEADLESS = False

# ==================== 小红书 MCP 配置 ====================
# 使用 xiaohongshu-mcp HTTP API（最稳定，推荐）

# 小红书多账号映射（账号名 → MCP 服务地址）
# 每个账号需要启动独立的 xiaohongshu-mcp 实例
XHS_MCP_ACCOUNTS = {
    "账号A": "http://localhost:8080",  # 第一个账号
    "账号B": "http://localhost:8081",  # 第二个账号
}

# 默认 MCP 服务地址（当没有指定账号时使用）
XHS_MCP_URL = "http://localhost:8080"

# 小红书发布默认可见范围
XHS_VISIBILITY = "公开可见"  # "公开可见" | "仅自己可见" | "仅互关好友可见"
