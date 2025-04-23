"""
日志控制器模块
"""
import logging
from datetime import datetime

from controllers.base_controller import BaseController
from models.log import Log

logger = logging.getLogger(__name__)

class LogController(BaseController):
    """日志控制器类，处理系统日志管理"""
    
    def __init__(self, db, current_user=None):
        """
        初始化日志控制器
        
        参数:
            db (Database): 数据库实例
            current_user (dict): 当前用户信息
        """
        super().__init__(db, current_user)
        self.log_model = Log(self.db)
    
    def get_logs(self, filters=None, page=1, page_size=50):
        """
        获取系统日志
        
        参数:
            filters (dict): 过滤条件
            page (int): 页码
            page_size (int): 每页大小
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin'):
            return self.format_response(False, message="权限不足，需要管理员权限")
        
        # 计算分页参数
        offset = (page - 1) * page_size
        
        # 获取日志记录
        logs = self.log_model.get_logs(filters, page_size, offset)
        
        # 构建分页结果
        pagination = {
            'items': logs,
            'page': page,
            'page_size': page_size,
            'has_more': len(logs) == page_size
        }
        
        return self.format_response(True, data=pagination)
    
    def search_logs(self, keyword, start_date=None, end_date=None, page=1, page_size=50):
        """
        搜索系统日志
        
        参数:
            keyword (str): 搜索关键词
            start_date (str): 开始日期，格式为'YYYY-MM-DD'
            end_date (str): 结束日期，格式为'YYYY-MM-DD'
            page (int): 页码
            page_size (int): 每页大小
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin'):
            return self.format_response(False, message="权限不足，需要管理员权限")
        
        # 计算分页参数
        offset = (page - 1) * page_size
        
        # 搜索日志记录
        logs = self.log_model.search_logs(keyword, start_date, end_date, page_size, offset)
        
        # 构建分页结果
        pagination = {
            'items': logs,
            'page': page,
            'page_size': page_size,
            'has_more': len(logs) == page_size,
            'keyword': keyword,
            'start_date': start_date,
            'end_date': end_date
        }
        
        return self.format_response(True, data=pagination)
    
    def get_user_activity(self, username, limit=50):
        """
        获取用户活动记录
        
        参数:
            username (str): 用户名
            limit (int): 限制返回记录数
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin') and (self.username != username):
            return self.format_response(False, message="权限不足，只能查看自己的活动记录或需要管理员权限")
        
        # 获取用户活动记录
        logs = self.log_model.get_user_activity(username, limit)
        
        return self.format_response(True, data=logs)
    
    def get_operation_stats(self, days=30):
        """
        获取操作统计信息
        
        参数:
            days (int): 统计的天数
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin'):
            return self.format_response(False, message="权限不足，需要管理员权限")
        
        # 获取操作统计信息
        stats = self.log_model.get_operation_stats(days)
        
        return self.format_response(True, data=stats)
    
    def clear_old_logs(self, days=365):
        """
        清除旧日志记录
        
        参数:
            days (int): 保留的天数，默认保留一年的日志
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin'):
            return self.format_response(False, message="权限不足，需要管理员权限")
        
        # 清除旧日志记录
        cleared_count = self.log_model.clear_old_logs(days)
        
        # 记录操作日志
        self.log_operation(
            operation="清除旧日志",
            details=f"清除了 {cleared_count} 条超过 {days} 天的旧日志记录"
        )
        
        return self.format_response(True, message=f"成功清除 {cleared_count} 条旧日志记录")
        
    def get_user_logs(self, username, page=1, page_size=20):
        """
        获取用户日志记录（支持分页）
        
        参数:
            username (str): 用户名
            page (int): 页码
            page_size (int): 每页大小
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin') and (self.username != username):
            return self.format_response(False, message="权限不足，只能查看自己的日志记录或需要管理员权限")
        
        try:
            # 构建过滤条件
            filters = {'username': username}
            
            # 计算分页参数
            offset = (page - 1) * page_size
            
            # 获取日志记录
            logs = self.log_model.get_logs(filters, page_size, offset)
            
            # 获取总记录数
            total_count = self.log_model.count_logs(filters)
            
            # 构建分页结果
            pagination = {
                'items': logs,
                'page': page,
                'page_size': page_size,
                'total_items': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
            
            return self.format_response(True, data=pagination)
        except Exception as e:
            logger.error(f"获取用户日志记录失败: {e}")
            return self.format_response(False, message=f"获取用户日志记录失败: {str(e)}")