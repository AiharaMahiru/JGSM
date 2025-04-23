"""
命令行界面系统日志管理视图模块
"""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CLILogView:
    """命令行界面系统日志管理视图类"""
    
    def __init__(self, cli_view, log_controller):
        """
        初始化系统日志管理视图
        
        参数:
            cli_view: 命令行界面视图实例
            log_controller: 日志控制器实例
        """
        self.cli_view = cli_view
        self.log_controller = log_controller
    
    def show_system_logs(self):
        """显示系统日志管理界面"""
        while True:
            self.cli_view.clear_screen()
            self.cli_view.show_header("系统日志管理")
            
            print("1. 查看操作日志")
            print("2. 搜索日志记录")
            print("3. 查看用户活动")
            print("4. 操作统计分析")
            print("5. 清理旧日志")
            print("0. 返回主菜单")
            print()
            
            choice = input("请选择操作 [0-5]: ").strip()
            
            if choice == "1":
                self.show_logs()
            elif choice == "2":
                self.show_search_logs()
            elif choice == "3":
                self.show_user_activity()
            elif choice == "4":
                self.show_operation_stats()
            elif choice == "5":
                self.show_clear_logs()
            elif choice == "0":
                break
            else:
                self.cli_view.show_message("无效的选择，请重新输入！", "warning")
                input("\n按回车键继续...")
    
    def show_logs(self, page=1, filters=None):
        """
        显示操作日志列表
        
        参数:
            page (int): 页码
            filters (dict): 过滤条件
        """
        self.cli_view.clear_screen()
        self.cli_view.show_header("操作日志列表")
        
        # 获取日志列表
        result = self.log_controller.get_logs(filters, page, 15)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        pagination = result['data']
        logs = pagination['items']
        
        if not logs:
            self.cli_view.show_message("没有找到日志记录！", "info")
            input("\n按回车键继续...")
            return
        
        # 显示日志列表
        print(f"{'ID':<5} {'时间':<20} {'用户':<15} {'操作':<15} {'详情':<40}")
        print("-" * 95)
        
        for log in logs:
            # 截断过长的详情
            details = log.get('details', '')
            if len(details) > 40:
                details = details[:37] + "..."
            
            print(f"{log.get('id', ''):<5} {log.get('timestamp', ''):<20} {log.get('username', ''):<15} {log.get('operation', ''):<15} {details:<40}")
        
        print("-" * 95)
        print(f"第 {pagination['page']} 页，每页 {pagination['page_size']} 条记录")
        
        # 分页导航
        print("\n[P] 上一页  [N] 下一页  [F] 筛选  [V] 查看详情  [0] 返回")
        choice = input("\n请选择操作: ").strip().lower()
        
        if choice == 'p' and pagination['page'] > 1:
            self.show_logs(page - 1, filters)
        elif choice == 'n' and pagination['has_more']:
            self.show_logs(page + 1, filters)
        elif choice == 'f':
            self.show_filter_logs()
        elif choice == 'v':
            log_id = input("请输入要查看的日志ID: ").strip()
            self.show_log_details(log_id, logs)
        elif choice == '0':
            return
        else:
            self.show_logs(page, filters)
    
    def show_log_details(self, log_id, logs=None):
        """
        显示日志详情
        
        参数:
            log_id (str): 日志ID
            logs (list, optional): 日志列表，如果提供则从中查找，否则从数据库查询
        """
        self.cli_view.clear_screen()
        self.cli_view.show_header("日志详情")
        
        # 查找日志记录
        log = None
        if logs:
            for item in logs:
                if str(item.get('id', '')) == log_id:
                    log = item
                    break
        
        if not log:
            self.cli_view.show_message(f"未找到ID为 {log_id} 的日志记录！", "error")
            input("\n按回车键继续...")
            return
        
        # 显示日志详情
        print(f"日志ID: {log.get('id', '')}")
        print(f"时间: {log.get('timestamp', '')}")
        print(f"用户: {log.get('username', '')}")
        print(f"操作: {log.get('operation', '')}")
        print(f"目标: {log.get('target', '')}")
        print(f"IP地址: {log.get('ip_address', '')}")
        print("\n详情:")
        print(log.get('details', ''))
        
        input("\n按回车键继续...")
    
    def show_filter_logs(self):
        """显示筛选日志界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("筛选日志")
        
        # 收集筛选条件
        filters = {}
        
        username = input("用户名: ").strip()
        if username:
            filters['username'] = username
        
        operation = input("操作类型: ").strip()
        if operation:
            filters['operation'] = operation
        
        date_range = input("日期范围 (今天/昨天/本周/本月/全部): ").strip().lower()
        if date_range == "今天":
            today = datetime.now().strftime('%Y-%m-%d')
            filters['start_date'] = today
            filters['end_date'] = today
        elif date_range == "昨天":
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            filters['start_date'] = yesterday
            filters['end_date'] = yesterday
        elif date_range == "本周":
            today = datetime.now()
            start_of_week = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
            filters['start_date'] = start_of_week
        elif date_range == "本月":
            today = datetime.now()
            start_of_month = today.replace(day=1).strftime('%Y-%m-%d')
            filters['start_date'] = start_of_month
        
        # 应用筛选
        self.show_logs(1, filters)
    
    def show_search_logs(self):
        """显示搜索日志界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("搜索日志")
        
        # 输入搜索关键词
        keyword = input("请输入搜索关键词: ").strip()
        if not keyword:
            self.cli_view.show_message("搜索关键词不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 输入日期范围（可选）
        print("\n日期范围 (可选):")
        start_date = input("开始日期 (YYYY-MM-DD): ").strip()
        end_date = input("结束日期 (YYYY-MM-DD): ").strip()
        
        # 搜索日志
        result = self.log_controller.search_logs(keyword, start_date, end_date)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        pagination = result['data']
        logs = pagination['items']
        
        if not logs:
            self.cli_view.show_message(f"没有找到匹配 '{keyword}' 的日志记录！", "info")
            input("\n按回车键继续...")
            return
        
        # 显示搜索结果
        self.cli_view.clear_screen()
        self.cli_view.show_header("搜索结果")
        
        print(f"关键词: '{keyword}'")
        if start_date:
            print(f"开始日期: {start_date}")
        if end_date:
            print(f"结束日期: {end_date}")
        
        print(f"\n找到 {len(logs)} 条匹配记录:")
        print(f"{'ID':<5} {'时间':<20} {'用户':<15} {'操作':<15} {'详情':<40}")
        print("-" * 95)
        
        for log in logs:
            # 截断过长的详情
            details = log.get('details', '')
            if len(details) > 40:
                details = details[:37] + "..."
            
            print(f"{log.get('id', ''):<5} {log.get('timestamp', ''):<20} {log.get('username', ''):<15} {log.get('operation', ''):<15} {details:<40}")
        
        # 查看详情选项
        print("\n[V] 查看详情  [0] 返回")
        choice = input("\n请选择操作: ").strip().lower()
        
        if choice == 'v':
            log_id = input("请输入要查看的日志ID: ").strip()
            self.show_log_details(log_id, logs)
    
    def show_user_activity(self):
        """显示用户活动界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("用户活动")
        
        # 输入用户名
        username = input("请输入用户名: ").strip()
        if not username:
            self.cli_view.show_message("用户名不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取用户活动记录
        result = self.log_controller.get_user_activity(username)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        logs = result['data']
        
        if not logs:
            self.cli_view.show_message(f"没有找到用户 '{username}' 的活动记录！", "info")
            input("\n按回车键继续...")
            return
        
        # 显示用户活动
        print(f"\n用户 '{username}' 的最近 {len(logs)} 条活动记录:")
        print(f"{'时间':<20} {'操作':<15} {'详情':<55}")
        print("-" * 90)
        
        for log in logs:
            # 截断过长的详情
            details = log.get('details', '')
            if len(details) > 55:
                details = details[:52] + "..."
            
            print(f"{log.get('timestamp', ''):<20} {log.get('operation', ''):<15} {details:<55}")
        
        input("\n按回车键继续...")
    
    def show_operation_stats(self):
        """显示操作统计分析界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("操作统计分析")
        
        # 选择统计时间范围
        print("请选择统计时间范围:")
        print("1. 最近7天")
        print("2. 最近30天")
        print("3. 最近90天")
        print("4. 最近365天")
        print("0. 返回")
        
        choice = input("\n请选择 [0-4]: ").strip()
        
        days = 0
        if choice == "1":
            days = 7
        elif choice == "2":
            days = 30
        elif choice == "3":
            days = 90
        elif choice == "4":
            days = 365
        elif choice == "0":
            return
        else:
            self.cli_view.show_message("无效的选择，请重新输入！", "warning")
            input("\n按回车键继续...")
            self.show_operation_stats()
            return
        
        # 获取操作统计信息
        result = self.log_controller.get_operation_stats(days)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        stats = result['data']
        
        # 显示统计信息
        print(f"\n最近 {days} 天的操作统计:")
        print(f"总操作次数: {stats.get('total_operations', 0)}")
        print(f"活跃用户数: {stats.get('active_users', 0)}")
        
        # 显示操作类型分布
        if 'operation_types' in stats:
            print("\n操作类型分布:")
            for op_type, count in stats['operation_types'].items():
                print(f"{op_type}: {count} 次")
        
        # 显示用户活跃度排名
        if 'user_activity' in stats:
            print("\n用户活跃度排名:")
            for i, (username, count) in enumerate(stats['user_activity'].items()):
                print(f"{i+1}. {username}: {count} 次操作")
                if i >= 9:  # 只显示前10名
                    break
        
        # 显示每日操作趋势
        if 'daily_trend' in stats:
            print("\n每日操作趋势:")
            for date, count in stats['daily_trend'].items():
                print(f"{date}: {count} 次")
        
        input("\n按回车键继续...")
    
    def show_clear_logs(self):
        """显示清理旧日志界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("清理旧日志")
        
        print("请选择要保留的日志时间范围:")
        print("1. 保留最近30天")
        print("2. 保留最近90天")
        print("3. 保留最近180天")
        print("4. 保留最近365天")
        print("0. 返回")
        
        choice = input("\n请选择 [0-4]: ").strip()
        
        days = 0
        if choice == "1":
            days = 30
        elif choice == "2":
            days = 90
        elif choice == "3":
            days = 180
        elif choice == "4":
            days = 365
        elif choice == "0":
            return
        else:
            self.cli_view.show_message("无效的选择，请重新输入！", "warning")
            input("\n按回车键继续...")
            self.show_clear_logs()
            return
        
        # 确认清理
        if not self.cli_view.show_confirmation(f"确认清除 {days} 天前的所有日志? 此操作不可恢复!"):
            self.cli_view.show_message("已取消清理日志！", "info")
            input("\n按回车键继续...")
            return
        
        # 清理旧日志
        result = self.log_controller.clear_old_logs(days)
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")