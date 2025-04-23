"""
用户控制器模块
"""
import logging
import re
from datetime import datetime

from controllers.base_controller import BaseController
from models.user import User
from models.log import Log

logger = logging.getLogger(__name__)

class UserController(BaseController):
    """用户控制器类，处理用户认证和权限管理"""
    
    def __init__(self, db, current_user=None):
        """
        初始化用户控制器
        
        参数:
            db (Database): 数据库实例
            current_user (dict): 当前用户信息
        """
        super().__init__(db, current_user)
        self.user_model = User(self.db)
    
    def login(self, username, password):
        """
        用户登录
        
        参数:
            username (str): 用户名
            password (str): 密码
        
        返回:
            dict: 响应结果
        """
        # 验证用户凭据
        user = self.user_model.authenticate(username, password)
        
        if user:
            # 记录登录日志
            log_model = Log(self.db)
            log_model.add_log({
                'username': username,
                'operation': '用户登录',
                'details': f"用户 {username} 登录成功"
            })
            
            # 移除敏感信息
            if 'password' in user:
                del user['password']
            
            return self.format_response(True, data=user, message="登录成功")
        else:
            return self.format_response(False, message="用户名或密码错误")
    
    def add_user(self, user_data):
        """
        添加新用户
        
        参数:
            user_data (dict): 用户信息
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin'):
            return self.format_response(False, message="权限不足，需要管理员权限")
        
        # 验证必填字段
        required_fields = ['username', 'password', 'role']
        valid, error_message = self.validate_required_fields(user_data, required_fields)
        if not valid:
            return self.format_response(False, message=error_message)
        
        # 验证用户名格式
        if not self._validate_username(user_data['username']):
            return self.format_response(False, message="用户名格式不正确，应为字母、数字和下划线的组合，长度在3-20之间")
        
        # 验证密码强度
        if not self._validate_password(user_data['password']):
            return self.format_response(False, message="密码强度不足，应包含字母和数字，长度至少为6位")
        
        # 验证角色是否有效
        valid_roles = ['admin', 'teacher', 'student', 'guest']
        if user_data['role'] not in valid_roles:
            return self.format_response(False, message=f"无效的角色，有效角色为: {', '.join(valid_roles)}")
        
        # 添加用户
        success = self.user_model.add_user(user_data)
        
        if success:
            # 记录操作日志
            self.log_operation(
                operation="添加用户",
                target=f"用户: {user_data['username']}",
                details=f"添加了用户 {user_data['username']}，角色: {user_data['role']}"
            )
            return self.format_response(True, message=f"成功添加用户: {user_data['username']}")
        else:
            return self.format_response(False, message="添加用户失败，可能是用户名已存在")
    
    def update_user(self, username, update_data):
        """
        更新用户信息
        
        参数:
            username (str): 用户名
            update_data (dict): 更新的用户信息
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin') and (self.username != username):
            return self.format_response(False, message="权限不足，只能修改自己的信息或需要管理员权限")
        
        # 检查用户是否存在
        user = self.user_model.get_user(username)
        if not user:
            return self.format_response(False, message=f"未找到用户名为 {username} 的用户")
        
        # 普通用户不能修改自己的角色
        if 'role' in update_data and self.user_role != 'admin':
            return self.format_response(False, message="权限不足，无法修改用户角色")
        
        # 验证密码强度
        if 'password' in update_data and not self._validate_password(update_data['password']):
            return self.format_response(False, message="密码强度不足，应包含字母和数字，长度至少为6位")
        
        # 验证角色是否有效
        if 'role' in update_data:
            valid_roles = ['admin', 'teacher', 'student', 'guest']
            if update_data['role'] not in valid_roles:
                return self.format_response(False, message=f"无效的角色，有效角色为: {', '.join(valid_roles)}")
        
        # 更新用户信息
        success = self.user_model.update_user(username, update_data)
        
        if success:
            # 记录操作日志
            self.log_operation(
                operation="更新用户信息",
                target=f"用户: {username}",
                details=f"更新了用户 {username} 的信息"
            )
            return self.format_response(True, message=f"成功更新用户信息: {username}")
        else:
            return self.format_response(False, message="更新用户信息失败")
    
    def delete_user(self, username):
        """
        删除用户
        
        参数:
            username (str): 用户名
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin'):
            return self.format_response(False, message="权限不足，需要管理员权限")
        
        # 不能删除自己
        if self.username == username:
            return self.format_response(False, message="不能删除当前登录的用户")
        
        # 检查用户是否存在
        user = self.user_model.get_user(username)
        if not user:
            return self.format_response(False, message=f"未找到用户名为 {username} 的用户")
        
        # 删除用户
        success = self.user_model.delete_user(username)
        
        if success:
            # 记录操作日志
            self.log_operation(
                operation="删除用户",
                target=f"用户: {username}",
                details=f"删除了用户 {username}"
            )
            return self.format_response(True, message=f"成功删除用户: {username}")
        else:
            return self.format_response(False, message="删除用户失败")
    
    def get_user(self, username):
        """
        获取用户信息
        
        参数:
            username (str): 用户名
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin') and (self.username != username):
            return self.format_response(False, message="权限不足，只能查看自己的信息或需要管理员权限")
        
        # 获取用户信息
        user = self.user_model.get_user(username)
        
        if user:
            return self.format_response(True, data=user)
        else:
            return self.format_response(False, message=f"未找到用户名为 {username} 的用户")
    
    def get_all_users(self, filters=None, page=1, page_size=20):
        """
        获取用户列表
        
        参数:
            filters (dict, optional): 过滤条件
            page (int): 页码
            page_size (int): 每页大小
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin'):
            return self.format_response(False, message="权限不足，需要管理员权限")
        
        try:
            # 处理过滤条件
            role = None
            if filters and 'role' in filters:
                role = filters['role']
            
            # 获取用户总数
            users = self.user_model.get_all_users(role)
            total = len(users)
            
            # 计算分页参数
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            # 分页处理
            paginated_users = users[start_idx:end_idx] if start_idx < total else []
            
            # 构建分页结果
            pagination = {
                'items': paginated_users,
                'page': page,
                'page_size': page_size,
                'total_items': total,
                'total_pages': (total + page_size - 1) // page_size
            }
            
            return self.format_response(True, data=pagination)
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return self.format_response(False, message=f"获取用户列表失败: {str(e)}")
    
    def change_password(self, username, old_password, new_password):
        """
        修改密码
        
        参数:
            username (str): 用户名
            old_password (str): 旧密码
            new_password (str): 新密码
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('student') and (self.username != username):
            return self.format_response(False, message="权限不足，只能修改自己的密码或需要管理员权限")
        
        # 验证密码强度
        if not self._validate_password(new_password):
            return self.format_response(False, message="密码强度不足，应包含字母和数字，长度至少为6位")
        
        # 修改密码
        success = self.user_model.change_password(username, old_password, new_password)
        
        if success:
            # 记录操作日志
            self.log_operation(
                operation="修改密码",
                target=f"用户: {username}",
                details=f"修改了用户 {username} 的密码"
            )
            return self.format_response(True, message="密码修改成功")
        else:
            return self.format_response(False, message="密码修改失败，可能是旧密码错误")
    
    def reset_password(self, username, new_password):
        """
        重置密码（管理员功能）
        
        参数:
            username (str): 用户名
            new_password (str): 新密码
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin'):
            return self.format_response(False, message="权限不足，需要管理员权限")
        
        # 检查用户是否存在
        user = self.user_model.get_user(username)
        if not user:
            return self.format_response(False, message=f"未找到用户名为 {username} 的用户")
        
        # 验证密码强度
        if not self._validate_password(new_password):
            return self.format_response(False, message="密码强度不足，应包含字母和数字，长度至少为6位")
        
        # 更新密码
        update_data = {
            'password': new_password,
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        success = self.user_model.update_user(username, update_data)
        
        if success:
            # 记录操作日志
            self.log_operation(
                operation="重置密码",
                target=f"用户: {username}",
                details=f"重置了用户 {username} 的密码"
            )
            return self.format_response(True, message=f"成功重置用户 {username} 的密码")
        else:
            return self.format_response(False, message="重置密码失败")
    
    def _validate_username(self, username):
        """
        验证用户名格式
        
        参数:
            username (str): 用户名
        
        返回:
            bool: 格式正确返回True，否则返回False
        """
        # 用户名应为字母、数字和下划线的组合，长度在3-20之间
        pattern = r'^[A-Za-z0-9_]{3,20}$'
        return bool(re.match(pattern, username))
    
    def _validate_password(self, password):
        """
        验证密码强度
        
        参数:
            password (str): 密码
        
        返回:
            bool: 强度足够返回True，否则返回False
        """
        # 密码应包含字母和数字，长度至少为6位
        if len(password) < 6:
            return False
        
        # 检查是否包含字母
        if not re.search(r'[A-Za-z]', password):
            return False
        
        # 检查是否包含数字
        if not re.search(r'[0-9]', password):
            return False
        
        return True