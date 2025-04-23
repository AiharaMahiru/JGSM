"""
基础视图模块
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseView:
    """基础视图类，定义视图的基本接口和方法"""
    
    def __init__(self, controllers=None, db=None):
        """
        初始化基础视图
        
        参数:
            controllers (dict): 控制器字典，键为控制器名称，值为控制器实例
            db (Database): 数据库实例
        """
        self.controllers = controllers or {}
        self.current_user = None
        self.db = db
    
    def run(self):
        """启动视图界面"""
        raise NotImplementedError("子类必须实现此方法")
    
    def set_current_user(self, user):
        """
        设置当前用户，并同步更新控制器实例中的用户信息
        
        参数:
            user (dict): 用户信息
        """
        logger.debug(f"Setting current user in BaseView: {user}")
        self.current_user = user
        
        # 同步更新所有控制器实例的 current_user
        if self.controllers:
            for controller_name, controller_instance in self.controllers.items():
                if hasattr(controller_instance, 'current_user'):
                    logger.debug(f"Updating current_user for controller: {controller_name}")
                    controller_instance.current_user = user
                    controller_instance.username = user.get('username') if user else None
                    controller_instance.user_role = user.get('role') if user else None
                else:
                    logger.warning(f"Controller {controller_name} does not have 'current_user' attribute.")
    
    def get_current_user(self):
        """
        获取当前用户
        
        返回:
            dict: 当前用户信息
        """
        return self.current_user
    
    def get_system_info(self):
        """
        获取系统信息
        
        返回:
            dict: 系统信息
        """
        return {
            'name': '学生管理系统',
            'version': '1.0.0',
            'author': '开发团队',
            'copyright': f'© {datetime.now().year} 版权所有'
        }