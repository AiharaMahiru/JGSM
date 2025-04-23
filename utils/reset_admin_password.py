"""
重置管理员密码工具
"""
import os
import sys
import sqlite3
import hashlib

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import TABLES
from config.settings import DATABASE_CONFIG

def hash_password(password):
    """对密码进行哈希处理"""
    salt = "xtR9ZGgI"
    iterations = 150000
    
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
    hashed = f"pbkdf2:sha256:{iterations}${salt}${dk.hex()}"
    
    return hashed

def reset_admin_password(new_password="admin123"):
    """重置管理员密码为指定值"""
    try:
        # 连接数据库
        db_path = DATABASE_CONFIG['name']
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 生成新密码的哈希值
        hashed_password = hash_password(new_password)
        
        # 更新管理员密码
        cursor.execute(f"UPDATE {TABLES['users']} SET password = ? WHERE username = ?", 
                      (hashed_password, "admin"))
        
        # 提交更改
        conn.commit()
        
        # 关闭连接
        conn.close()
        
        print(f"管理员密码已重置为: {new_password}")
        return True
    except Exception as e:
        print(f"重置密码失败: {e}")
        return False

if __name__ == "__main__":
    # 默认重置密码为 admin123
    reset_admin_password()