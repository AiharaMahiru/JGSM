"""
命令行界面视图模块
"""
import os
import sys
import logging
import getpass
from datetime import datetime

from views.base_view import BaseView
from controllers.student_controller import StudentController
from controllers.course_controller import CourseController
from controllers.grade_controller import GradeController
from controllers.user_controller import UserController
from controllers.log_controller import LogController

logger = logging.getLogger(__name__)

class CommandLineView(BaseView):
    """命令行界面视图类，实现命令行交互"""
    
    def __init__(self, controllers=None, db=None):
        """
        初始化命令行界面视图
        
        参数:
            controllers (dict): 控制器字典
            db (Database): 数据库实例
        """
        super().__init__(controllers, db)
        self.running = False
    
    def run(self):
        """启动命令行界面"""
        self.running = True
        self.clear_screen()
        self.show_welcome()
        
        # 如果没有控制器，初始化控制器
        if not self.controllers:
            self.init_controllers()
        
        # 登录
        if not self.show_login():
            self.exit()
            return
        
        # 主循环
        while self.running:
            self.show_main_menu()
        
        self.show_goodbye()
    
    def init_controllers(self):
        """初始化控制器"""
        if not self.db:
            logger.error("数据库实例未初始化，无法创建控制器")
            return
            
        self.controllers = {
            'student': StudentController(self.db),
            'course': CourseController(self.db),
            'grade': GradeController(self.db),
            'user': UserController(self.db),
            'log': LogController(self.db)
        }
    
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_welcome(self):
        """显示欢迎信息"""
        system_info = self.get_system_info()
        
        self.clear_screen()
        print("=" * 60)
        print(f"欢迎使用 {system_info['name']} v{system_info['version']}")
        print("=" * 60)
        print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()
    
    def show_goodbye(self):
        """显示再见信息"""
        self.clear_screen()
        print("=" * 60)
        print("感谢使用学生管理系统，再见！")
        print("=" * 60)
    
    def show_login(self):
        """
        显示登录界面
        
        返回:
            bool: 登录成功返回True，否则返回False
        """
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            print("\n登录系统")
            print("-" * 20)
            
            username = input("用户名: ").strip()
            if not username:
                print("用户名不能为空！")
                continue
            
            password = getpass.getpass("密码: ")
            if not password:
                print("密码不能为空！")
                continue
            
            # 验证用户凭据
            user_controller = self.controllers.get('user')
            if not user_controller:
                if not self.db:
                    logger.error("数据库实例未初始化，无法创建用户控制器")
                    return False
                user_controller = UserController(self.db)
                self.controllers['user'] = user_controller
            
            result = user_controller.login(username, password)
            
            if result['success']:
                self.set_current_user(result['data'])
                logger.debug(f"Login successful. Current user set in view: {self.current_user}")
                self.show_message(f"欢迎回来，{result['data'].get('real_name') or username}！", "success")
                return True
            else:
                attempts += 1
                remaining = max_attempts - attempts
                if remaining > 0:
                    self.show_message(f"{result['message']}，还有 {remaining} 次尝试机会。", "error")
                else:
                    self.show_message(f"{result['message']}，登录失败！", "error")
        
        return False
    
    def show_main_menu(self):
        """显示主菜单"""
        self.clear_screen()
        self.show_header("主菜单")
        
        # 根据用户角色显示不同的菜单选项
        role = self.current_user.get('role', 'guest')
        
        menu_options = [
            {"key": "1", "text": "学生管理", "roles": ["admin", "teacher"]},
            {"key": "2", "text": "课程管理", "roles": ["admin", "teacher"]},
            {"key": "3", "text": "成绩管理", "roles": ["admin", "teacher"]},
            {"key": "4", "text": "用户管理", "roles": ["admin"]},
            {"key": "5", "text": "系统日志", "roles": ["admin"]},
            {"key": "6", "text": "个人信息", "roles": ["admin", "teacher", "student", "guest"]},
            {"key": "7", "text": "修改密码", "roles": ["admin", "teacher", "student", "guest"]},
            {"key": "0", "text": "退出系统", "roles": ["admin", "teacher", "student", "guest"]}
        ]
        
        # 显示菜单选项
        for option in menu_options:
            if role in option["roles"]:
                print(f"{option['key']}. {option['text']}")
        
        print()
        choice = input("请选择操作 [0-7]: ").strip()
        
        # 处理用户选择
        if choice == "1" and role in ["admin", "teacher"]:
            self.show_student_management()
        elif choice == "2" and role in ["admin", "teacher"]:
            self.show_course_management()
        elif choice == "3" and role in ["admin", "teacher"]:
            self.show_grade_management()
        elif choice == "4" and role in ["admin"]:
            self.show_user_management()
        elif choice == "5" and role in ["admin"]:
            self.show_system_logs()
        elif choice == "6":
            self.show_personal_info()
        elif choice == "7":
            self.show_change_password()
        elif choice == "0":
            self.exit()
        else:
            self.show_message("无效的选择，请重新输入！", "warning")
            input("\n按回车键继续...")
    
    def show_header(self, title):
        """
        显示页面标题
        
        参数:
            title (str): 页面标题
        """
        system_info = self.get_system_info()
        print("=" * 60)
        print(f"{system_info['name']} - {title}")
        print("=" * 60)
        print(f"当前用户: {self.current_user.get('real_name') or self.current_user.get('username')} ({self.current_user.get('role')})")
        print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        print()
    
    def show_message(self, message, message_type='info'):
        """
        显示消息
        
        参数:
            message (str): 消息内容
            message_type (str): 消息类型，可选值：info, success, warning, error
        """
        if message_type == 'info':
            print(f"\n信息: {message}")
        elif message_type == 'success':
            print(f"\n成功: {message}")
        elif message_type == 'warning':
            print(f"\n警告: {message}")
        elif message_type == 'error':
            print(f"\n错误: {message}")
        else:
            print(f"\n{message}")
    
    def show_confirmation(self, message):
        """
        显示确认对话框
        
        参数:
            message (str): 确认消息
        
        返回:
            bool: 用户确认返回True，取消返回False
        """
        while True:
            choice = input(f"\n{message} (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            else:
                print("请输入 y 或 n")
    
    def exit(self):
        """退出系统"""
        if self.show_confirmation("确定要退出系统吗?"):
            self.running = False
