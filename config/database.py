"""
数据库配置模块
"""
import os
from pathlib import Path

# 数据库文件路径
DB_PATH = os.path.join(Path(__file__).parent.parent, 'data', 'student_management.db')

# 数据库表名
TABLES = {
    'students': 'students',
    'courses': 'courses',
    'grades': 'grades',
    'users': 'users',
    'logs': 'operation_logs'
}