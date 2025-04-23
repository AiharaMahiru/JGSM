"""
用户模型模块
"""
import logging
import sqlite3
import hashlib
import os
from datetime import datetime

from config.database import TABLES
from config.settings import PERMISSION_LEVELS
from models.database import Database

logger = logging.getLogger(__name__)

class User:
    """用户模型类，处理用户账户管理和权限验证"""
    
    def __init__(self, db=None):
        """初始化用户模型"""
        self.db = db if db else Database()
        if not hasattr(self.db, 'connection') or self.db.connection is None:
            self.db.connect()
    
    def add_user(self, user_data):
        """
        添加新用户
        
        参数:
            user_data (dict): 用户信息字典，包含以下字段:
                - username: 用户名
                - password: 密码
                - real_name: 真实姓名（可选）
                - role: 角色（admin/teacher/student/guest）
        
        返回:
            bool: 添加成功返回True，否则返回False
        """
        try:
            # 验证必填字段
            if not user_data.get('username') or not user_data.get('password') or not user_data.get('role'):
                logger.error("添加用户失败: 用户名、密码和角色为必填项")
                return False
            
            # 验证角色是否有效
            if user_data.get('role') not in PERMISSION_LEVELS:
                logger.error(f"添加用户失败: 无效的角色 {user_data.get('role')}")
                return False
            
            # 对密码进行哈希处理
            user_data['password'] = self._hash_password(user_data['password'])
            
            # 准备SQL语句和参数
            fields = ', '.join(user_data.keys())
            placeholders = ', '.join(['?'] * len(user_data))
            values = list(user_data.values())
            
            # 执行插入操作
            sql = f"INSERT INTO {TABLES['users']} ({fields}) VALUES ({placeholders})"
            self.db.execute(sql, values)
            self.db.commit()
            
            logger.info(f"成功添加用户: {user_data['username']} (角色: {user_data['role']})")
            return True
        except sqlite3.IntegrityError:
            self.db.rollback()
            logger.error(f"添加用户失败: 用户名 {user_data.get('username')} 已存在")
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"添加用户失败: {e}")
            return False
    
    def update_user(self, username, update_data):
        """
        更新用户信息
        
        参数:
            username (str): 用户名
            update_data (dict): 需要更新的字段和值
        
        返回:
            bool: 更新成功返回True，否则返回False
        """
        try:
            if not update_data:
                logger.warning("更新用户信息失败: 没有提供更新数据")
                return False
            
            # 如果更新密码，对密码进行哈希处理
            if 'password' in update_data:
                update_data['password'] = self._hash_password(update_data['password'])
            
            # 验证角色是否有效
            if 'role' in update_data and update_data['role'] not in PERMISSION_LEVELS:
                logger.error(f"更新用户信息失败: 无效的角色 {update_data.get('role')}")
                return False
            
            # 添加更新时间
            update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 准备SQL语句和参数
            set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(username)  # WHERE子句的参数
            
            # 执行更新操作
            sql = f"UPDATE {TABLES['users']} SET {set_clause} WHERE username = ?"
            self.db.execute(sql, values)
            self.db.commit()
            
            # 检查是否有记录被更新
            if self.db.cursor.rowcount > 0:
                logger.info(f"成功更新用户信息: {username}")
                return True
            else:
                logger.warning(f"更新用户信息失败: 未找到用户名为 {username} 的用户")
                return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新用户信息失败: {e}")
            return False
    
    def delete_user(self, username):
        """
        删除用户
        
        参数:
            username (str): 用户名
        
        返回:
            bool: 删除成功返回True，否则返回False
        """
        try:
            # 执行删除操作
            sql = f"DELETE FROM {TABLES['users']} WHERE username = ?"
            self.db.execute(sql, (username,))
            self.db.commit()
            
            # 检查是否有记录被删除
            if self.db.cursor.rowcount > 0:
                logger.info(f"成功删除用户: {username}")
                return True
            else:
                logger.warning(f"删除用户失败: 未找到用户名为 {username} 的用户")
                return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除用户失败: {e}")
            return False
    
    def get_user(self, username):
        """
        获取用户信息
        
        参数:
            username (str): 用户名
        
        返回:
            dict: 用户信息字典，未找到返回None
        """
        try:
            sql = f"SELECT * FROM {TABLES['users']} WHERE username = ?"
            self.db.execute(sql, (username,))
            user = self.db.fetchone()
            
            if user:
                # 将Row对象转换为字典
                user_dict = dict(user)
                # 出于安全考虑，移除密码字段
                if 'password' in user_dict:
                    del user_dict['password']
                return user_dict
            else:
                logger.warning(f"未找到用户名为 {username} 的用户")
                return None
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    def get_all_users(self, role=None):
        """
        获取用户列表
        
        参数:
            role (str, optional): 角色过滤，如果提供则只返回该角色的用户
        
        返回:
            list: 用户信息字典列表
        """
        try:
            # 构建基本SQL
            sql = f"SELECT username, real_name, role, last_login, created_at, updated_at FROM {TABLES['users']}"
            params = []
            
            # 如果提供了角色，添加角色过滤条件
            if role:
                sql += " WHERE role = ?"
                params.append(role)
            
            # 添加排序
            sql += " ORDER BY username"
            
            # 执行查询
            self.db.execute(sql, params)
            users = self.db.fetchall()
            
            # 将Row对象列表转换为字典列表
            return [dict(user) for user in users]
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return []
    
    def authenticate(self, username, password):
        """
        验证用户凭据
        
        参数:
            username (str): 用户名
            password (str): 密码
        
        返回:
            dict: 验证成功返回用户信息字典，失败返回None
        """
        try:
            # 获取用户信息
            sql = f"SELECT * FROM {TABLES['users']} WHERE username = ?"
            self.db.execute(sql, (username,))
            user = self.db.fetchone()
            
            if not user:
                logger.warning(f"认证失败: 用户名 {username} 不存在")
                return None
            
            # 验证密码
            hashed_password = self._hash_password(password)
            if user['password'] != hashed_password:
                logger.warning(f"认证失败: 用户 {username} 密码错误")
                return None
            
            # 更新最后登录时间
            self.update_last_login(username)
            
            # 返回用户信息（不包含密码）
            user_dict = dict(user)
            del user_dict['password']
            
            logger.info(f"用户 {username} 认证成功")
            return user_dict
        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            return None
    
    def update_last_login(self, username):
        """
        更新用户最后登录时间
        
        参数:
            username (str): 用户名
        
        返回:
            bool: 更新成功返回True，否则返回False
        """
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = f"UPDATE {TABLES['users']} SET last_login = ? WHERE username = ?"
            self.db.execute(sql, (now, username))
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新最后登录时间失败: {e}")
            return False
    
    def check_permission(self, username, required_role):
        """
        检查用户是否具有指定角色的权限
        
        参数:
            username (str): 用户名
            required_role (str): 所需角色
        
        返回:
            bool: 具有权限返回True，否则返回False
        """
        try:
            # 获取用户角色
            sql = f"SELECT role FROM {TABLES['users']} WHERE username = ?"
            self.db.execute(sql, (username,))
            user = self.db.fetchone()
            
            if not user:
                logger.warning(f"权限检查失败: 用户 {username} 不存在")
                return False
            
            user_role = user['role']
            
            # 获取用户角色和所需角色的权限级别
            user_level = PERMISSION_LEVELS.get(user_role, 0)
            required_level = PERMISSION_LEVELS.get(required_role, 0)
            
            # 检查用户权限级别是否大于等于所需权限级别
            has_permission = user_level >= required_level
            
            if not has_permission:
                logger.warning(f"权限不足: 用户 {username} (角色: {user_role}) 尝试执行需要 {required_role} 权限的操作")
            
            return has_permission
        except Exception as e:
            logger.error(f"权限检查失败: {e}")
            return False
    
    def change_password(self, username, old_password, new_password):
        """
        修改用户密码
        
        参数:
            username (str): 用户名
            old_password (str): 旧密码
            new_password (str): 新密码
        
        返回:
            bool: 修改成功返回True，否则返回False
        """
        try:
            # 验证旧密码
            sql = f"SELECT password FROM {TABLES['users']} WHERE username = ?"
            self.db.execute(sql, (username,))
            user = self.db.fetchone()
            
            if not user:
                logger.warning(f"修改密码失败: 用户 {username} 不存在")
                return False
            
            hashed_old_password = self._hash_password(old_password)
            if user['password'] != hashed_old_password:
                logger.warning(f"修改密码失败: 用户 {username} 旧密码错误")
                return False
            
            # 更新密码
            hashed_new_password = self._hash_password(new_password)
            update_data = {
                'password': hashed_new_password,
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            sql = f"UPDATE {TABLES['users']} SET password = ?, updated_at = ? WHERE username = ?"
            self.db.execute(sql, (update_data['password'], update_data['updated_at'], username))
            self.db.commit()
            
            logger.info(f"用户 {username} 成功修改密码")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"修改密码失败: {e}")
            return False
    
    def _hash_password(self, password):
        """
        对密码进行哈希处理
        
        参数:
            password (str): 原始密码
        
        返回:
            str: 哈希后的密码
        """
        # 使用PBKDF2算法进行密码哈希
        salt = "xtR9ZGgI"  # 在实际应用中应该为每个密码生成唯一的盐值
        iterations = 150000
        
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
        hashed = f"pbkdf2:sha256:{iterations}${salt}${dk.hex()}"
        
        return hashed