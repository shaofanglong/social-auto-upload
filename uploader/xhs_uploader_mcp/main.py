"""小红书上传器 - MCP 版本

基于 xiaohongshu-mcp 的 HTTP API 实现
"""

import requests
from pathlib import Path
from typing import List, Optional
import json


class XhsUploaderMCP:
    """小红书上传器（MCP 版本）"""
    
    def __init__(self, mcp_url: str = "http://localhost:8080"):
        """
        初始化上传器
        
        Args:
            mcp_url: xiaohongshu-mcp 服务地址
        """
        self.mcp_url = mcp_url.rstrip('/')
        self.api_base = f"{self.mcp_url}/api/v1"
        self.timeout = 300  # 5分钟超时（视频上传可能较慢）
    
    def check_login(self) -> bool:
        """检查登录状态"""
        try:
            resp = requests.get(
                f"{self.api_base}/login/status",
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("is_logged_in", False)
        except Exception as e:
            print(f"检查登录状态失败: {e}")
            return False
    
    def get_login_qrcode(self) -> dict:
        """获取登录二维码"""
        try:
            resp = requests.get(
                f"{self.api_base}/login/qrcode",
                timeout=10
            )
            resp.raise_for_status()
            return resp.json().get("data", {})
        except Exception as e:
            print(f"获取登录二维码失败: {e}")
            return {}
    
    def upload_image(
        self,
        title: str,
        content: str,
        images: List[str],
        tags: Optional[List[str]] = None,
        visibility: str = "公开可见",
        schedule_at: Optional[str] = None
    ) -> dict:
        """
        上传图文到小红书
        
        Args:
            title: 标题
            content: 描述内容
            images: 图片路径列表（本地绝对路径或 HTTP 链接）
            tags: 标签列表
            visibility: 可见范围（"公开可见" | "仅自己可见" | "仅互关好友可见"）
            schedule_at: 定时发布时间（ISO8601 格式，如 "2024-03-09T15:00:00+08:00"）
        
        Returns:
            dict: {"success": True/False, "data": {...}, "message": "..."}
        """
        # 验证图片路径
        for img_path in images:
            if not img_path.startswith('http'):
                if not Path(img_path).exists():
                    return {
                        "success": False,
                        "error": f"图片文件不存在: {img_path}"
                    }
        
        payload = {
            "title": title,
            "content": content,
            "images": images,
            "tags": tags or [],
            "visibility": visibility
        }
        
        if schedule_at:
            payload["schedule_at"] = schedule_at
        
        try:
            resp = requests.post(
                f"{self.api_base}/publish",
                json=payload,
                timeout=self.timeout
            )
            resp.raise_for_status()
            result = resp.json()
            
            if result.get("success"):
                return {
                    "success": True,
                    "data": result.get("data", {}),
                    "message": result.get("message", "发布成功")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "发布失败")
                }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "请求超时，请检查 xiaohongshu-mcp 服务是否正常运行"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": f"无法连接到 xiaohongshu-mcp 服务 ({self.mcp_url})，请确保服务已启动"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"上传图文失败: {str(e)}"
            }
    
    def upload_video(
        self,
        title: str,
        content: str,
        video: str,
        tags: Optional[List[str]] = None,
        visibility: str = "公开可见",
        schedule_at: Optional[str] = None
    ) -> dict:
        """
        上传视频到小红书
        
        Args:
            title: 标题
            content: 描述内容
            video: 视频文件路径（本地绝对路径）
            tags: 标签列表
            visibility: 可见范围（"公开可见" | "仅自己可见" | "仅互关好友可见"）
            schedule_at: 定时发布时间（ISO8601 格式）
        
        Returns:
            dict: {"success": True/False, "data": {...}, "message": "..."}
        """
        # 验证视频文件
        if not Path(video).exists():
            return {
                "success": False,
                "error": f"视频文件不存在: {video}"
            }
        
        payload = {
            "title": title,
            "content": content,
            "video": video,
            "tags": tags or [],
            "visibility": visibility
        }
        
        if schedule_at:
            payload["schedule_at"] = schedule_at
        
        try:
            print(f"正在上传视频到小红书...")
            print(f"  标题: {title}")
            print(f"  视频: {video}")
            print(f"  标签: {tags}")
            
            resp = requests.post(
                f"{self.api_base}/publish_video",
                json=payload,
                timeout=self.timeout
            )
            resp.raise_for_status()
            result = resp.json()
            
            if result.get("success"):
                print(f"✅ 视频上传成功")
                return {
                    "success": True,
                    "data": result.get("data", {}),
                    "message": result.get("message", "发布成功")
                }
            else:
                error_msg = result.get("error", "发布失败")
                print(f"❌ 视频上传失败: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "请求超时（视频上传可能需要较长时间），请检查 xiaohongshu-mcp 服务是否正常运行"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": f"无法连接到 xiaohongshu-mcp 服务 ({self.mcp_url})，请确保服务已启动"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"上传视频失败: {str(e)}"
            }


# ==================== 兼容接口 ====================

def upload_video(
    title: str,
    video_path: str,
    desc: str,
    tags: Optional[List[str]] = None,
    mcp_url: str = "http://localhost:8080",
    visibility: str = "公开可见",
    schedule_at: Optional[str] = None
) -> dict:
    """
    上传视频到小红书（兼容接口）
    
    Args:
        title: 标题
        video_path: 视频文件路径
        desc: 描述内容
        tags: 标签列表
        mcp_url: xiaohongshu-mcp 服务地址
        visibility: 可见范围
        schedule_at: 定时发布时间
    
    Returns:
        dict: {"success": True/False, "data": {...}, "message": "..."}
    """
    uploader = XhsUploaderMCP(mcp_url)
    
    # 检查登录
    if not uploader.check_login():
        return {
            "success": False,
            "error": "未登录，请先启动 xiaohongshu-mcp 服务并扫码登录"
        }
    
    return uploader.upload_video(
        title=title,
        content=desc,
        video=video_path,
        tags=tags,
        visibility=visibility,
        schedule_at=schedule_at
    )


def upload_image(
    title: str,
    image_paths: List[str],
    desc: str,
    tags: Optional[List[str]] = None,
    mcp_url: str = "http://localhost:8080",
    visibility: str = "公开可见",
    schedule_at: Optional[str] = None
) -> dict:
    """
    上传图文到小红书（兼容接口）
    
    Args:
        title: 标题
        image_paths: 图片路径列表
        desc: 描述内容
        tags: 标签列表
        mcp_url: xiaohongshu-mcp 服务地址
        visibility: 可见范围
        schedule_at: 定时发布时间
    
    Returns:
        dict: {"success": True/False, "data": {...}, "message": "..."}
    """
    uploader = XhsUploaderMCP(mcp_url)
    
    # 检查登录
    if not uploader.check_login():
        return {
            "success": False,
            "error": "未登录，请先启动 xiaohongshu-mcp 服务并扫码登录"
        }
    
    return uploader.upload_image(
        title=title,
        content=desc,
        images=image_paths,
        tags=tags,
        visibility=visibility,
        schedule_at=schedule_at
    )
