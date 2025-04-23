"""
命令行界面学生管理视图模块
"""
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CLIStudentView:
    """命令行界面学生管理视图类"""
    
    def __init__(self, cli_view, student_controller, grade_controller=None):
        """
        初始化学生管理视图
        
        参数:
            cli_view: 命令行界面视图实例
            student_controller: 学生控制器实例
            grade_controller: 成绩控制器实例（可选）
        """
        self.cli_view = cli_view
        self.student_controller = student_controller
        self.grade_controller = grade_controller
    
    def show_student_management(self):
        """显示学生管理界面"""
        while True:
            self.cli_view.clear_screen()
            self.cli_view.show_header("学生管理")
            
            print("1. 查看学生列表")
            print("2. 添加新学生")
            print("3. 修改学生信息")
            print("4. 删除学生")
            print("5. 搜索学生")
            print("6. 导入学生数据")
            print("0. 返回主菜单")
            print()
            
            choice = input("请选择操作 [0-6]: ").strip()
            
            if choice == "1":
                self.show_student_list()
            elif choice == "2":
                self.show_add_student()
            elif choice == "3":
                self.show_edit_student()
            elif choice == "4":
                self.show_delete_student()
            elif choice == "5":
                self.show_search_student()
            elif choice == "6":
                self.show_import_students()
            elif choice == "0":
                break
            else:
                self.cli_view.show_message("无效的选择，请重新输入！", "warning")
                input("\n按回车键继续...")
    
    def show_student_list(self, page=1, filters=None):
        """
        显示学生列表
        
        参数:
            page (int): 页码
            filters (dict): 过滤条件
        """
        self.cli_view.clear_screen()
        self.cli_view.show_header("学生列表")
        
        # 获取学生列表
        result = self.student_controller.get_all_students(filters, page, 10)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        pagination = result['data']
        students = pagination['items']
        
        if not students:
            self.cli_view.show_message("没有找到学生记录！", "info")
            input("\n按回车键继续...")
            return
        
        # 显示学生列表
        print(f"{'学号':<15} {'姓名':<10} {'性别':<5} {'班级':<15} {'状态':<5}")
        print("-" * 60)
        
        for student in students:
            print(f"{student['student_id']:<15} {student['name']:<10} {student.get('gender', ''):<5} {student.get('class_name', ''):<15} {student.get('status', ''):<5}")
        
        print("-" * 60)
        print(f"第 {pagination['page']} 页，共 {pagination['total_pages']} 页，总计 {pagination['total_items']} 条记录")
        
        # 分页导航
        print("\n[P] 上一页  [N] 下一页  [F] 筛选  [V] 查看详情  [0] 返回")
        choice = input("\n请选择操作: ").strip().lower()
        
        if choice == 'p' and pagination['page'] > 1:
            self.show_student_list(page - 1, filters)
        elif choice == 'n' and pagination['page'] < pagination['total_pages']:
            self.show_student_list(page + 1, filters)
        elif choice == 'f':
            self.show_filter_students()
        elif choice == 'v':
            student_id = input("请输入要查看的学生学号: ").strip()
            self.show_student_details(student_id)
        elif choice == '0':
            return
        else:
            self.show_student_list(page, filters)
    
    def show_student_details(self, student_id):
        """
        显示学生详情
        
        参数:
            student_id (str): 学号
        """
        self.cli_view.clear_screen()
        self.cli_view.show_header("学生详情")
        
        # 获取学生信息
        result = self.student_controller.get_student(student_id)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        student = result['data']
        
        # 显示学生详情
        print(f"学号: {student['student_id']}")
        print(f"姓名: {student['name']}")
        print(f"性别: {student.get('gender', '未设置')}")
        print(f"出生日期: {student.get('birth_date', '未设置')}")
        print(f"班级: {student.get('class_name', '未设置')}")
        print(f"入学日期: {student.get('admission_date', '未设置')}")
        print(f"联系电话: {student.get('contact_phone', '未设置')}")
        print(f"电子邮箱: {student.get('email', '未设置')}")
        print(f"地址: {student.get('address', '未设置')}")
        print(f"状态: {student.get('status', '未设置')}")
        print(f"创建时间: {student.get('created_at', '未知')}")
        print(f"更新时间: {student.get('updated_at', '未知')}")
        
        # 获取学生成绩
        if self.grade_controller:
            grade_result = self.grade_controller.get_student_grades(student_id)
            if grade_result['success'] and grade_result['data']['items']:
                print("\n成绩记录:")
                print(f"{'学期':<10} {'课程编号':<10} {'课程名称':<20} {'学分':<5} {'成绩':<5} {'绩点':<5}")
                print("-" * 60)
                
                for grade in grade_result['data']['items']:
                    print(f"{grade['semester']:<10} {grade['course_id']:<10} {grade.get('course_name', ''):<20} {grade.get('credit', ''):<5} {grade['score']:<5} {grade.get('grade_point', ''):<5}")
        
        input("\n按回车键继续...")
    
    def show_add_student(self):
        """显示添加学生界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("添加新学生")
        
        # 收集学生信息
        student_data = {}
        
        student_data['student_id'] = input("学号 (必填): ").strip()
        if not student_data['student_id']:
            self.cli_view.show_message("学号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        student_data['name'] = input("姓名 (必填): ").strip()
        if not student_data['name']:
            self.cli_view.show_message("姓名不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        gender = input("性别 (男/女/其他): ").strip()
        if gender:
            student_data['gender'] = gender
        
        birth_date = input("出生日期 (YYYY-MM-DD): ").strip()
        if birth_date:
            student_data['birth_date'] = birth_date
        
        class_name = input("班级: ").strip()
        if class_name:
            student_data['class_name'] = class_name
        
        admission_date = input("入学日期 (YYYY-MM-DD): ").strip()
        if admission_date:
            student_data['admission_date'] = admission_date
        
        contact_phone = input("联系电话: ").strip()
        if contact_phone:
            student_data['contact_phone'] = contact_phone
        
        email = input("电子邮箱: ").strip()
        if email:
            student_data['email'] = email
        
        address = input("地址: ").strip()
        if address:
            student_data['address'] = address
        
        status = input("状态 (在读/休学/退学/毕业): ").strip()
        if status:
            student_data['status'] = status
        
        # 确认添加
        print("\n学生信息:")
        for key, value in student_data.items():
            print(f"{key}: {value}")
        
        if not self.cli_view.show_confirmation("确认添加该学生?"):
            self.cli_view.show_message("已取消添加学生！", "info")
            input("\n按回车键继续...")
            return
        
        # 添加学生
        result = self.student_controller.add_student(student_data)
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")
    
    def show_edit_student(self):
        """显示修改学生信息界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("修改学生信息")
        
        # 输入学号
        student_id = input("请输入要修改的学生学号: ").strip()
        if not student_id:
            self.cli_view.show_message("学号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取学生信息
        result = self.student_controller.get_student(student_id)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        student = result['data']
        
        # 显示当前信息
        print("\n当前学生信息:")
        for key, value in student.items():
            if key not in ['created_at', 'updated_at']:
                print(f"{key}: {value}")
        
        print("\n请输入新的信息（不修改的项目直接回车）:")
        
        # 收集更新信息
        update_data = {}
        
        name = input(f"姓名 [{student['name']}]: ").strip()
        if name:
            update_data['name'] = name
        
        gender = input(f"性别 [{student.get('gender', '')}]: ").strip()
        if gender:
            update_data['gender'] = gender
        
        birth_date = input(f"出生日期 [{student.get('birth_date', '')}]: ").strip()
        if birth_date:
            update_data['birth_date'] = birth_date
        
        class_name = input(f"班级 [{student.get('class_name', '')}]: ").strip()
        if class_name:
            update_data['class_name'] = class_name
        
        admission_date = input(f"入学日期 [{student.get('admission_date', '')}]: ").strip()
        if admission_date:
            update_data['admission_date'] = admission_date
        
        contact_phone = input(f"联系电话 [{student.get('contact_phone', '')}]: ").strip()
        if contact_phone:
            update_data['contact_phone'] = contact_phone
        
        email = input(f"电子邮箱 [{student.get('email', '')}]: ").strip()
        if email:
            update_data['email'] = email
        
        address = input(f"地址 [{student.get('address', '')}]: ").strip()
        if address:
            update_data['address'] = address
        
        status = input(f"状态 [{student.get('status', '')}]: ").strip()
        if status:
            update_data['status'] = status
        
        if not update_data:
            self.cli_view.show_message("没有修改任何信息！", "info")
            input("\n按回车键继续...")
            return
        
        # 确认修改
        print("\n修改信息:")
        for key, value in update_data.items():
            print(f"{key}: {value}")
        
        if not self.cli_view.show_confirmation("确认修改该学生信息?"):
            self.cli_view.show_message("已取消修改学生信息！", "info")
            input("\n按回车键继续...")
            return
        
        # 更新学生信息
        result = self.student_controller.update_student(student_id, update_data)
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")
    
    def show_delete_student(self):
        """显示删除学生界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("删除学生")
        
        # 输入学号
        student_id = input("请输入要删除的学生学号: ").strip()
        if not student_id:
            self.cli_view.show_message("学号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取学生信息
        result = self.student_controller.get_student(student_id)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        student = result['data']
        
        # 显示学生信息
        print("\n学生信息:")
        print(f"学号: {student['student_id']}")
        print(f"姓名: {student['name']}")
        print(f"性别: {student.get('gender', '未设置')}")
        print(f"班级: {student.get('class_name', '未设置')}")
        print(f"状态: {student.get('status', '未设置')}")
        
        # 确认删除
        if not self.cli_view.show_confirmation("确认删除该学生? 此操作不可恢复!"):
            self.cli_view.show_message("已取消删除学生！", "info")
            input("\n按回车键继续...")
            return
        
        # 删除学生
        result = self.student_controller.delete_student(student_id)
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")
    
    def show_search_student(self):
        """显示搜索学生界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("搜索学生")
        
        # 输入搜索关键词
        keyword = input("请输入搜索关键词 (学号/姓名/班级/电话): ").strip()
        if not keyword:
            self.cli_view.show_message("搜索关键词不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 搜索学生
        result = self.student_controller.search_students(keyword)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        students = result['data']['items']
        
        if not students:
            self.cli_view.show_message(f"没有找到匹配 '{keyword}' 的学生记录！", "info")
            input("\n按回车键继续...")
            return
        
        # 显示搜索结果
        print(f"\n搜索结果 ({len(students)} 条记录):")
        print(f"{'学号':<15} {'姓名':<10} {'性别':<5} {'班级':<15} {'状态':<5}")
        print("-" * 60)
        
        for student in students:
            print(f"{student['student_id']:<15} {student['name']:<10} {student.get('gender', ''):<5} {student.get('class_name', ''):<15} {student.get('status', ''):<5}")
        
        # 查看详情选项
        print("\n[V] 查看详情  [0] 返回")
        choice = input("\n请选择操作: ").strip().lower()
        
        if choice == 'v':
            student_id = input("请输入要查看的学生学号: ").strip()
            self.show_student_details(student_id)
    
    def show_filter_students(self):
        """显示筛选学生界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("筛选学生")
        
        # 收集筛选条件
        filters = {}
        
        class_name = input("班级: ").strip()
        if class_name:
            filters['class_name'] = class_name
        
        status = input("状态 (在读/休学/退学/毕业): ").strip()
        if status:
            filters['status'] = status
        
        # 应用筛选
        self.show_student_list(1, filters)
    
    def show_import_students(self):
        """显示导入学生数据界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("导入学生数据")
        
        self.cli_view.show_message("此功能需要准备CSV文件，然后通过程序导入。", "info")
        self.cli_view.show_message("CSV文件格式应包含以下字段: student_id,name,gender,birth_date,class_name,admission_date,contact_phone,email,address,status", "info")
        
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
            students_data = []
            
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    students_data.append(row)
            
            if not students_data:
                self.cli_view.show_message("CSV文件中没有数据！", "error")
                input("\n按回车键继续...")
                return
            
            # 确认导入
            print(f"\n找到 {len(students_data)} 条学生记录，前5条记录预览:")
            for i, student in enumerate(students_data[:5]):
                print(f"{i+1}. 学号: {student.get('student_id', '')}, 姓名: {student.get('name', '')}, 班级: {student.get('class_name', '')}")
            
            if not self.cli_view.show_confirmation("确认导入这些学生数据?"):
                self.cli_view.show_message("已取消导入学生数据！", "info")
                input("\n按回车键继续...")
                return
            
            # 导入学生数据
            result = self.student_controller.import_students(students_data)
            
            if result['success']:
                self.cli_view.show_message(result['message'], "success")
                
                # 显示导入结果
                data = result['data']
                print(f"\n成功导入: {data['success_count']} 条记录")
                print(f"导入失败: {data['failed_count']} 条记录")
                
                if data['failed_count'] > 0 and self.cli_view.show_confirmation("是否查看失败记录详情?"):
                    print("\n失败记录详情:")
                    for i, record in enumerate(data['failed_records']):
                        print(f"{i+1}. 学号: {record['data'].get('student_id', '')}, 姓名: {record['data'].get('name', '')}")
                        print(f"   原因: {record['reason']}")
            else:
                self.cli_view.show_message(result['message'], "error")
            
            input("\n按回车键继续...")
        except Exception as e:
            self.cli_view.show_message(f"导入过程中出错: {str(e)}", "error")
            input("\n按回车键继续...")