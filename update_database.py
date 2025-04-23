"""
更新数据库表结构的脚本
"""
import os
import sqlite3
from pathlib import Path

# 获取数据库文件路径
DB_PATH = os.path.join(Path(__file__).parent, 'data', 'student_management.db')

def update_courses_table():
    """更新courses表，添加semester字段"""
    print(f"正在连接数据库: {DB_PATH}")
    
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 开始事务
        conn.execute("BEGIN TRANSACTION")
        
        # 检查courses表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='courses'")
        if not cursor.fetchone():
            print("courses表不存在，无需更新")
            return
        
        print("正在更新courses表结构...")
        
        # 创建临时表，包含所有需要的列
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses_temp (
            course_id TEXT PRIMARY KEY,
            course_name TEXT NOT NULL,
            credit REAL NOT NULL,
            teacher TEXT,
            description TEXT,
            semester TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 将旧表中的数据复制到临时表
        cursor.execute("""
        INSERT INTO courses_temp (course_id, course_name, credit, teacher, description, created_at, updated_at)
        SELECT course_id, course_name, credit, teacher, description, created_at, updated_at FROM courses
        """)
        
        # 删除旧表
        cursor.execute("DROP TABLE courses")
        
        # 将临时表重命名为原表名
        cursor.execute("ALTER TABLE courses_temp RENAME TO courses")
        
        # 提交事务
        conn.commit()
        print("courses表更新成功，已添加semester字段")
        
    except sqlite3.Error as e:
        # 发生错误时回滚事务
        if conn:
            conn.rollback()
        print(f"更新数据库时发生错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()

if __name__ == "__main__":
    update_courses_table()