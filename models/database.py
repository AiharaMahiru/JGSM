"""
数据库连接和初始化模块
"""
import os
import sqlite3
import logging
from pathlib import Path

from config.database import TABLES

logger = logging.getLogger(__name__)

class Database:
    """数据库管理类，负责数据库连接和初始化"""
    
    def __init__(self, config):
        """
        初始化数据库连接
        
        参数:
            config (dict): 数据库配置字典
        """
        self.config = config
        # 确保数据目录存在
        os.makedirs(os.path.dirname(config['name']), exist_ok=True)
        
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = sqlite3.connect(
                self.config['name'],
                timeout=self.config.get('timeout', 15),
                isolation_level=self.config.get('isolation_level')
            )
            # 启用外键约束
            self.connection.execute("PRAGMA foreign_keys = ON")
            # 设置行工厂为字典，使查询结果以字典形式返回
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            logger.info(f"成功连接到数据库: {self.config['name']}")
            return True
        except sqlite3.Error as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("数据库连接已关闭")
    
    def commit(self):
        """提交事务"""
        if self.connection:
            self.connection.commit()
    
    def rollback(self):
        """回滚事务"""
        if self.connection:
            self.connection.rollback()
    
    def execute(self, sql, params=None):
        """执行SQL语句"""
        try:
            if params:
                return self.cursor.execute(sql, params)
            else:
                return self.cursor.execute(sql)
        except sqlite3.Error as e:
            logger.error(f"SQL执行错误: {e}, SQL: {sql}, 参数: {params}")
            raise
    
    def fetchone(self):
        """获取一条查询结果"""
        return self.cursor.fetchone()
    
    def fetchall(self):
        """获取所有查询结果"""
        return self.cursor.fetchall()
    
    def init_database(self):
        """初始化数据库表结构"""
        if not self.connect():
            logger.error("无法连接到数据库，初始化失败")
            return False
            
        try:
            # 创建学生表
            self.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLES['students']} (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                gender TEXT CHECK(gender IN ('男', '女', '其他')),
                birth_date TEXT,
                class_name TEXT,
                admission_date TEXT,
                contact_phone TEXT,
                email TEXT,
                address TEXT,
                status TEXT DEFAULT '在读' CHECK(status IN ('在读', '休学', '退学', '毕业')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建课程表
            self.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLES['courses']} (
                course_id TEXT PRIMARY KEY,
                course_name TEXT NOT NULL,
                credit REAL NOT NULL,
                teacher TEXT,
                description TEXT,
                semester TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建成绩表
            self.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLES['grades']} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_id TEXT NOT NULL,
                semester TEXT NOT NULL,
                score REAL CHECK(score >= 0 AND score <= 100),
                grade_point REAL,
                exam_date TEXT,
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES {TABLES['students']}(student_id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES {TABLES['courses']}(course_id) ON DELETE CASCADE,
                UNIQUE(student_id, course_id, semester)
            )
            ''')
            
            # 创建用户表
            self.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLES['users']} (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                real_name TEXT,
                role TEXT NOT NULL CHECK(role IN ('admin', 'teacher', 'student', 'guest')),
                email TEXT,
                phone TEXT,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建操作日志表
            self.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLES['logs']} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                operation TEXT NOT NULL,
                target TEXT,
                details TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建默认管理员账户
            self.execute(f'''
            INSERT OR IGNORE INTO {TABLES['users']} (username, password, real_name, role)
            VALUES (?, ?, ?, ?)
            ''', ('admin', 'pbkdf2:sha256:150000$xtR9ZGgI$f9b8a88aad54f3a5b7d197ebc3a1a92a0f4b53ad6b276fe6bf0782fcd7e9965a', '系统管理员', 'admin'))
            
            self.commit()
            logger.info("数据库表结构初始化完成")
            return True
        except sqlite3.Error as e:
            self.rollback()
            logger.error(f"数据库初始化失败: {e}")
            return False