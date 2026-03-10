import asyncio
import os
import sqlite3
import threading
import time
import uuid
from pathlib import Path
from queue import Queue
from flask_cors import CORS
from myUtils.auth import check_cookie
from flask import Flask, request, jsonify, Response, render_template, send_from_directory
from conf import BASE_DIR, XHS_MCP_URL, XHS_MCP_ACCOUNTS
from myUtils.login import get_tencent_cookie, douyin_cookie_gen, get_ks_cookie
from myUtils.postVideo import post_video_tencent, post_video_DouYin, post_video_ks, post_video_xhs, post_image_xhs
import requests

active_queues = {}
app = Flask(__name__)

# 允许所有来源跨域访问
CORS(app)

# 限制上传文件大小为160MB
app.config['MAX_CONTENT_LENGTH'] = 160 * 1024 * 1024

# 获取当前目录（假设 index.html 和 assets 在这里）
current_dir = os.path.dirname(os.path.abspath(__file__))
# 前端构建输出目录
frontend_dist = os.path.join(current_dir, 'sau_frontend', 'dist')


def init_db():
    """初始化数据库，确保所有表存在"""
    db_path = Path(BASE_DIR / "db" / "database.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # 发布历史记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS publish_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform INTEGER NOT NULL,
                title TEXT NOT NULL,
                account_name TEXT,
                file_list TEXT,
                tags TEXT,
                status INTEGER DEFAULT 0,
                error_msg TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # 账号信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type INTEGER NOT NULL,
                filePath TEXT NOT NULL,
                userName TEXT NOT NULL,
                status INTEGER DEFAULT 0
            )
        ''')
        # 文件记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filesize REAL,
                upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT
            )
        ''')
        conn.commit()


init_db()

# 处理所有静态资源请求（未来打包用）
@app.route('/assets/<filename>')
def custom_static(filename):
    return send_from_directory(os.path.join(frontend_dist, 'assets'), filename)


@app.route('/videoFile/<filename>')
def serve_video_file(filename):
    """提供 videoFile 目录下的文件访问（图片/视频预览）"""
    video_dir = str(Path(BASE_DIR / "videoFile"))
    return send_from_directory(video_dir, filename)

# 处理 favicon.ico 静态资源（未来打包用）
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(frontend_dist, 'assets'), 'vite.svg')

@app.route('/vite.svg')
def vite_svg():
    return send_from_directory(os.path.join(frontend_dist, 'assets'), 'vite.svg')

# （未来打包用）
@app.route('/')
def index():  # put application's code here
    return send_from_directory(frontend_dist, 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({
            "code": 400,
            "data": None,
            "msg": "No file part in the request"
        }), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            "code": 400,
            "data": None,
            "msg": "No selected file"
        }), 400
    try:
        # 保存文件到指定位置
        uuid_v1 = uuid.uuid1()
        filename = f"{uuid_v1}_{file.filename}"
        filepath = Path(BASE_DIR / "videoFile" / filename)
        file.save(filepath)
        # 返回相对路径（供后续发布使用）和预览 URL
        return jsonify({
            "code": 200,
            "msg": "File uploaded successfully",
            "data": {
                "path": filename,
                "url": f"/videoFile/{filename}"
            }
        }), 200
    except Exception as e:
        return jsonify({"code":500,"msg": str(e),"data":None}), 500

@app.route('/getFile', methods=['GET'])
def get_file():
    # 获取 filename 参数
    filename = request.args.get('filename')

    if not filename:
        return jsonify({"code": 400, "msg": "filename is required", "data": None}), 400

    # 防止路径穿越攻击
    if '..' in filename or filename.startswith('/'):
        return jsonify({"code": 400, "msg": "Invalid filename", "data": None}), 400

    # 拼接完整路径
    file_path = str(Path(BASE_DIR / "videoFile"))

    # 返回文件
    return send_from_directory(file_path,filename)


@app.route('/uploadSave', methods=['POST'])
def upload_save():
    if 'file' not in request.files:
        return jsonify({
            "code": 400,
            "data": None,
            "msg": "No file part in the request"
        }), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({
            "code": 400,
            "data": None,
            "msg": "No selected file"
        }), 400

    # 获取表单中的自定义文件名（可选）
    custom_filename = request.form.get('filename', None)
    if custom_filename:
        filename = custom_filename + "." + file.filename.split('.')[-1]
    else:
        filename = file.filename

    try:
        # 生成 UUID v1
        uuid_v1 = uuid.uuid1()
        print(f"UUID v1: {uuid_v1}")

        # 构造文件名和路径
        final_filename = f"{uuid_v1}_{filename}"
        filepath = Path(BASE_DIR / "videoFile" / f"{uuid_v1}_{filename}")

        # 保存文件
        file.save(filepath)

        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                                INSERT INTO file_records (filename, filesize, file_path)
            VALUES (?, ?, ?)
                                ''', (filename, round(float(os.path.getsize(filepath)) / (1024 * 1024),2), final_filename))
            conn.commit()
            print("✅ 上传文件已记录")

        return jsonify({
            "code": 200,
            "msg": "File uploaded and saved successfully",
            "data": {
                "filename": filename,
                "filepath": final_filename
            }
        }), 200

    except Exception as e:
        print(f"Upload failed: {e}")
        return jsonify({
            "code": 500,
            "msg": f"upload failed: {e}",
            "data": None
        }), 500

@app.route('/getFiles', methods=['GET'])
def get_all_files():
    try:
        # 使用 with 自动管理数据库连接
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row  # 允许通过列名访问结果
            cursor = conn.cursor()

            # 查询所有记录
            cursor.execute("SELECT * FROM file_records")
            rows = cursor.fetchall()

            # 将结果转为字典列表，并提取UUID
            data = []
            for row in rows:
                row_dict = dict(row)
                # 从 file_path 中提取 UUID (文件名的第一部分，下划线前)
                if row_dict.get('file_path'):
                    file_path_parts = row_dict['file_path'].split('_', 1)  # 只分割第一个下划线
                    if len(file_path_parts) > 0:
                        row_dict['uuid'] = file_path_parts[0]  # UUID 部分
                    else:
                        row_dict['uuid'] = ''
                else:
                    row_dict['uuid'] = ''
                data.append(row_dict)

            return jsonify({
                "code": 200,
                "msg": "success",
                "data": data
            }), 200
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str("get file failed!"),
            "data": None
        }), 500


@app.route("/getAccounts", methods=['GET'])
def getAccounts():
    """快速获取所有账号信息，不进行cookie验证"""
    try:
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
            SELECT * FROM user_info''')
            rows = cursor.fetchall()
            rows_list = [list(row) for row in rows]

            # 避免终端编码问题（GBK）
            # print("\n当前数据表内容（快速获取）：")
            # for row in rows:
            #     print(row)

            return jsonify(
                {
                    "code": 200,
                    "msg": None,
                    "data": rows_list
                }), 200
    except Exception as e:
        # 避免控制台编码导致异常
        return jsonify({
            "code": 500,
            "msg": f"获取账号列表失败: {str(e)}",
            "data": None
        }), 500


@app.route("/getValidAccounts",methods=['GET'])
def getValidAccounts():
    import asyncio
    with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM user_info''')
        rows = cursor.fetchall()
        rows_list = [list(row) for row in rows]
        for row in rows_list:
            flag = asyncio.run(check_cookie(row[1],row[2]))
            if not flag:
                row[4] = 0
                cursor.execute('''
                UPDATE user_info 
                SET status = ? 
                WHERE id = ?
                ''', (0,row[0]))
                conn.commit()
        return jsonify(
                        {
                            "code": 200,
                            "msg": None,
                            "data": rows_list
                        }),200

@app.route('/deleteFile', methods=['GET'])
def delete_file():
    file_id = request.args.get('id')

    if not file_id or not file_id.isdigit():
        return jsonify({
            "code": 400,
            "msg": "Invalid or missing file ID",
            "data": None
        }), 400

    try:
        # 获取数据库连接
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 查询要删除的记录
            cursor.execute("SELECT * FROM file_records WHERE id = ?", (file_id,))
            record = cursor.fetchone()

            if not record:
                return jsonify({
                    "code": 404,
                    "msg": "File not found",
                    "data": None
                }), 404

            record = dict(record)

            # 获取文件路径并删除实际文件
            file_path = Path(BASE_DIR / "videoFile" / record['file_path'])
            if file_path.exists():
                try:
                    file_path.unlink()  # 删除文件
                    print(f"✅ 实际文件已删除: {file_path}")
                except Exception as e:
                    print(f"⚠️ 删除实际文件失败: {e}")
                    # 即使删除文件失败，也要继续删除数据库记录，避免数据不一致
            else:
                print(f"⚠️ 实际文件不存在: {file_path}")

            # 删除数据库记录
            cursor.execute("DELETE FROM file_records WHERE id = ?", (file_id,))
            conn.commit()

        return jsonify({
            "code": 200,
            "msg": "File deleted successfully",
            "data": {
                "id": record['id'],
                "filename": record['filename']
            }
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str("delete failed!"),
            "data": None
        }), 500

@app.route('/deleteAccount', methods=['GET'])
def delete_account():
    account_id = request.args.get('id')

    if not account_id or not account_id.isdigit():
        return jsonify({
            "code": 400,
            "msg": "Invalid or missing account ID",
            "data": None
        }), 400

    account_id = int(account_id)

    try:
        # 获取数据库连接
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 查询要删除的记录
            cursor.execute("SELECT * FROM user_info WHERE id = ?", (account_id,))
            record = cursor.fetchone()

            if not record:
                return jsonify({
                    "code": 404,
                    "msg": "account not found",
                    "data": None
                }), 404

            record = dict(record)

            # 删除关联的cookie文件
            if record.get('filePath'):
                cookie_file_path = Path(BASE_DIR / "cookiesFile" / record['filePath'])
                if cookie_file_path.exists():
                    try:
                        cookie_file_path.unlink()
                        print(f"✅ Cookie文件已删除: {cookie_file_path}")
                    except Exception as e:
                        print(f"⚠️ 删除Cookie文件失败: {e}")

            # 删除数据库记录
            cursor.execute("DELETE FROM user_info WHERE id = ?", (account_id,))
            conn.commit()

        return jsonify({
            "code": 200,
            "msg": "account deleted successfully",
            "data": None
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": f"delete failed: {str(e)}",
            "data": None
        }), 500


# SSE 登录接口
@app.route('/login')
def login():
    # 1 小红书 2 视频号 3 抖音 4 快手
    type = request.args.get('type')
    # 账号名
    id = request.args.get('id')

    # 模拟一个用于异步通信的队列
    status_queue = Queue()
    active_queues[id] = status_queue

    def on_close():
        print(f"清理队列: {id}")
        del active_queues[id]
    # 启动异步任务线程
    thread = threading.Thread(target=run_async_function, args=(type,id,status_queue), daemon=True)
    thread.start()
    response = Response(sse_stream(status_queue,), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'  # 关键：禁用 Nginx 缓冲
    response.headers['Content-Type'] = 'text/event-stream'
    response.headers['Connection'] = 'keep-alive'
    return response

@app.route('/postVideo', methods=['POST'])
def postVideo():
    # 获取JSON数据
    data = request.get_json()

    if not data:
        return jsonify({"code": 400, "msg": "请求数据不能为空", "data": None}), 400

    # 从JSON数据中提取fileList和accountList
    file_list = data.get('fileList', [])
    account_list = data.get('accountList', [])
    type = data.get('type')
    title = data.get('title')
    tags = data.get('tags')
    category = data.get('category')
    enableTimer = data.get('enableTimer')
    if category == 0:
        category = None
    productLink = data.get('productLink', '')
    productTitle = data.get('productTitle', '')
    thumbnail_path = data.get('thumbnail', '')
    is_draft = data.get('isDraft', False)  # 新增参数：是否保存为草稿

    videos_per_day = data.get('videosPerDay')
    start_days = data.get('startDays')

    # 将前端 ['10:00', '14:00'] 转为整数小时 [10, 14]（所有平台通用）
    def _parse_daily_times(times):
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

    daily_times = _parse_daily_times(data.get('dailyTimes'))

    # 参数校验
    if not file_list:
        return jsonify({"code": 400, "msg": "文件列表不能为空", "data": None}), 400
    if type != 1 and not account_list:
        return jsonify({"code": 400, "msg": "账号列表不能为空", "data": None}), 400
    if not type:
        return jsonify({"code": 400, "msg": "平台类型不能为空", "data": None}), 400
    if not title:
        return jsonify({"code": 400, "msg": "标题不能为空", "data": None}), 400

    import json as _json
    print("File List:", file_list)
    print("Account List:", account_list)

    try:
        if type == 1:
            post_video_xhs(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                               start_days)
        elif type == 2:
            post_video_tencent(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                               start_days, is_draft)
        elif type == 3:
            post_video_DouYin(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                      start_days, thumbnail_path, productLink, productTitle)
        elif type == 4:
            post_video_ks(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                      start_days)
        else:
            return jsonify({"code": 400, "msg": f"不支持的平台类型: {type}", "data": None}), 400

        # 写入发布历史
        try:
            with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO publish_history (platform, title, account_name, file_list, tags, status) VALUES (?,?,?,?,?,?)',
                    (type, title, _json.dumps(account_list, ensure_ascii=False),
                     _json.dumps(file_list, ensure_ascii=False),
                     _json.dumps(tags or [], ensure_ascii=False), 1)
                )
                conn.commit()
        except Exception as he:
            pass  # 避免 GBK 编码错误

        return jsonify({"code": 200, "msg": "发布任务已提交", "data": None}), 200
    except Exception as e:
        # 写入失败历史
        try:
            import json as _json2
            with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO publish_history (platform, title, account_name, file_list, tags, status, error_msg) VALUES (?,?,?,?,?,?,?)',
                    (type, title, _json2.dumps(account_list, ensure_ascii=False),
                     _json2.dumps(file_list, ensure_ascii=False),
                     _json2.dumps(tags or [], ensure_ascii=False), 0, str(e))
                )
                conn.commit()
        except Exception:
            pass
        return jsonify({"code": 500, "msg": f"发布失败: {str(e)}", "data": None}), 500


@app.route('/updateUserinfo', methods=['POST'])
def updateUserinfo():
    # 获取JSON数据
    data = request.get_json()

    # 从JSON数据中提取 type 和 userName
    user_id = data.get('id')
    type = data.get('type')
    userName = data.get('userName')
    try:
        # 获取数据库连接
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 更新数据库记录
            cursor.execute('''
                           UPDATE user_info
                           SET type     = ?,
                               userName = ?
                           WHERE id = ?;
                           ''', (type, userName, user_id))
            conn.commit()

        return jsonify({
            "code": 200,
            "msg": "account update successfully",
            "data": None
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str("update failed!"),
            "data": None
        }), 500

@app.route('/postVideoBatch', methods=['POST'])
def postVideoBatch():
    import json as _json
    data_list = request.get_json()

    if not isinstance(data_list, list):
        return jsonify({"code": 400, "msg": "Expected a JSON array", "data": None}), 400

    for data in data_list:
        file_list = data.get('fileList', [])
        account_list = data.get('accountList', [])
        type = data.get('type')
        title = data.get('title')
        tags = data.get('tags')
        category = data.get('category')
        enableTimer = data.get('enableTimer')
        if category == 0:
            category = None
        productLink = data.get('productLink', '')
        productTitle = data.get('productTitle', '')
        is_draft = data.get('isDraft', False)
        videos_per_day = data.get('videosPerDay')
        daily_times_raw = data.get('dailyTimes')
        start_days = data.get('startDays')

        # 将前端 ['10:00', '14:00'] 转为整数小时 [10, 14]
        def _parse_times(times):
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

        daily_times = _parse_times(daily_times_raw)

        status = 1
        error_msg = None
        try:
            if type == 1:
                post_video_xhs(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times, start_days)
            elif type == 2:
                post_video_tencent(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times, start_days, is_draft)
            elif type == 3:
                post_video_DouYin(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times, start_days, productLink, productTitle)
            elif type == 4:
                post_video_ks(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times, start_days)
        except Exception as e:
            status = 0
            error_msg = str(e)
            print(f"批量发布失败: {e}")

        # 写入发布历史
        try:
            with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO publish_history (platform, title, account_name, file_list, tags, status, error_msg) VALUES (?,?,?,?,?,?,?)',
                    (type, title or '',
                     _json.dumps(account_list, ensure_ascii=False),
                     _json.dumps(file_list, ensure_ascii=False),
                     _json.dumps(tags or [], ensure_ascii=False),
                     status, error_msg)
                )
                conn.commit()
        except Exception as he:
            print(f"写入批量发布历史失败: {he}")

    return jsonify({"code": 200, "msg": None, "data": None}), 200

# Cookie文件上传API
@app.route('/uploadCookie', methods=['POST'])
def upload_cookie():
    try:
        if 'file' not in request.files:
            return jsonify({
                "code": 400,
                "msg": "没有找到Cookie文件",
                "data": None
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "code": 400,
                "msg": "Cookie文件名不能为空",
                "data": None
            }), 400

        if not file.filename.endswith('.json'):
            return jsonify({
                "code": 400,
                "msg": "Cookie文件必须是JSON格式",
                "data": None
            }), 400

        # 获取账号信息
        account_id = request.form.get('id')
        platform = request.form.get('platform')

        if not account_id or not platform:
            return jsonify({
                "code": 400,
                "msg": "缺少账号ID或平台信息",
                "data": None
            }), 400

        # 从数据库获取账号的文件路径
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT filePath FROM user_info WHERE id = ?', (account_id,))
            result = cursor.fetchone()

        if not result:
            return jsonify({
                "code": 500,
                "msg": "账号不存在",
                "data": None
            }), 404

        # 保存上传的Cookie文件到对应路径
        cookie_file_path = Path(BASE_DIR / "cookiesFile" / result['filePath'])
        cookie_file_path.parent.mkdir(parents=True, exist_ok=True)

        file.save(str(cookie_file_path))

        # 更新数据库中的账号信息（可选，比如更新更新时间）
        # 这里可以根据需要添加额外的处理逻辑

        return jsonify({
            "code": 200,
            "msg": "Cookie文件上传成功",
            "data": None
        }), 200

    except Exception as e:
        print(f"上传Cookie文件时出错: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"上传Cookie文件失败: {str(e)}",
            "data": None
        }), 500


# Cookie文件下载API
@app.route('/downloadCookie', methods=['GET'])
def download_cookie():
    try:
        file_path = request.args.get('filePath')
        if not file_path:
            return jsonify({
                "code": 500,
                "msg": "缺少文件路径参数",
                "data": None
            }), 400

        # 验证文件路径的安全性，防止路径遍历攻击
        cookie_file_path = Path(BASE_DIR / "cookiesFile" / file_path).resolve()
        base_path = Path(BASE_DIR / "cookiesFile").resolve()

        if not cookie_file_path.is_relative_to(base_path):
            return jsonify({
                "code": 500,
                "msg": "非法文件路径",
                "data": None
            }), 400

        if not cookie_file_path.exists():
            return jsonify({
                "code": 500,
                "msg": "Cookie文件不存在",
                "data": None
            }), 404

        # 返回文件
        return send_from_directory(
            directory=str(cookie_file_path.parent),
            path=cookie_file_path.name,
            as_attachment=True
        )

    except Exception as e:
        print(f"下载Cookie文件时出错: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"下载Cookie文件失败: {str(e)}",
            "data": None
        }), 500


# 包装函数：在线程中运行异步函数
def run_async_function(type, id, status_queue):
    if type == '1':
        # 小红书已改为 MCP 登录，旧 Playwright 流程不再使用
        # 直接推送提示，让前端知道应该用 /xhs/mcp/login
        status_queue.put('{"code": 400, "msg": "小红书请使用 MCP 扫码登录"}')
    elif type == '2':
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(get_tencent_cookie(id, status_queue))
        loop.close()
    elif type == '3':
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(douyin_cookie_gen(id, status_queue))
        loop.close()
    elif type == '4':
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(get_ks_cookie(id, status_queue))
        loop.close()

# SSE 流生成器函数
def sse_stream(status_queue):
    while True:
        if not status_queue.empty():
            msg = status_queue.get()
            yield f"data: {msg}\n\n"
        else:
            # 避免 CPU 占满
            time.sleep(0.1)


# ==================== 小红书 MCP 接口 ====================

def _get_mcp_url_by_account(account_name):
    """根据账号名获取 MCP URL"""
    return XHS_MCP_ACCOUNTS.get(account_name, XHS_MCP_URL)


def _call_mcp(mcp_url, path, method='GET', json=None, timeout=10):
    """通用 MCP 请求封装，附带错误提示"""
    try:
        if method == 'GET':
            resp = requests.get(f"{mcp_url}{path}", timeout=timeout)
        else:
            resp = requests.post(f"{mcp_url}{path}", json=json, timeout=timeout)
        resp.raise_for_status()
        return resp.json(), None
    except requests.exceptions.HTTPError as e:
        # 5xx 也算服务在线（未登录时 MCP 返回 500），尝试解析响应体
        if e.response is not None and e.response.status_code >= 500:
            try:
                return e.response.json(), None
            except Exception:
                return {}, None
        return None, str(e)
    except requests.exceptions.ConnectionError:
        return None, f"无法连接到小红书 MCP 服务 ({mcp_url})，请先启动服务：cd D:\\xiaohongshu-mcp && go run . --port {mcp_url.split(':')[-1]}"
    except requests.exceptions.Timeout:
        return None, f"请求小红书 MCP 超时 ({mcp_url})"
    except Exception as e:
        return None, str(e)


@app.route('/xhs/mcp/status', methods=['GET'])
def xhs_mcp_status():
    """检查所有小红书 MCP 实例的状态"""
    result = {}
    for name, url in XHS_MCP_ACCOUNTS.items():
        data, err = _call_mcp(url, '/api/v1/login/status', timeout=60)
        if err:
            result[name] = {"url": url, "online": False, "logged_in": False, "error": err}
        else:
            logged_in = data.get("data", {}).get("is_logged_in", False)
            username = data.get("data", {}).get("username", "")
            result[name] = {"url": url, "online": True, "logged_in": logged_in, "username": username}

    return jsonify({"code": 200, "msg": "success", "data": result})


@app.route('/xhs/mcp/login', methods=['GET'])
def xhs_mcp_login():
    """
    SSE 接口：获取指定 MCP 账号的登录二维码并轮询登录结果
    ?account=账号A
    前端监听 SSE，收到 data:image... 显示二维码，收到 200 表示成功，500 表示失败
    """
    account_name = request.args.get('account', '')
    mcp_url = _get_mcp_url_by_account(account_name) if account_name else XHS_MCP_URL

    def generate():
        # 1. 获取二维码
        data, err = _call_mcp(mcp_url, '/api/v1/login/qrcode', timeout=10)
        if err:
            yield f"data: 500\n\n"
            return

        if data.get("data", {}).get("is_logged_in"):
            yield f"data: 200\n\n"
            return

        img = data.get("data", {}).get("img", "")
        if not img:
            yield f"data: 500\n\n"
            return

        # 2. 推送二维码图片
        yield f"data: {img}\n\n"

        # 3. 轮询登录状态（最多 3 分钟）
        for _ in range(180):
            time.sleep(1)
            status_data, err = _call_mcp(mcp_url, '/api/v1/login/status', timeout=5)
            if err:
                continue
            if status_data.get("data", {}).get("is_logged_in"):
                # 登录成功，写入数据库
                try:
                    with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                        cursor = conn.cursor()
                        # 检查是否已存在
                        cursor.execute('SELECT id FROM user_info WHERE userName = ? AND type = 1', (account_name,))
                        if not cursor.fetchone():
                            file_path = f"xhs_mcp_{account_name}.json"
                            cursor.execute(
                                'INSERT INTO user_info (type, filePath, userName, status) VALUES (?, ?, ?, ?)',
                                (1, file_path, account_name, 1)
                            )
                            conn.commit()
                        else:
                            cursor.execute(
                                'UPDATE user_info SET status = 1 WHERE userName = ? AND type = 1',
                                (account_name,)
                            )
                            conn.commit()
                except Exception as e:
                    print(f"写入数据库失败: {e}")
                yield f"data: 200\n\n"
                return

        yield f"data: 500\n\n"

    return Response(generate(), mimetype='text/event-stream',
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route('/xhs/mcp/accounts', methods=['GET'])
def xhs_mcp_accounts():
    """获取 MCP 账号配置列表"""
    accounts = []
    for name, url in XHS_MCP_ACCOUNTS.items():
        accounts.append({"name": name, "url": url})
    return jsonify({"code": 200, "msg": "success", "data": accounts})


# MCP 进程管理（key: account_name, value: subprocess.Popen）
_mcp_processes = {}


@app.route('/xhs/mcp/start', methods=['POST'])
def xhs_mcp_start():
    """启动指定账号的 MCP 服务"""
    import subprocess
    data = request.get_json() or {}
    account_name = data.get('account', '')
    mcp_url = _get_mcp_url_by_account(account_name) if account_name else XHS_MCP_URL
    port = mcp_url.split(':')[-1].split('/')[0]

    if account_name in _mcp_processes and _mcp_processes[account_name].poll() is None:
        return jsonify({"code": 200, "msg": f"MCP 服务已在运行 (port {port})", "data": None})

    mcp_dir = r'D:\xiaohongshu-mcp'
    try:
        proc = subprocess.Popen(
            ['go', 'run', '.', '--port', port],
            cwd=mcp_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        _mcp_processes[account_name] = proc
        return jsonify({"code": 200, "msg": f"MCP 服务已启动 (port {port}, pid {proc.pid})", "data": {"pid": proc.pid, "port": port}})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"启动失败: {str(e)}", "data": None}), 500


@app.route('/xhs/mcp/stop', methods=['POST'])
def xhs_mcp_stop():
    """停止指定账号的 MCP 服务"""
    data = request.get_json() or {}
    account_name = data.get('account', '')

    proc = _mcp_processes.get(account_name)
    if proc and proc.poll() is None:
        proc.terminate()
        _mcp_processes.pop(account_name, None)
        return jsonify({"code": 200, "msg": "MCP 服务已停止", "data": None})
    return jsonify({"code": 200, "msg": "MCP 服务未在运行", "data": None})


@app.route('/postImage', methods=['POST'])
def post_image():
    """图文发布接口（小红书专用）"""
    import json as _json
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据不能为空", "data": None}), 400

    file_list = data.get('fileList', [])
    account_list = data.get('accountList', [])
    title = data.get('title')
    tags = data.get('tags', [])

    if not file_list:
        return jsonify({"code": 400, "msg": "图片列表不能为空", "data": None}), 400
    if not title:
        return jsonify({"code": 400, "msg": "标题不能为空", "data": None}), 400

    try:
        post_image_xhs(title, file_list, tags, account_list)

        # 写入发布历史
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO publish_history (platform, title, account_name, file_list, tags, status) VALUES (?,?,?,?,?,?)',
                (1, title, _json.dumps(account_list, ensure_ascii=False),
                 _json.dumps(file_list, ensure_ascii=False),
                 _json.dumps(tags, ensure_ascii=False), 1)
            )
            conn.commit()

        return jsonify({"code": 200, "msg": "图文发布任务已提交", "data": None}), 200
    except Exception as e:
        # 写入失败历史
        try:
            with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO publish_history (platform, title, account_name, file_list, tags, status, error_msg) VALUES (?,?,?,?,?,?,?)',
                    (1, title, _json.dumps(account_list, ensure_ascii=False),
                     _json.dumps(file_list, ensure_ascii=False),
                     _json.dumps(tags, ensure_ascii=False), 0, str(e))
                )
                conn.commit()
        except Exception:
            pass
        print(f"发布图文时出错: {str(e)}")
        return jsonify({"code": 500, "msg": f"发布失败: {str(e)}", "data": None}), 500


@app.route('/publishHistory', methods=['GET'])
def get_publish_history():
    """获取发布历史记录"""
    import json as _json
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 20))
    platform = request.args.get('platform')
    status = request.args.get('status')
    offset = (page - 1) * page_size

    try:
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            conditions = []
            params = []
            if platform:
                conditions.append('platform = ?')
                params.append(int(platform))
            if status is not None and status != '':
                conditions.append('status = ?')
                params.append(int(status))

            where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''

            cursor.execute(f'SELECT COUNT(*) FROM publish_history {where}', params)
            total = cursor.fetchone()[0]

            cursor.execute(
                f'SELECT * FROM publish_history {where} ORDER BY created_at DESC LIMIT ? OFFSET ?',
                params + [page_size, offset]
            )
            rows = cursor.fetchall()

        platform_map = {1: '小红书', 2: '视频号', 3: '抖音', 4: '快手'}
        result = []
        for row in rows:
            result.append({
                'id': row['id'],
                'platform': platform_map.get(row['platform'], str(row['platform'])),
                'platformType': row['platform'],
                'title': row['title'],
                'accountName': _json.loads(row['account_name'] or '[]'),
                'fileList': _json.loads(row['file_list'] or '[]'),
                'tags': _json.loads(row['tags'] or '[]'),
                'status': row['status'],
                'statusText': '成功' if row['status'] == 1 else '失败',
                'errorMsg': row['error_msg'],
                'createdAt': row['created_at']
            })

        return jsonify({"code": 200, "msg": "success", "data": {"list": result, "total": total}}), 200
    except Exception as e:
        return jsonify({"code": 500, "msg": str(e), "data": None}), 500


@app.route('/xhs/mcp/config', methods=['GET'])
def xhs_mcp_config_get():
    """获取 XHS MCP 账号配置"""
    accounts = [{"name": k, "url": v} for k, v in XHS_MCP_ACCOUNTS.items()]
    return jsonify({"code": 200, "msg": "success", "data": {
        "accounts": accounts,
        "defaultUrl": XHS_MCP_URL
    }})


@app.route('/xhs/mcp/config', methods=['POST'])
def xhs_mcp_config_save():
    """保存 XHS MCP 账号配置到 conf.py"""
    import re
    data = request.get_json() or {}
    accounts = data.get('accounts', [])  # [{"name": "账号A", "url": "http://..."}]
    default_url = data.get('defaultUrl', 'http://localhost:8080')

    if not accounts:
        return jsonify({"code": 400, "msg": "账号列表不能为空", "data": None}), 400

    # 生成新的配置内容
    accounts_dict = {item['name']: item['url'] for item in accounts if item.get('name') and item.get('url')}
    accounts_str = '{\n' + ''.join(f'    "{k}": "{v}",\n' for k, v in accounts_dict.items()) + '}'

    conf_path = Path(BASE_DIR / "conf.py")
    try:
        content = conf_path.read_text(encoding='utf-8')
        # 替换 XHS_MCP_ACCOUNTS
        content = re.sub(
            r'XHS_MCP_ACCOUNTS\s*=\s*\{[^}]*\}',
            f'XHS_MCP_ACCOUNTS = {accounts_str}',
            content, flags=re.DOTALL
        )
        # 替换 XHS_MCP_URL
        content = re.sub(
            r'XHS_MCP_URL\s*=\s*["\'][^"\']*["\']',
            f'XHS_MCP_URL = "{default_url}"',
            content
        )
        conf_path.write_text(content, encoding='utf-8')

        # 热更新内存中的配置
        import conf as _conf
        import importlib
        importlib.reload(_conf)
        from conf import XHS_MCP_ACCOUNTS as new_accounts, XHS_MCP_URL as new_url

        # 同步更新 sau_backend 自身的全局变量
        import sys
        _this = sys.modules[__name__]
        _this.XHS_MCP_ACCOUNTS = new_accounts
        _this.XHS_MCP_URL = new_url

        # 同步更新 postVideo 模块
        import myUtils.postVideo as _pv
        _pv.XHS_MCP_ACCOUNTS = new_accounts
        _pv.XHS_MCP_URL = new_url

        return jsonify({"code": 200, "msg": "配置已保存，重启后完全生效", "data": None})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"保存失败: {str(e)}", "data": None}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5409)
