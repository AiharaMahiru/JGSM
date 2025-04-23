"""
日志模型模块
"""
import logging
import sqlite3
from datetime import datetime
import socket

from config.database import TABLES
from models.database import Database

logger = logging.getLogger(__name__)

class Log:
    """日志模型类，处理系统操作日志记录和查询"""
    
    def __init__(self, db=None):
        """初始化日志模型"""
        self.db = db if db else Database()
        if not hasattr(self.db, 'connection') or self.db.connection is None:
            self.db.connect()
    
    def add_log(self, log_data):
        """
        添加新日志记录
        
        参数:
            log_data (dict): 日志信息字典，包含以下字段:
                - username: 用户名
                - operation: 操作类型
                - target: 操作目标（可选）
                - details: 详细信息（可选）
                - ip_address: IP地址（可选，如果不提供则自动获取）
        
        返回:
            bool: 添加成功返回True，否则返回False
        """
        try:
            # 验证必填字段
            if not log_data.get('operation'):
                logger.error("添加日志失败: 操作类型为必填项")
                return False
            
            # 如果没有提供IP地址，尝试获取本机IP
            if 'ip_address' not in log_data:
                try:
                    hostname = socket.gethostname()
                    log_data['ip_address'] = socket.gethostbyname(hostname)
                except:
                    log_data['ip_address'] = '127.0.0.1'
            
            # 准备SQL语句和参数
            fields = ', '.join(log_data.keys())
            placeholders = ', '.join(['?'] * len(log_data))
            values = list(log_data.values())
            
            # 执行插入操作
            sql = f"INSERT INTO {TABLES['logs']} ({fields}) VALUES ({placeholders})"
            self.db.execute(sql, values)
            self.db.commit()
            
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"添加日志失败: {e}")
            return False
    
    def get_logs(self, filters=None, limit=100, offset=0):
        """
        获取日志记录
        
        参数:
            filters (dict): 过滤条件，如 {'username': 'admin', 'operation': 'login'}
            limit (int): 限制返回记录数
            offset (int): 偏移量
        
        返回:
            list: 日志记录字典列表
        """
        try:
            # 构建基本SQL
            sql = f"SELECT * FROM {TABLES['logs']}"
            params = []
            
            # 添加过滤条件
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
                
                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)
            
            # 添加排序
            sql += " ORDER BY timestamp DESC"
            
            # 添加分页
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            # 执行查询
            self.db.execute(sql, params)
            logs = self.db.fetchall()
            
            # 将Row对象列表转换为字典列表
            return [dict(log) for log in logs]
        except Exception as e:
            logger.error(f"获取日志记录失败: {e}")
            return []
    
    def search_logs(self, keyword, start_date=None, end_date=None, limit=100, offset=0):
        """
        搜索日志记录
        
        参数:
            keyword (str): 搜索关键词
            start_date (str): 开始日期，格式为'YYYY-MM-DD'
            end_date (str): 结束日期，格式为'YYYY-MM-DD'
            limit (int): 限制返回记录数
            offset (int): 偏移量
        
        返回:
            list: 匹配的日志记录字典列表
        """
        try:
            # 构建基本SQL
            sql = f"""
            SELECT * FROM {TABLES['logs']} 
            WHERE (username LIKE ? OR operation LIKE ? OR target LIKE ? OR details LIKE ?)
            """
            pattern = f"%{keyword}%"
            params = [pattern, pattern, pattern, pattern]
            
            # 添加日期范围条件
            if start_date:
                sql += " AND timestamp >= ?"
                params.append(f"{start_date} 00:00:00")
            
            if end_date:
                sql += " AND timestamp <= ?"
                params.append(f"{end_date} 23:59:59")
            
            # 添加排序
            sql += " ORDER BY timestamp DESC"
            
            # 添加分页
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            # 执行查询
            self.db.execute(sql, params)
            logs = self.db.fetchall()
            
            # 将Row对象列表转换为字典列表
            return [dict(log) for log in logs]
        except Exception as e:
            logger.error(f"搜索日志记录失败: {e}")
            return []
    
    def get_user_activity(self, username, limit=50):
        """
        获取用户活动记录
        
        参数:
            username (str): 用户名
            limit (int): 限制返回记录数
        
        返回:
            list: 用户活动记录字典列表
        """
        try:
            sql = f"""
            SELECT * FROM {TABLES['logs']} 
            WHERE username = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """
            self.db.execute(sql, (username, limit))
            logs = self.db.fetchall()
            
            # 将Row对象列表转换为字典列表
            return [dict(log) for log in logs]
        except Exception as e:
            logger.error(f"获取用户活动记录失败: {e}")
            return []
    
    def get_operation_stats(self, days=30):
        """
        获取操作统计信息
        
        参数:
            days (int): 统计的天数
        
        返回:
            dict: 操作统计信息字典
        """
        try:
            # 获取操作类型统计
            sql = f"""
            SELECT operation, COUNT(*) as count
            FROM {TABLES['logs']}
            WHERE timestamp >= datetime('now', '-{days} days')
            GROUP BY operation
            ORDER BY count DESC
            """
            self.db.execute(sql)
            operation_stats = self.db.fetchall()
            
            # 获取用户活跃度统计
            sql = f"""
            SELECT username, COUNT(*) as count
            FROM {TABLES['logs']}
            WHERE timestamp >= datetime('now', '-{days} days')
            GROUP BY username
            ORDER BY count DESC
            LIMIT 10
            """
            self.db.execute(sql)
            user_stats = self.db.fetchall()
            
            # 获取每日操作数量统计
            sql = f"""
            SELECT date(timestamp) as date, COUNT(*) as count
            FROM {TABLES['logs']}
            WHERE timestamp >= datetime('now', '-{days} days')
            GROUP BY date(timestamp)
            ORDER BY date
            """
            self.db.execute(sql)
            daily_stats = self.db.fetchall()
            
            return {
                'operation_stats': [dict(stat) for stat in operation_stats],
                'user_stats': [dict(stat) for stat in user_stats],
                'daily_stats': [dict(stat) for stat in daily_stats]
            }
        except Exception as e:
            logger.error(f"获取操作统计信息失败: {e}")
            return {
                'operation_stats': [],
                'user_stats': [],
                'daily_stats': []
            }
    
    def clear_old_logs(self, days=365):
        """
        清除旧日志记录
        
        参数:
            days (int): 保留的天数，默认保留一年的日志
        
        返回:
            int: 清除的记录数
        """
        try:
            sql = f"""
            DELETE FROM {TABLES['logs']}
            WHERE timestamp < datetime('now', '-{days} days')
            """
            self.db.execute(sql)
            self.db.commit()
            
            cleared_count = self.db.cursor.rowcount
            logger.info(f"成功清除 {cleared_count} 条旧日志记录")
            return cleared_count
        except Exception as e:
            self.db.rollback()
            logger.error(f"清除旧日志记录失败: {e}")
            return 0