# social-auto-upload 小红书 CDP 改造完成

## ✅ 已完成的工作

### 1. 创建 CDP 版本的小红书上传器

**位置**: `uploader/xhs_uploader_cdp/`

**文件**:
- `__init__.py` - 模块初始化
- `main.py` - 核心上传逻辑（基于 xiaohongshu-skills）
- `README.md` - 使用文档

**特性**:
- ✅ CDP 浏览器自动化（更稳定）
- ✅ 不需要签名服务
- ✅ 不需要 cookies 管理
- ✅ 支持多账号隔离（独立 profile + 端口）
- ✅ 兼容 social-auto-upload 的接口

### 2. 配置文件

**位置**: `conf.py`

**新增配置**:
```python
# 小红书账号配置（CDP 版本）
XHS_ACCOUNTS_CDP = {
    "旗舰店": {
        "account_name": "旗舰店",
        "enabled": True,
        "description": "旗舰店账号"
    },
    "实况分析": {
        "account_name": "实况分析", 
        "enabled": True,
        "description": "实况分析账号"
    }
}

# 默认使用的小红书账号
XHS_DEFAULT_ACCOUNT = "旗舰店"

# 是否使用 CDP 版本
USE_XHS_CDP = True
```

### 3. 测试脚本

**位置**: `test_xhs_cdp.py`

测试双账号上传功能（视频 + 图文）

### 4. 使用示例

**位置**: `examples/upload_to_xhs_cdp.py`

展示如何使用 CDP 版本上传器

---

## 📋 使用步骤

### 1. 添加小红书账号

```bash
# 添加旗舰店账号
python D:\xiaohongshu-skills\scripts\cli.py add-account --name 旗舰店

# 添加实况分析账号
python D:\xiaohongshu-skills\scripts\cli.py add-account --name 实况分析
```

### 2. 登录账号

```bash
# 登录旗舰店
python D:\xiaohongshu-skills\scripts\cli.py --account 旗舰店 login

# 登录实况分析
python D:\xiaohongshu-skills\scripts\cli.py --account 实况分析 login
```

会弹出浏览器，扫码登录。

### 3. 测试上传

```bash
cd D:\social-auto-upload
python test_xhs_cdp.py
```

### 4. 在代码中使用

```python
from uploader.xhs_uploader_cdp import upload_video, upload_image

# 上传视频到旗舰店
result = upload_video(
    account_name="旗舰店",
    video_path="D:/video.mp4",
    title="视频标题",
    desc="视频描述",
    tags=["标签1", "标签2"],
    dry_run=False  # False=实际发布
)

# 上传图文到实况分析
result = upload_image(
    account_name="实况分析",
    image_paths=["D:/img1.jpg", "D:/img2.jpg"],
    title="图文标题",
    desc="图文描述",
    tags=["标签1", "标签2"],
    dry_run=False
)
```

---

## 🔄 多账号隔离机制

每个账号使用：
- **独立的 Chrome profile** - 登录状态完全隔离
- **独立的调试端口** - 进程级别隔离

示例：
- 旗舰店 → `C:\Users\12943\.xhs\accounts\旗舰店\chrome-profile` + port 9223
- 实况分析 → `C:\Users\12943\.xhs\accounts\实况分析\chrome-profile` + port 9224

---

## 📊 与旧版本对比

| 特性 | xhs_uploader（旧） | xhs_uploader_cdp（新） |
|------|------------------|---------------------|
| 实现方式 | xhs 库（API 逆向） | CDP 浏览器自动化 |
| 稳定性 | ⚠️ 容易失效 | ✅ 更稳定 |
| 签名服务 | ❌ 需要 Flask 服务 | ✅ 不需要 |
| Cookies | ❌ 需要手动管理 | ✅ 自动管理 |
| 多账号 | ⚠️ Cookie 切换 | ✅ Profile 隔离 |
| 风控 | ⚠️ 容易被检测 | ✅ 模拟真人操作 |

---

## 🚀 下一步

### 集成到 Web 界面（可选）

如果需要在 Web 界面中使用 CDP 版本：

1. 修改 `sau_backend/` 中的小红书上传逻辑
2. 添加账号选择下拉框
3. 调用 `uploader.xhs_uploader_cdp` 而不是 `uploader.xhs_uploader`

### 保留其他平台

- ✅ 抖音 - `uploader/douyin_uploader/`
- ✅ B站 - `uploader/bilibili_uploader/`
- ✅ 快手 - `uploader/ks_uploader/`
- ✅ 视频号 - `uploader/tencent_uploader/`

这些平台的上传器保持不变，继续使用原有实现。

---

## 📝 注意事项

1. **依赖**：需要 xiaohongshu-skills 安装在 `D:\xiaohongshu-skills`
2. **Chrome**：需要安装 Chrome 浏览器
3. **登录**：每个账号需要先登录才能使用
4. **测试模式**：建议先用 `dry_run=True` 测试，确认无误后再实际发布

---

## 🐛 故障排查

### 问题：CLI 路径不存在

修改 `uploader/xhs_uploader_cdp/main.py` 中的 `XHS_SKILLS_CLI` 路径。

### 问题：账号未登录

运行登录命令：
```bash
python D:\xiaohongshu-skills\scripts\cli.py --account 账号名 login
```

### 问题：Chrome 未安装

下载安装 Chrome：https://www.google.cn/chrome/

---

## 📄 文件清单

```
D:\social-auto-upload\
├── uploader/
│   ├── xhs_uploader_cdp/          # 新增：CDP 版本
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── README.md
│   ├── xhs_uploader/              # 保留：旧版本（可选）
│   ├── douyin_uploader/           # 保留：抖音
│   ├── bilibili_uploader/         # 保留：B站
│   └── ...
├── examples/
│   └── upload_to_xhs_cdp.py       # 新增：使用示例
├── conf.py                        # 修改：添加 CDP 配置
├── test_xhs_cdp.py                # 新增：测试脚本
└── CHANGELOG_CDP.md               # 本文件
```

---

改造完成！🎉
