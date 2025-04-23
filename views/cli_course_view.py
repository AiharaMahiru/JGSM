"""
命令行界面课程管理视图模块
"""
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CLICourseView:
    """命令行界面课程管理视图类"""
    
    def __init__(self, cli_view, course_controller, grade_controller=None):
        """
        初始化课程管理视图
        
        参数:
            cli_view: 命令行界面视图实例
            course_controller: 课程控制器实例
            grade_controller: 成绩控制器实例（可选）
        """
        self.cli_view = cli_view
        self.course_controller = course_controller
        self.grade_controller = grade_controller
    
    def show_course_management(self):
        """显示课程管理界面"""
        while True:
            self.cli_view.clear_screen()
            self.cli_view.show_header("课程管理")
            
            print("1. 查看课程列表")
            print("2. 添加新课程")
            print("3. 修改课程信息")
            print("4. 删除课程")
            print("5. 搜索课程")
            print("6. 导入课程数据")
            print("0. 返回主菜单")
            print()
            
            choice = input("请选择操作 [0-6]: ").strip()
            
            if choice == "1":
                self.show_course_list()
            elif choice == "2":
                self.show_add_course()
            elif choice == "3":
                self.show_edit_course()
            elif choice == "4":
                self.show_delete_course()
            elif choice == "5":
                self.show_search_course()
            elif choice == "6":
                self.show_import_courses()
            elif choice == "0":
                break
            else:
                self.cli_view.show_message("无效的选择，请重新输入！", "warning")
                input("\n按回车键继续...")
    
    def show_course_list(self, page=1, filters=None):
        """
        显示课程列表
        
        参数:
            page (int): 页码
            filters (dict): 过滤条件
        """
        self.cli_view.clear_screen()
        self.cli_view.show_header("课程列表")
        
        # 获取课程列表
        result = self.course_controller.get_all_courses(filters, page, 10)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        pagination = result['data']
        courses = pagination['items']
        
        if not courses:
            self.cli_view.show_message("没有找到课程记录！", "info")
            input("\n按回车键继续...")
            return
        
        # 显示课程列表
        print(f"{'课程编号':<10} {'课程名称':<20} {'学分':<5} {'任课教师':<10}")
        print("-" * 60)
        
        for course in courses:
            print(f"{course['course_id']:<10} {course['course_name']:<20} {course['credit']:<5} {course.get('teacher', ''):<10}")
        
        print("-" * 60)
        print(f"第 {pagination['page']} 页，共 {pagination['total_pages']} 页，总计 {pagination['total_items']} 条记录")
        
        # 分页导航
        print("\n[P] 上一页  [N] 下一页  [F] 筛选  [V] 查看详情  [0] 返回")
        choice = input("\n请选择操作: ").strip().lower()
        
        if choice == 'p' and pagination['page'] > 1:
            self.show_course_list(page - 1, filters)
        elif choice == 'n' and pagination['page'] < pagination['total_pages']:
            self.show_course_list(page + 1, filters)
        elif choice == 'f':
            self.show_filter_courses()
        elif choice == 'v':
            course_id = input("请输入要查看的课程编号: ").strip()
            self.show_course_details(course_id)
        elif choice == '0':
            return
        else:
            self.show_course_list(page, filters)
    
    def show_course_details(self, course_id):
        """
        显示课程详情
        
        参数:
            course_id (str): 课程编号
        """
        self.cli_view.clear_screen()
        self.cli_view.show_header("课程详情")
        
        # 获取课程信息
        result = self.course_controller.get_course(course_id)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        course = result['data']
        
        # 显示课程详情
        print(f"课程编号: {course['course_id']}")
        print(f"课程名称: {course['course_name']}")
        print(f"学分: {course['credit']}")
        print(f"任课教师: {course.get('teacher', '未设置')}")
        print(f"课程描述: {course.get('description', '未设置')}")
        print(f"创建时间: {course.get('created_at', '未知')}")
        print(f"更新时间: {course.get('updated_at', '未知')}")
        
        # 获取课程成绩统计（如果有成绩控制器）
        if self.grade_controller:
            # 获取学期列表
            semesters = ["2023-2024-1", "2023-2024-2", "2024-2025-1"]  # 这里应该从数据库获取
            
            print("\n选择学期查看成绩统计:")
            for i, semester in enumerate(semesters):
                print(f"{i+1}. {semester}")
            
            choice = input("\n请选择学期 (输入序号): ").strip()
            try:
                index = int(choice) - 1
                if 0 <= index < len(semesters):
                    semester = semesters[index]
                    stats_result = self.grade_controller.get_course_statistics(course_id, semester)
                    
                    if stats_result['success']:
                        stats = stats_result['data']
                        print(f"\n{semester} 学期成绩统计:")
                        print(f"总人数: {stats['total_students']}")
                        print(f"最高分: {stats['max_score']}")
                        print(f"最低分: {stats['min_score']}")
                        print(f"平均分: {stats['avg_score']}")
                        print(f"及格率: {stats['pass_rate']}%")
                        
                        print("\n分数段分布:")
                        for score_range, count in stats.get('score_distribution', {}).items():
                            print(f"{score_range}: {count}人")
            except:
                pass
        
        input("\n按回车键继续...")
    
    def show_add_course(self):
        """显示添加课程界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("添加新课程")
        
        # 收集课程信息
        course_data = {}
        
        course_data['course_id'] = input("课程编号 (必填): ").strip()
        if not course_data['course_id']:
            self.cli_view.show_message("课程编号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        course_data['course_name'] = input("课程名称 (必填): ").strip()
        if not course_data['course_name']:
            self.cli_view.show_message("课程名称不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        credit = input("学分 (必填): ").strip()
        if not credit:
            self.cli_view.show_message("学分不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        try:
            course_data['credit'] = float(credit)
        except ValueError:
            self.cli_view.show_message("学分必须为数字！", "error")
            input("\n按回车键继续...")
            return
        
        teacher = input("任课教师: ").strip()
        if teacher:
            course_data['teacher'] = teacher
        
        description = input("课程描述: ").strip()
        if description:
            course_data['description'] = description
        
        # 确认添加
        print("\n课程信息:")
        for key, value in course_data.items():
            print(f"{key}: {value}")
        
        if not self.cli_view.show_confirmation("确认添加该课程?"):
            self.cli_view.show_message("已取消添加课程！", "info")
            input("\n按回车键继续...")
            return
        
        # 添加课程
        result = self.course_controller.add_course(course_data)
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")
    
    def show_edit_course(self):
        """显示修改课程信息界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("修改课程信息")
        
        # 输入课程编号
        course_id = input("请输入要修改的课程编号: ").strip()
        if not course_id:
            self.cli_view.show_message("课程编号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取课程信息
        result = self.course_controller.get_course(course_id)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        course = result['data']
        
        # 显示当前信息
        print("\n当前课程信息:")
        for key, value in course.items():
            if key not in ['created_at', 'updated_at']:
                print(f"{key}: {value}")
        
        print("\n请输入新的信息（不修改的项目直接回车）:")
        
        # 收集更新信息
        update_data = {}
        
        course_name = input(f"课程名称 [{course['course_name']}]: ").strip()
        if course_name:
            update_data['course_name'] = course_name
        
        credit = input(f"学分 [{course['credit']}]: ").strip()
        if credit:
            try:
                update_data['credit'] = float(credit)
            except ValueError:
                self.cli_view.show_message("学分必须为数字！", "error")
                input("\n按回车键继续...")
                return
        
        teacher = input(f"任课教师 [{course.get('teacher', '')}]: ").strip()
        if teacher:
            update_data['teacher'] = teacher
        
        description = input(f"课程描述 [{course.get('description', '')}]: ").strip()
        if description:
            update_data['description'] = description
        
        if not update_data:
            self.cli_view.show_message("没有修改任何信息！", "info")
            input("\n按回车键继续...")
            return
        
        # 确认修改
        print("\n修改信息:")
        for key, value in update_data.items():
            print(f"{key}: {value}")
        
        if not self.cli_view.show_confirmation("确认修改该课程信息?"):
            self.cli_view.show_message("已取消修改课程信息！", "info")
            input("\n按回车键继续...")
            return
        
        # 更新课程信息
        result = self.course_controller.update_course(course_id, update_data)
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")
    
    def show_delete_course(self):
        """显示删除课程界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("删除课程")
        
        # 输入课程编号
        course_id = input("请输入要删除的课程编号: ").strip()
        if not course_id:
            self.cli_view.show_message("课程编号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取课程信息
        result = self.course_controller.get_course(course_id)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        course = result['data']
        
        # 显示课程信息
        print("\n课程信息:")
        print(f"课程编号: {course['course_id']}")
        print(f"课程名称: {course['course_name']}")
        print(f"学分: {course['credit']}")
        print(f"任课教师: {course.get('teacher', '未设置')}")
        
        # 确认删除
        if not self.cli_view.show_confirmation("确认删除该课程? 此操作不可恢复!"):
            self.cli_view.show_message("已取消删除课程！", "info")
            input("\n按回车键继续...")
            return
        
        # 删除课程
        result = self.course_controller.delete_course(course_id)
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")
    
    def show_search_course(self):
        """显示搜索课程界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("搜索课程")
        
        # 输入搜索关键词
        keyword = input("请输入搜索关键词 (课程编号/课程名称/教师): ").strip()
        if not keyword:
            self.cli_view.show_message("搜索关键词不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 搜索课程
        result = self.course_controller.search_courses(keyword)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        courses = result['data']['items']
        
        if not courses:
            self.cli_view.show_message(f"没有找到匹配 '{keyword}' 的课程记录！", "info")
            input("\n按回车键继续...")
            return
        
        # 显示搜索结果
        print(f"\n搜索结果 ({len(courses)} 条记录):")
        print(f"{'课程编号':<10} {'课程名称':<20} {'学分':<5} {'任课教师':<10}")
        print("-" * 60)
        
        for course in courses:
            print(f"{course['course_id']:<10} {course['course_name']:<20} {course['credit']:<5} {course.get('teacher', ''):<10}")
        
        # 查看详情选项
        print("\n[V] 查看详情  [0] 返回")
        choice = input("\n请选择操作: ").strip().lower()
        
        if choice == 'v':
            course_id = input("请输入要查看的课程编号: ").strip()
            self.show_course_details(course_id)
    
    def show_filter_courses(self):
        """显示筛选课程界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("筛选课程")
        
        # 收集筛选条件
        filters = {}
        
        teacher = input("任课教师: ").strip()
        if teacher:
            filters['teacher'] = teacher
        
        # 应用筛选
        self.show_course_list(1, filters)
    
    def show_import_courses(self):
        """显示导入课程数据界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("导入课程数据")
        
        self.cli_view.show_message("此功能需要准备CSV文件，然后通过程序导入。", "info")
        self.cli_view.show_message("CSV文件格式应包含以下字段: course_id,course_name,credit,teacher,description", "info")
        
        if not self.cli_view.show_confirmation("是否继续操作?"):
            return
        
        filepath = input("\n请输入CSV文件路径: ").strip()
        if not filepath:
            self.cli_view.show_message("文件路径不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        if not os.path.exists(filepath):
            self.cli_view.show_message(f"文件 {filepath} 不存在！", "error")
            input("\n按回车键继续...")
            return
        
        try:
            import csv
            courses_data = []
            
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    courses_data.append(row)
            
            if not courses_data:
                self.cli_view.show_message("CSV文件中没有数据！", "error")
                input("\n按回车键继续...")
                return
            
            # 确认导入
            print(f"\n找到 {len(courses_data)} 条课程记录，前5条记录预览:")
            for i, course in enumerate(courses_data[:5]):
                print(f"{i+1}. 编号: {course.get('course_id', '')}, 名称: {course.get('course_name', '')}, 学分: {course.get('credit', '')}")
            
            if not self.cli_view.show_confirmation("确认导入这些课程数据?"):
                self.cli_view.show_message("已取消导入课程数据！", "info")
                input("\n按回车键继续...")
                return
            
            # 导入课程数据
            result = self.course_controller.import_courses(courses_data)
            
            if result['success']:
                self.cli_view.show_message(result['message'], "success")
                
                # 显示导入结果
                data = result['data']
                print(f"\n成功导入: {data['success_count']} 条记录")
                print(f"导入失败: {data['failed_count']} 条记录")
                
                if data['failed_count'] > 0 and self.cli_view.show_confirmation("是否查看失败记录详情?"):
                    print("\n失败记录详情:")
                    for i, record in enumerate(data['failed_records']):
                        print(f"{i+1}. 编号: {record['data'].get('course_id', '')}, 名称: {record['data'].get('course_name', '')}")
                        print(f"   原因: {record['reason']}")
            else:
                self.cli_view.show_message(result['message'], "error")
            
            input("\n按回车键继续...")
        except Exception as e:
            self.cli_view.show_message(f"导入过程中出错: {str(e)}", "error")
            input("\n按回车键继续...")