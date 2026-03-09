"""小红书上传器 - MCP 版本

基于 xiaohongshu-mcp 的 HTTP API 实现
与 social-auto-upload 框架集成
"""

from .main import XhsUploaderMCP, upload_video, upload_image

__all__ = ['XhsUploaderMCP', 'upload_video', 'upload_image']
__version__ = "1.0.0"
__author__ = "social-auto-upload + xiaohongshu-mcp"
