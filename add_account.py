import sqlite3
conn = sqlite3.connect('D:/social-auto-upload/db/database.db')
conn.execute("INSERT OR REPLACE INTO user_info (type, filePath, userName, status) VALUES (1, 'xhs_mcp_诺斯马丁实况.json', '诺斯马丁实况', 1)")
conn.commit()
conn.close()
print('账号已添加到数据库')
