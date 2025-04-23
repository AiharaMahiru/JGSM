"""
系统全局配置模块
"""
import os
import logging
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 日志配置
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'system.log')
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 系统配置
SYSTEM_NAME = "学生管理系统"
VERSION = "1.0.0"

# 权限级别
PERMISSION_LEVELS = {
    'admin': 3,    # 管理员权限
    'teacher': 2,  # 教师权限
    'student': 1,  # 学生权限
    'guest': 0     # 访客权限
}

# 数据导出配置
EXPORT_DIR = os.path.join(BASE_DIR, 'data', 'exports')
SUPPORTED_EXPORT_FORMATS = ['csv', 'excel', 'pdf']

# 日志配置字典
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': LOG_FORMAT
        },
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    },
}

# 数据库配置
DATABASE_CONFIG = {
    'type': 'sqlite',
    'name': os.path.join(BASE_DIR, 'data', 'student_management.db'),
    'create_if_not_exists': True,
    'timeout': 15,
    'isolation_level': None,  # 自动提交
}