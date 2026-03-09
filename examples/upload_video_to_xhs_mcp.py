"""小红书上传示例 - MCP 版本

展示如何使用 xiaohongshu-mcp 上传视频和图文
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from conf import XHS_MCP_URL
from uploader.xhs_uploader_mcp import XhsUploaderMCP, upload_video, upload_image


def check_mcp_service():
    """检查 xiaohongshu-mcp 服务是否运行"""
    print("="*60)
    print("检查 xiaohongshu-mcp 服务状态")
    print("="*60)
    
    uploader = XhsUploaderMCP(XHS_MCP_URL)
    
    if uploader.check_login():
        print(f"✅ 已登录，服务地址: {XHS_MCP_URL}")
        return True
    else:
        print(f"❌ 未登录或服务未启动")
        print(f"\n请先启动 xiaohongshu-mcp 服务:")
        print(f"  cd D:\\xiaohongshu-mcp")
        print(f"  go run . --port 8080")
        print(f"\n然后访问 {XHS_MCP_URL}/api/v1/login/qrcode 扫码登录")
        return False


def upload_video_example():
    """视频上传示例"""
    print("\n" + "="*60)
    print("小红书视频上传示例（MCP 版本）")
    print("="*60)
    
    # 视频文件路径（请修改为实际路径）
    video_path = "D:/videos/test_video.mp4"
    
    # 检查文件是否存在
    if not Path(video_path).exists():
        print(f"❌ 视频文件不存在: {video_path}")
        print(f"请修改 video_path 为实际的视频文件路径")
        return
    
    # 视频信息
    title = "测试视频标题"
    desc = """这是视频描述内容

可以包含多行文字
这里是视频的主要介绍"""
    
    tags = ["测试", "小红书", "自动化"]
    
    print(f"\n正在上传视频...")
    print(f"  标题: {title}")
    print(f"  视频: {video_path}")
    print(f"  标签: {tags}")
    
    # 上传视频
    result = upload_video(
        title=title,
        video_path=video_path,
        desc=desc,
        tags=tags,
        mcp_url=XHS_MCP_URL
    )
    
    # 打印结果
    if result.get("success"):
        print(f"\n✅ 上传成功！")
        print(f"   帖子ID: {result.get('data', {}).get('post_id', 'unknown')}")
    else:
        print(f"\n❌ 上传失败: {result.get('error')}")


def upload_image_example():
    """图文上传示例"""
    print("\n" + "="*60)
    print("小红书图文上传示例（MCP 版本）")
    print("="*60)
    
    # 图片文件路径（请修改为实际路径）
    image_paths = [
        "D:/images/img1.jpg",
        "D:/images/img2.jpg",
        "D:/images/img3.jpg"
    ]
    
    # 检查文件是否存在
    missing = [img for img in image_paths if not Path(img).exists()]
    if missing:
        print(f"❌ 图片文件不存在: {missing}")
        print(f"请修改 image_paths 为实际的图片文件路径")
        return
    
    # 图文信息
    title = "测试图文标题"
    desc = """这是图文描述内容

可以包含多行文字
这里是图文的主要介绍"""
    
    tags = ["测试", "小红书", "自动化"]
    
    print(f"\n正在上传图文...")
    print(f"  标题: {title}")
    print(f"  图片数量: {len(image_paths)}")
    print(f"  标签: {tags}")
    
    # 上传图文
    result = upload_image(
        title=title,
        image_paths=image_paths,
        desc=desc,
        tags=tags,
        mcp_url=XHS_MCP_URL
    )
    
    # 打印结果
    if result.get("success"):
        print(f"\n✅ 上传成功！")
        print(f"   帖子ID: {result.get('data', {}).get('post_id', 'unknown')}")
    else:
        print(f"\n❌ 上传失败: {result.get('error')}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("小红书 MCP 上传器使用示例")
    print("="*60)
    
    # 显示配置
    print(f"\n当前配置:")
    print(f"  MCP 服务地址: {XHS_MCP_URL}")
    
    # 检查服务状态
    if not check_mcp_service():
        return
    
    print("\n" + "="*60)
    print("⚠️  注意：请修改示例中的文件路径为实际路径")
    print("="*60)
    
    # 运行示例（取消注释以运行）
    # upload_video_example()
    # upload_image_example()
    
    print("\n" + "="*60)
    print("示例代码已准备好，请取消注释以运行")
    print("="*60)


if __name__ == "__main__":
    main()
