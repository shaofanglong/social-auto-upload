import asyncio
from pathlib import Path

from conf import BASE_DIR, XHS_MCP_URL, XHS_MCP_ACCOUNTS, XHS_VISIBILITY
from uploader.douyin_uploader.main import DouYinVideo
from uploader.ks_uploader.main import KSVideo
from uploader.tencent_uploader.main import TencentVideo
from uploader.xhs_uploader_mcp import upload_video as xhs_mcp_upload_video
from utils.constant import TencentZoneTypes
from utils.files_times import generate_schedule_time_next_day


def post_video_tencent(title,files,tags,account_file,category=TencentZoneTypes.LIFESTYLE.value,enableTimer=False,videos_per_day = 1, daily_times=None,start_days = 0, is_draft=False):
    # 生成文件的完整路径
    account_file = [Path(BASE_DIR / "cookiesFile" / file) for file in account_file]
    files = [Path(BASE_DIR / "videoFile" / file) for file in files]
    if enableTimer:
        publish_datetimes = generate_schedule_time_next_day(len(files), videos_per_day, daily_times,start_days)
    else:
        publish_datetimes = [0 for i in range(len(files))]
    for index, file in enumerate(files):
        for cookie in account_file:
            print(f"文件路径{str(file)}")
            # 打印视频文件名、标题和 hashtag
            print(f"视频文件名：{file}")
            print(f"标题：{title}")
            print(f"Hashtag：{tags}")
            app = TencentVideo(title, str(file), tags, publish_datetimes[index], cookie, category, is_draft)
            asyncio.run(app.main(), debug=False)


def post_video_DouYin(title,files,tags,account_file,category=TencentZoneTypes.LIFESTYLE.value,enableTimer=False,videos_per_day = 1, daily_times=None,start_days = 0,
                      thumbnail_path = '',
                      productLink = '', productTitle = ''):
    # 生成文件的完整路径
    account_file = [Path(BASE_DIR / "cookiesFile" / file) for file in account_file]
    files = [Path(BASE_DIR / "videoFile" / file) for file in files]
    if enableTimer:
        publish_datetimes = generate_schedule_time_next_day(len(files), videos_per_day, daily_times,start_days)
    else:
        publish_datetimes = [0 for i in range(len(files))]
    for index, file in enumerate(files):
        for cookie in account_file:
            print(f"文件路径{str(file)}")
            # 打印视频文件名、标题和 hashtag
            print(f"视频文件名：{file}")
            print(f"标题：{title}")
            print(f"Hashtag：{tags}")
            app = DouYinVideo(title, str(file), tags, publish_datetimes[index], cookie, thumbnail_path, productLink, productTitle)
            asyncio.run(app.main(), debug=False)


def post_video_ks(title,files,tags,account_file,category=TencentZoneTypes.LIFESTYLE.value,enableTimer=False,videos_per_day = 1, daily_times=None,start_days = 0):
    # 生成文件的完整路径
    account_file = [Path(BASE_DIR / "cookiesFile" / file) for file in account_file]
    files = [Path(BASE_DIR / "videoFile" / file) for file in files]
    if enableTimer:
        publish_datetimes = generate_schedule_time_next_day(len(files), videos_per_day, daily_times,start_days)
    else:
        publish_datetimes = [0 for i in range(len(files))]
    for index, file in enumerate(files):
        for cookie in account_file:
            print(f"文件路径{str(file)}")
            # 打印视频文件名、标题和 hashtag
            print(f"视频文件名：{file}")
            print(f"标题：{title}")
            print(f"Hashtag：{tags}")
            app = KSVideo(title, str(file), tags, publish_datetimes[index], cookie)
            asyncio.run(app.main(), debug=False)

def post_video_xhs(title, files, tags, account_file=None, category=TencentZoneTypes.LIFESTYLE.value, enableTimer=False, videos_per_day=1, daily_times=None, start_days=0):
    """
    使用 xiaohongshu-mcp 发布视频到小红书
    
    支持多账号：
    - 如果传入 account_file（账号文件路径列表），会根据账号名查找对应的 MCP URL
    - 如果没有传入，使用默认 MCP URL
    """
    import sqlite3
    
    # 生成文件的完整路径
    files = [Path(BASE_DIR / "videoFile" / file) for file in files]
    
    # 处理标签
    desc = " ".join([f"#{tag}" for tag in tags]) if tags else ""
    
    # 确定要使用的 MCP URL 列表
    mcp_urls = []
    
    if account_file and len(account_file) > 0:
        # 根据 account_file（filePath）查询账号名，然后映射到 MCP URL
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            for file_path in account_file:
                cursor.execute('SELECT userName FROM user_info WHERE filePath = ? AND type = 1', (file_path,))
                row = cursor.fetchone()
                if row:
                    account_name = row[0]
                    # 从配置中查找对应的 MCP URL
                    mcp_url = XHS_MCP_ACCOUNTS.get(account_name, XHS_MCP_URL)
                    mcp_urls.append((account_name, mcp_url))
                    print(f"账号 [{account_name}] 映射到 MCP: {mcp_url}")
                else:
                    print(f"⚠️  未找到账号信息: {file_path}，使用默认 MCP")
                    mcp_urls.append(("默认账号", XHS_MCP_URL))
    else:
        # 没有指定账号，使用默认 MCP
        mcp_urls.append(("默认账号", XHS_MCP_URL))
    
    # 对每个文件和每个账号进行发布
    for file in files:
        print(f"\n视频文件名：{file}")
        print(f"标题：{title}")
        print(f"Hashtag：{tags}")
        
        for account_name, mcp_url in mcp_urls:
            print(f"\n使用账号 [{account_name}] 发布到小红书...")
            
            # 调用 MCP API
            result = xhs_mcp_upload_video(
                title=title,
                video_path=str(file),
                desc=desc,
                tags=tags,
                mcp_url=mcp_url,
                visibility=XHS_VISIBILITY
            )
            
            if result.get("success"):
                post_id = result.get('data', {}).get('post_id', 'unknown')
                print(f"✅ [{account_name}] 发布成功: {post_id}")
            else:
                error = result.get('error', 'unknown error')
                print(f"❌ [{account_name}] 发布失败: {error}")



# post_video("333",["demo.mp4"],"d","d")
# post_video_DouYin("333",["demo.mp4"],"d","d")