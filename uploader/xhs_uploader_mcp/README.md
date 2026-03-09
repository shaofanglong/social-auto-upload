# 小红书上传器 - MCP 版本

基于 xiaohongshu-mcp 的 HTTP API 实现，替换原有的 xhs 库（API 逆向）和 CDP CLI 版本。

## 优势

- ✅ **更稳定**：基于 xiaohongshu-mcp 的 CDP 浏览器自动化
- ✅ **不需要签名服务**：无需维护独立的签名服务
- ✅ **不需要 Cookie 管理**：xiaohongshu-mcp 自动管理登录状态
- ✅ **简单易用**：只需 HTTP 请求，无需复杂配置
- ✅ **功能完整**：支持图文、视频、定时发布

## 前置条件

### 1. 启动 xiaohongshu-mcp 服务

```bash
cd D:\xiaohongshu-mcp
go run . --port 8080
```

### 2. 登录小红书

访问 `http://localhost:8080/api/v1/login/qrcode` 获取二维码，用小红书 App 扫码登录。

或者使用 Python 脚本：

```python
from uploader.xhs_uploader_mcp import XhsUploaderMCP

uploader = XhsUploaderMCP("http://localhost:8080")
qrcode_data = uploader.get_login_qrcode()
print(f"请扫描二维码登录: {qrcode_data['img']}")
```

## 使用方法

### 方式 1：直接使用类

```python
from uploader.xhs_uploader_mcp import XhsUploaderMCP

uploader = XhsUploaderMCP("http://localhost:8080")

# 检查登录状态
if not uploader.check_login():
    print("未登录，请先扫码登录")
    exit(1)

# 上传视频
result = uploader.upload_video(
    title="视频标题",
    content="视频描述 #标签1 #标签2",
    video="D:/videos/test.mp4",
    tags=["标签1", "标签2"],
    visibility="公开可见"
)

if result["success"]:
    print(f"发布成功: {result['data']['post_id']}")
else:
    print(f"发布失败: {result['error']}")

# 上传图文
result = uploader.upload_image(
    title="图文标题",
    content="图文描述 #标签1 #标签2",
    images=["D:/images/img1.jpg", "D:/images/img2.jpg"],
    tags=["标签1", "标签2"],
    visibility="公开可见"
)
```

### 方式 2：使用兼容函数

```python
from uploader.xhs_uploader_mcp import upload_video, upload_image

# 上传视频
result = upload_video(
    title="视频标题",
    video_path="D:/videos/test.mp4",
    desc="视频描述",
    tags=["标签1", "标签2"],
    mcp_url="http://localhost:8080"
)

# 上传图文
result = upload_image(
    title="图文标题",
    image_paths=["D:/images/img1.jpg", "D:/images/img2.jpg"],
    desc="图文描述",
    tags=["标签1", "标签2"],
    mcp_url="http://localhost:8080"
)
```

### 方式 3：集成到 social-auto-upload

在 `conf.py` 中配置：

```python
# xiaohongshu-mcp 服务地址
XHS_MCP_URL = "http://localhost:8080"
```

然后在代码中使用：

```python
from conf import XHS_MCP_URL
from uploader.xhs_uploader_mcp import upload_video

result = upload_video(
    title="视频标题",
    video_path="D:/videos/test.mp4",
    desc="视频描述",
    tags=["标签1", "标签2"],
    mcp_url=XHS_MCP_URL
)
```

## 参数说明

### upload_video

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | str | ✅ | 视频标题（最多 30 字） |
| content | str | ✅ | 视频描述 |
| video | str | ✅ | 视频文件路径（本地绝对路径） |
| tags | List[str] | ❌ | 标签列表 |
| visibility | str | ❌ | 可见范围："公开可见"（默认）、"仅自己可见"、"仅互关好友可见" |
| schedule_at | str | ❌ | 定时发布时间（ISO8601 格式，如 "2024-03-09T15:00:00+08:00"） |

### upload_image

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | str | ✅ | 图文标题（最多 30 字） |
| content | str | ✅ | 图文描述 |
| images | List[str] | ✅ | 图片路径列表（本地绝对路径或 HTTP 链接） |
| tags | List[str] | ❌ | 标签列表 |
| visibility | str | ❌ | 可见范围 |
| schedule_at | str | ❌ | 定时发布时间 |

## 返回值

```python
{
    "success": True,  # 是否成功
    "data": {
        "post_id": "xxx",  # 帖子 ID
        "title": "xxx",
        "status": "published"
    },
    "message": "发布成功"
}
```

失败时：

```python
{
    "success": False,
    "error": "错误信息"
}
```

## 故障排查

### 问题 1：无法连接到 xiaohongshu-mcp 服务

**错误信息**：`无法连接到 xiaohongshu-mcp 服务 (http://localhost:8080)`

**解决方法**：
1. 确保 xiaohongshu-mcp 服务已启动：
   ```bash
   cd D:\xiaohongshu-mcp
   go run . --port 8080
   ```
2. 检查端口是否被占用：
   ```bash
   netstat -ano | findstr :8080
   ```

### 问题 2：未登录

**错误信息**：`未登录，请先启动 xiaohongshu-mcp 服务并扫码登录`

**解决方法**：
1. 访问 `http://localhost:8080/api/v1/login/qrcode`
2. 用小红书 App 扫描二维码登录
3. 登录成功后重试

### 问题 3：视频/图片文件不存在

**错误信息**：`视频文件不存在: D:/videos/test.mp4`

**解决方法**：
1. 检查文件路径是否正确（使用绝对路径）
2. 确保文件存在且有读取权限

### 问题 4：请求超时

**错误信息**：`请求超时（视频上传可能需要较长时间）`

**解决方法**：
1. 视频上传需要较长时间，请耐心等待
2. 检查网络连接是否正常
3. 检查 xiaohongshu-mcp 服务日志

## 与旧版本的区别

| 特性 | xhs_uploader（旧） | xhs_uploader_cdp（旧） | xhs_uploader_mcp（新） |
|------|------------------|---------------------|---------------------|
| 实现方式 | xhs 库（API 逆向） | xiaohongshu-skills CLI | xiaohongshu-mcp HTTP API |
| 稳定性 | ⚠️ 容易失效 | ✅ 稳定 | ✅ 最稳定 |
| 签名服务 | ❌ 需要 | ✅ 不需要 | ✅ 不需要 |
| Cookie 管理 | ❌ 需要手动管理 | ✅ 自动管理 | ✅ 自动管理 |
| 多账号 | ⚠️ Cookie 切换 | ✅ Profile 隔离 | ⚠️ 单账号（需多实例） |
| 依赖 | xhs 库 + 签名服务 | xiaohongshu-skills | xiaohongshu-mcp |

## 注意事项

1. **xiaohongshu-mcp 必须先启动**
   - 默认端口 8080
   - 需要先扫码登录

2. **图片/视频路径**
   - 推荐使用本地绝对路径
   - 图片也支持 HTTP/HTTPS 链接
   - 视频仅支持本地路径

3. **多账号支持**
   - xiaohongshu-mcp 目前是单账号（通过 Cookie 文件）
   - 如需多账号，需要启动多个 MCP 实例（不同端口 + 不同 Cookie 路径）

4. **定时发布**
   - 支持 `schedule_at` 参数（ISO8601 格式）
   - 示例：`"2024-03-09T15:00:00+08:00"`

## 更多信息

- xiaohongshu-mcp 项目：https://github.com/xpzouying/xiaohongshu-mcp
- social-auto-upload 项目：https://github.com/dreammis/social-auto-upload
