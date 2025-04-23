"""
命令行界面用户管理视图模块
"""
import os
import logging
import getpass
from datetime import datetime

logger = logging.getLogger(__name__)

class CLIUserView:
    """命令行界面用户管理视图类"""
    
    def __init__(self, cli_view, user_controller):
        """
        初始化用户管理视图
        
        参数:
            cli_view: 命令行界面视图实例
            user_controller: 用户控制器实例
        """
        self.cli_view = cli_view
        self.user_controller = user_controller
    
    def show_user_management(self):
        """显示用户管理界面"""
        while True:
            self.cli_view.clear_screen()
            self.cli_view.show_header("用户管理")
            
            print("1. 查看用户列表")
            print("2. 添加新用户")
            print("3. 修改用户信息")
            print("4. 删除用户")
            print("5. 重置用户密码")
            print("0. 返回主菜单")
            print()
            
            choice = input("请选择操作 [0-5]: ").strip()
            
            if choice == "1":
                self.show_user_list()
            elif choice == "2":
                self.show_add_user()
            elif choice == "3":
                self.show_edit_user()
            elif choice == "4":
                self.show_delete_user()
            elif choice == "5":
                self.show_reset_password()
            elif choice == "0":
                break
            else:
                self.cli_view.show_message("无效的选择，请重新输入！", "warning")
                input("\n按回车键继续...")
    
    def show_user_list(self, role=None):
        """
        显示用户列表
        
        参数:
            role (str, optional): 角色过滤
        """
        self.cli_view.clear_screen()
        self.cli_view.show_header("用户列表")
        
        # 获取用户列表
        result = self.user_controller.get_all_users(role)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        users = result['data']
        
        if not users:
            self.cli_view.show_message("没有找到用户记录！", "info")
            input("\n按回车键继续...")
            return
        
        # 显示用户列表
        print(f"{'用户名':<15} {'角色':<10} {'真实姓名':<15} {'创建时间':<20}")
        print("-" * 60)
        
        for user in users:
            print(f"{user['username']:<15} {user.get('role', ''):<10} {user.get('real_name', ''):<15} {user.get('created_at', ''):<20}")
        
        # 操作选项
        print("\n[F] 筛选  [V] 查看详情  [0] 返回")
        choice = input("\n请选择操作: ").strip().lower()
        
        if choice == 'f':
            self.show_filter_users()
        elif choice == 'v':
            username = input("请输入要查看的用户名: ").strip()
            self.show_user_details(username)
        elif choice == '0':
            return
        else:
            self.show_user_list(role)
    
    def show_user_details(self, username):
        """
        显示用户详情
        
        参数:
            username (str): 用户名
        """
        self.cli_view.clear_screen()
        self.cli_view.show_header("用户详情")
        
        # 获取用户信息
        result = self.user_controller.get_user(username)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        user = result['data']
        
        # 显示用户详情
        print(f"用户名: {user['username']}")
        print(f"角色: {user.get('role', '未设置')}")
        print(f"真实姓名: {user.get('real_name', '未设置')}")
        print(f"电子邮箱: {user.get('email', '未设置')}")
        print(f"联系电话: {user.get('phone', '未设置')}")
        print(f"最后登录时间: {user.get('last_login', '未登录')}")
        print(f"创建时间: {user.get('created_at', '未知')}")
        print(f"更新时间: {user.get('updated_at', '未知')}")
        
        input("\n按回车键继续...")
    
    def show_add_user(self):
        """显示添加用户界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("添加新用户")
        
        # 收集用户信息
        user_data = {}
        
        user_data['username'] = input("用户名 (必填): ").strip()
        if not user_data['username']:
            self.cli_view.show_message("用户名不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        password = getpass.getpass("密码 (必填): ")
        if not password:
            self.cli_view.show_message("密码不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        confirm_password = getpass.getpass("确认密码: ")
        if password != confirm_password:
            self.cli_view.show_message("两次输入的密码不一致！", "error")
            input("\n按回车键继续...")
            return
        
        user_data['password'] = password
        
        print("\n选择用户角色:")
        print("1. 管理员 (admin)")
        print("2. 教师 (teacher)")
        print("3. 学生 (student)")
        print("4. 访客 (guest)")
        
        role_choice = input("\n请选择角色 [1-4]: ").strip()
        
        if role_choice == "1":
            user_data['role'] = "admin"
        elif role_choice == "2":
            user_data['role'] = "teacher"
        elif role_choice == "3":
            user_data['role'] = "student"
        elif role_choice == "4":
            user_data['role'] = "guest"
        else:
            self.cli_view.show_message("无效的角色选择！", "error")
            input("\n按回车键继续...")
            return
        
        real_name = input("真实姓名: ").strip()
        if real_name:
            user_data['real_name'] = real_name
        
        email = input("电子邮箱: ").strip()
        if email:
            user_data['email'] = email
        
        phone = input("联系电话: ").strip()
        if phone:
            user_data['phone'] = phone
        
        # 确认添加
        print("\n用户信息:")
        for key, value in user_data.items():
            if key != 'password':
                print(f"{key}: {value}")
        
        if not self.cli_view.show_confirmation("确认添加该用户?"):
            self.cli_view.show_message("已取消添加用户！", "info")
            input("\n按回车键继续...")
            return
        
        # 添加用户
        result = self.user_controller.add_user(user_data)
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")
    
    def show_edit_user(self):
        """显示修改用户信息界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("修改用户信息")
        
        # 输入用户名
        username = input("请输入要修改的用户名: ").strip()
        if not username:
            self.cli_view.show_message("用户名不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取用户信息
        result = self.user_controller.get_user(username)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        user = result['data']
        
        # 显示当前信息
        print("\n当前用户信息:")
        for key, value in user.items():
            if key not in ['password', 'created_at', 'updated_at']:
                print(f"{key}: {value}")
        
        print("\n请输入新的信息（不修改的项目直接回车）:")
        
        # 收集更新信息
        update_data = {}
        
        # 如果当前用户是管理员，可以修改角色
        if self.cli_view.current_user.get('role') == 'admin':
            print("\n选择用户角色:")
            print(f"当前角色: {user.get('role', '未设置')}")
            print("1. 管理员 (admin)")
            print("2. 教师 (teacher)")
            print("3. 学生 (student)")
            print("4. 访客 (guest)")
            print("0. 不修改")
            
            role_choice = input("\n请选择角色 [0-4]: ").strip()
            
            if role_choice == "1":
                update_data['role'] = "admin"
            elif role_choice == "2":
                update_data['role'] = "teacher"
            elif role_choice == "3":
                update_data['role'] = "student"
            elif role_choice == "4":
                update_data['role'] = "guest"
        
        real_name = input(f"真实姓名 [{user.get('real_name', '')}]: ").strip()
        if real_name:
            update_data['real_name'] = real_name
        
        email = input(f"电子邮箱 [{user.get('email', '')}]: ").strip()
        if email:
            update_data['email'] = email
        
        phone = input(f"联系电话 [{user.get('phone', '')}]: ").strip()
        if phone:
            update_data['phone'] = phone
        
        if not update_data:
            self.cli_view.show_message("没有修改任何信息！", "info")
            input("\n按回车键继续...")
            return
        
        # 确认修改
        print("\n修改信息:")
        for key, value in update_data.items():
            print(f"{key}: {value}")
        
        if not self.cli_view.show_confirmation("确认修改该用户信息?"):
            self.cli_view.show_message("已取消修改用户信息！", "info")
            input("\n按回车键继续...")
            return
        
        # 更新用户信息
        result = self.user_controller.update_user(username, update_data)
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")
    
    def show_delete_user(self):
        """显示删除用户界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("删除用户")
        
        # 输入用户名
        username = input("请输入要删除的用户名: ").strip()
        if not username:
            self.cli_view.show_message("用户名不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取用户信息
        result = self.user_controller.get_user(username)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        user = result['data']
        
        # 显示用户信息
        print("\n用户信息:")
        print(f"用户名: {user['username']}")
        print(f"角色: {user.get('role', '未设置')}")
        print(f"真实姓名: {user.get('real_name', '未设置')}")
        
        # 确认删除
        if not self.cli_view.show_confirmation("确认删除该用户? 此操作不可恢复!"):
            self.cli_view.show_message("已取消删除用户！", "info")
            input("\n按回车键继续...")
            return
        
        # 删除用户
        result = self.user_controller.delete_user(username)
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")
    
    def show_reset_password(self):
        """显示重置密码界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("重置用户密码")
        
        # 输入用户名
        username = input("请输入要重置密码的用户名: ").strip()
        if not username:
            self.cli_view.show_message("用户名不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取用户信息
        result = self.user_controller.get_user(username)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        user = result['data']
        
        # 显示用户信息
        print("\n用户信息:")
        print(f"用户名: {user['username']}")
        print(f"角色: {user.get('role', '未设置')}")
        print(f"真实姓名: {user.get('real_name', '未设置')}")
        
        # 输入新密码
        new_password = getpass.getpass("新密码: ")
        if not new_password:
            self.cli_view.show_message("新密码不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        confirm_password = getpass.getpass("确认新密码: ")
        if new_password != confirm_password:
            self.cli_view.show_message("两次输入的密码不一致！", "error")
            input("\n按回车键继续...")
            return
        
        # 确认重置
        if not self.cli_view.show_confirmation("确认重置该用户的密码?"):
            self.cli_view.show_message("已取消重置密码！", "info")
            input("\n按回车键继续...")
            return
        
        # 重置密码
        result = self.user_controller.reset_password(username, new_password)
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")
    
    def show_filter_users(self):
        """显示筛选用户界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("筛选用户")
        
        print("请选择用户角色:")
        print("1. 管理员 (admin)")
        print("2. 教师 (teacher)")
        print("3. 学生 (student)")
        print("4. 访客 (guest)")
        print("0. 返回")
        
        choice = input("\n请选择角色 [0-4]: ").strip()
        
        if choice == "1":
            self.show_user_list("admin")
        elif choice == "2":
            self.show_user_list("teacher")
        elif choice == "3":
            self.show_user_list("student")
        elif choice == "4":
            self.show_user_list("guest")
        elif choice == "0":
            return
        else:
            self.cli_view.show_message("无效的选择，请重新输入！", "warning")
            input("\n按回车键继续...")
            self.show_filter_users()
    
    def show_personal_info(self):
        """显示个人信息界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("个人信息")
        
        # 获取当前用户信息
        username = self.cli_view.current_user.get('username')
        result = self.user_controller.get_user(username)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        user = result['data']
        
        # 显示用户详情
        print(f"用户名: {user['username']}")
        print(f"角色: {user.get('role', '未设置')}")
        print(f"真实姓名: {user.get('real_name', '未设置')}")
        print(f"电子邮箱: {user.get('email', '未设置')}")
        print(f"联系电话: {user.get('phone', '未设置')}")
        print(f"最后登录时间: {user.get('last_login', '未登录')}")
        print(f"创建时间: {user.get('created_at', '未知')}")
        
        # 修改个人信息选项
        print("\n[E] 修改个人信息  [P] 修改密码  [0] 返回")
        choice = input("\n请选择操作: ").strip().lower()
        
        if choice == 'e':
            self.show_edit_personal_info()
        elif choice == 'p':
            self.show_change_password()
        elif choice == '0':
            return
        else:
            self.show_personal_info()
    
    def show_edit_personal_info(self):
        """显示修改个人信息界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("修改个人信息")
        
        # 获取当前用户信息
        username = self.cli_view.current_user.get('username')
        result = self.user_controller.get_user(username)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        user = result['data']
        
        # 显示当前信息
        print("\n当前个人信息:")
        print(f"用户名: {user['username']}")
        print(f"真实姓名: {user.get('real_name', '未设置')}")
        print(f"电子邮箱: {user.get('email', '未设置')}")
        print(f"联系电话: {user.get('phone', '未设置')}")
        
        print("\n请输入新的信息（不修改的项目直接回车）:")
        
        # 收集更新信息
        update_data = {}
        
        real_name = input(f"真实姓名 [{user.get('real_name', '')}]: ").strip()
        if real_name:
            update_data['real_name'] = real_name
        
        email = input(f"电子邮箱 [{user.get('email', '')}]: ").strip()
        if email:
            update_data['email'] = email
        
        phone = input(f"联系电话 [{user.get('phone', '')}]: ").strip()
        if phone:
            update_data['phone'] = phone
        
        if not update_data:
            self.cli_view.show_message("没有修改任何信息！", "info")
            input("\n按回车键继续...")
            return
        
        # 确认修改
        print("\n修改信息:")
        for key, value in update_data.items():
            print(f"{key}: {value}")
        
        if not self.cli_view.show_confirmation("确认修改个人信息?"):
            self.cli_view.show_message("已取消修改个人信息！", "info")
            input("\n按回车键继续...")
            return
        
        # 更新用户信息
        result = self.user_controller.update_user(username, update_data)
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")
    
    def show_change_password(self):
        """显示修改密码界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("修改密码")
        
        # 获取当前用户信息
        username = self.cli_view.current_user.get('username')
        
        # 输入旧密码
        old_password = getpass.getpass("旧密码: ")
        if not old_password:
            self.cli_view.show_message("旧密码不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 输入新密码
        new_password = getpass.getpass("新密码: ")
        if not new_password:
            self.cli_view.show_message("新密码不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        confirm_password = getpass.getpass("确认新密码: ")
        if new_password != confirm_password:
            self.cli_view.show_message("两次输入的密码不一致！", "error")
            input("\n按回车键继续...")
            return
        
        # 确认修改
        if not self.cli_view.show_confirmation("确认修改密码?"):
            self.cli_view.show_message("已取消修改密码！", "info")
            input("\n按回车键继续...")
            return
        
        # 修改密码
        result = self.user_controller.change_password(username, old_password, new_password)
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")