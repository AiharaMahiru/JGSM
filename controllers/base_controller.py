"""
基础控制器模块
"""
import logging
from datetime import datetime

from models.database import Database
from models.log import Log
from models.user import User

logger = logging.getLogger(__name__)

class BaseController:
    """基础控制器类，提供通用功能和权限控制"""
    
    def __init__(self, db, current_user=None):
        """
        初始化基础控制器
        
        参数:
            db (Database): 数据库实例
            current_user (dict): 当前用户信息
        """
        # 设置数据库连接
        self.db = db
        
        # 初始化日志模型
        self.log_model = Log(self.db)
        
        # 设置当前用户
        self.current_user = current_user
        self.username = current_user.get('username') if current_user else None
        self.user_role = current_user.get('role') if current_user else None
        logger.debug(f"BaseController initialized with current_user: {self.current_user}")
    
    def __del__(self):
        """析构函数，确保数据库连接关闭"""
        # 注意：不再在这里关闭数据库连接，因为连接由main.py管理
        pass
    
    def check_permission(self, required_role):
        """
        检查当前用户是否具有所需权限
        
        参数:
            required_role (str): 所需角色
        
        返回:
            bool: 具有权限返回True，否则返回False
        """
        logger.debug(f"Checking permission for user: {self.current_user}, required role: {required_role}")
        if not self.current_user:
            logger.warning("权限检查失败: 未登录用户 (self.current_user is None)")
            return False
        
        user_model = User(self.db)
        return user_model.check_permission(self.username, required_role)
    
    def log_operation(self, operation, target=None, details=None):
        """
        记录操作日志
        
        参数:
            operation (str): 操作类型
            target (str): 操作目标
            details (str): 详细信息
        
        返回:
            bool: 记录成功返回True，否则返回False
        """
        log_data = {
            'username': self.username,
            'operation': operation,
            'target': target,
            'details': details
        }
        
        return self.log_model.add_log(log_data)
    
    def format_response(self, success, data=None, message=None):
        """
        格式化响应数据
        
        参数:
            success (bool): 操作是否成功
            data: 响应数据
            message (str): 响应消息
        
        返回:
            dict: 格式化的响应字典
        """
        return {
            'success': success,
            'data': data,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def validate_required_fields(self, data, required_fields):
        """
        验证必填字段
        
        参数:
            data (dict): 待验证的数据
            required_fields (list): 必填字段列表
        
        返回:
            tuple: (是否通过验证, 错误消息)
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                missing_fields.append(field)
        
        if missing_fields:
            error_message = f"缺少必填字段: {', '.join(missing_fields)}"
            return False, error_message
        
        return True, None
    
    def paginate(self, items, page=1, page_size=20):
        """
        对列表进行分页
        
        参数:
            items (list): 待分页的列表
            page (int): 页码，从1开始
            page_size (int): 每页大小
        
        返回:
            dict: 分页结果
        """
        # 确保页码和页大小为正整数
        page = max(1, page)
        page_size = max(1, page_size)
        
        # 计算总页数
        total_items = len(items)
        total_pages = (total_items + page_size - 1) // page_size
        
        # 计算当前页的起始和结束索引
        start_index = (page - 1) * page_size
        end_index = min(start_index + page_size, total_items)
        
        # 获取当前页的数据
        current_page_items = items[start_index:end_index]
        
        return {
            'items': current_page_items,
            'page': page,
            'page_size': page_size,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_previous': page > 1,
            'has_next': page < total_pages
        }