import asyncio
import sys
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

def _parse_daily_times(times):
    """将前端传来的 ['10:00', '14:00'] 转为 generate_schedule_time_next_day 需要的整数小时 [10, 14]"""
    if not times:
        return None
    result = []
    for t in times:
        if isinstance(t, int):
            result.append(t)
        elif isinstance(t, str) and ':' in t:
            result.append(int(t.split(':')[0]))
        else:
            try:
                result.append(int(t))
            except Exception:
                result.append(10)
    return result or None


def _resolve_xhs_mcp_urls(account_file):
    """根据 account_file 列表解析对应的 MCP URL，返回 [(account_name, mcp_url), ...]"""
    import sqlite3
    import sys
    mcp_urls = []
    
    print(f"[DEBUG] _resolve_xhs_mcp_urls input: {account_file}", file=sys.stderr)
    
    if account_file and len(account_file) > 0:
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            for file_path in account_file:
                print(f"[DEBUG] Querying DB for filePath={file_path}", file=sys.stderr)
                cursor.execute('SELECT userName FROM user_info WHERE filePath = ? AND type = 1', (file_path,))
                row = cursor.fetchone()
                if row:
                    account_name = row[0]
                    mcp_url = XHS_MCP_ACCOUNTS.get(account_name, XHS_MCP_URL)
                    print(f"[DEBUG] Found account: {account_name} -> {mcp_url}", file=sys.stderr)
                    mcp_urls.append((account_name, mcp_url))
                else:
                    print(f"[DEBUG] No account found for {file_path}, using default", file=sys.stderr)
                    mcp_urls.append(("默认账号", XHS_MCP_URL))
    else:
        print("[DEBUG] No account_file provided, using default", file=sys.stderr)
        mcp_urls.append(("默认账号", XHS_MCP_URL))
    
    print(f"[DEBUG] Final mcp_urls: {mcp_urls}", file=sys.stderr)
    return mcp_urls


def post_video_xhs(title, files, tags, account_file=None, category=TencentZoneTypes.LIFESTYLE.value,
                   enableTimer=False, videos_per_day=1, daily_times=None, start_days=0):
    """使用 xiaohongshu-mcp 发布视频到小红书，支持多账号和定时发布"""
    if daily_times is None:
        daily_times = ['10:00']

    # 生成文件完整路径
    file_paths = [Path(BASE_DIR / "videoFile" / f) for f in files]

    # 处理标签
    desc = " ".join([f"#{tag}" for tag in tags]) if tags else ""

    # 解析账号 → MCP URL
    mcp_urls = _resolve_xhs_mcp_urls(account_file)

    parsed_times = _parse_daily_times(daily_times)

    # 生成定时发布时间列表
    if enableTimer:
        raw_times = generate_schedule_time_next_day(
            total_videos=len(file_paths),
            videos_per_day=videos_per_day or 1,
            daily_times=parsed_times,
            start_days=start_days or 0
        )
        from datetime import timezone
        import datetime as _dt
        tz = _dt.timezone(_dt.timedelta(hours=8))
        publish_times = [t.replace(tzinfo=tz).isoformat() if t else None for t in raw_times]
    else:
        publish_times = [None] * len(file_paths)

    for idx, file in enumerate(file_paths):
        schedule_at = publish_times[idx] if idx < len(publish_times) else None
        print(f"\n[DEBUG] 视频：{file}  定时：{schedule_at or '立即发布'}", file=sys.stderr)

        for account_name, mcp_url in mcp_urls:
            print(f"[DEBUG] 账号 [{account_name}] 发布中...", file=sys.stderr)
            print(f"[DEBUG] 调用 xhs_mcp_upload_video:", file=sys.stderr)
            print(f"[DEBUG]   title={title}", file=sys.stderr)
            print(f"[DEBUG]   video_path={str(file)}", file=sys.stderr)
            print(f"[DEBUG]   desc={desc}", file=sys.stderr)
            print(f"[DEBUG]   tags={tags}", file=sys.stderr)
            print(f"[DEBUG]   mcp_url={mcp_url}", file=sys.stderr)
            print(f"[DEBUG]   visibility={XHS_VISIBILITY}", file=sys.stderr)
            print(f"[DEBUG]   schedule_at={schedule_at}", file=sys.stderr)
            
            result = xhs_mcp_upload_video(
                title=title,
                video_path=str(file),
                desc=desc,
                tags=tags,
                mcp_url=mcp_url,
                visibility=XHS_VISIBILITY,
                schedule_at=schedule_at
            )
            
            print(f"[DEBUG] xhs_mcp_upload_video 返回: {result}", file=sys.stderr)
            
            if result.get("success"):
                print(f"[DEBUG] 发布成功", file=sys.stderr)
            else:
                print(f"[DEBUG] 发布失败: {result.get('error', 'Unknown error')}", file=sys.stderr)


def post_image_xhs(title, images, tags, account_file=None, category=TencentZoneTypes.LIFESTYLE.value,
                   enableTimer=False, videos_per_day=1, daily_times=None, start_days=0):
    """使用 xiaohongshu-mcp 发布图文到小红书，支持多账号和定时发布"""
    from uploader.xhs_uploader_mcp import upload_image as xhs_mcp_upload_image
    if daily_times is None:
        daily_times = ['10:00']

    # 生成图片完整路径
    image_paths = [str(Path(BASE_DIR / "videoFile" / img)) for img in images]

    # 处理标签
    desc = " ".join([f"#{tag}" for tag in tags]) if tags else ""

    # 解析账号 → MCP URL
    mcp_urls = _resolve_xhs_mcp_urls(account_file)

    # daily_times 字符串转整数小时
    parsed_times = _parse_daily_times(daily_times)

    # 定时发布（图文按账号数量生成时间）
    if enableTimer:
        raw_times = generate_schedule_time_next_day(
            total_videos=len(mcp_urls),
            videos_per_day=videos_per_day or 1,
            daily_times=parsed_times,
            start_days=start_days or 0
        )
        from datetime import timezone
        import datetime as _dt
        tz = _dt.timezone(_dt.timedelta(hours=8))
        publish_times = [t.replace(tzinfo=tz).isoformat() if t else None for t in raw_times]
    else:
        publish_times = [None] * len(mcp_urls)

    print(f"\n图文标题：{title}  图片数：{len(image_paths)}")

    for idx, (account_name, mcp_url) in enumerate(mcp_urls):
        schedule_at = publish_times[idx] if idx < len(publish_times) else None
        print(f"  账号 [{account_name}] 发布中... 定时：{schedule_at or '立即'}")
        result = xhs_mcp_upload_image(
            title=title,
            image_paths=image_paths,
            desc=desc,
            tags=tags,
            mcp_url=mcp_url,
            visibility=XHS_VISIBILITY,
            schedule_at=schedule_at
        )
        if result.get("success"):
            # print removed to avoid GBK encoding error
            pass
        else:
            # print removed to avoid GBK encoding error
            pass


