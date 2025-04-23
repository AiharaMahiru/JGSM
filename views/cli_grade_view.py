"""
命令行界面成绩管理视图模块
"""
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CLIGradeView:
    """命令行界面成绩管理视图类"""
    
    def __init__(self, cli_view, grade_controller, student_controller=None, course_controller=None):
        """
        初始化成绩管理视图
        
        参数:
            cli_view: 命令行界面视图实例
            grade_controller: 成绩控制器实例
            student_controller: 学生控制器实例（可选）
            course_controller: 课程控制器实例（可选）
        """
        self.cli_view = cli_view
        self.grade_controller = grade_controller
        self.student_controller = student_controller
        self.course_controller = course_controller
    
    def show_grade_management(self):
        """显示成绩管理界面"""
        while True:
            self.cli_view.clear_screen()
            self.cli_view.show_header("成绩管理")
            
            print("1. 查看学生成绩")
            print("2. 查看课程成绩")
            print("3. 添加成绩记录")
            print("4. 修改成绩记录")
            print("5. 删除成绩记录")
            print("6. 成绩统计分析")
            print("7. 导入成绩数据")
            print("0. 返回主菜单")
            print()
            
            choice = input("请选择操作 [0-7]: ").strip()
            
            if choice == "1":
                self.show_student_grades()
            elif choice == "2":
                self.show_course_grades()
            elif choice == "3":
                self.show_add_grade()
            elif choice == "4":
                self.show_edit_grade()
            elif choice == "5":
                self.show_delete_grade()
            elif choice == "6":
                self.show_grade_statistics()
            elif choice == "7":
                self.show_import_grades()
            elif choice == "0":
                break
            else:
                self.cli_view.show_message("无效的选择，请重新输入！", "warning")
                input("\n按回车键继续...")
    
    def show_student_grades(self):
        """显示学生成绩界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("查看学生成绩")
        
        # 输入学号
        student_id = input("请输入学生学号: ").strip()
        if not student_id:
            self.cli_view.show_message("学号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取学生信息
        if self.student_controller:
            student_result = self.student_controller.get_student(student_id)
            if not student_result['success']:
                self.cli_view.show_message(student_result['message'], "error")
                input("\n按回车键继续...")
                return
            
            student = student_result['data']
            print(f"\n学生信息: {student['name']} ({student['student_id']}), 班级: {student.get('class_name', '未知')}")
        
        # 选择学期
        semester = input("\n请输入学期 (例如: 2023-2024-1)，留空查看所有学期: ").strip()
        
        # 获取学生成绩
        result = self.grade_controller.get_student_grades(student_id, semester)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        grades = result['data']['items']
        
        if not grades:
            self.cli_view.show_message(f"没有找到该学生的成绩记录！", "info")
            input("\n按回车键继续...")
            return
        
        # 显示成绩记录
        print(f"\n成绩记录:")
        print(f"{'学期':<12} {'课程编号':<10} {'课程名称':<20} {'学分':<5} {'成绩':<5} {'绩点':<5}")
        print("-" * 70)
        
        for grade in grades:
            print(f"{grade['semester']:<12} {grade['course_id']:<10} {grade.get('course_name', ''):<20} {grade.get('credit', ''):<5} {grade['score']:<5} {grade.get('grade_point', ''):<5}")
        
        # 计算GPA
        gpa_result = self.grade_controller.calculate_student_gpa(student_id, semester)
        if gpa_result['success']:
            gpa_data = gpa_result['data']
            print("\nGPA统计:")
            print(f"总学分: {gpa_data['total_credit']}")
            print(f"GPA: {gpa_data['gpa']}")
            print(f"加权平均分: {gpa_data['weighted_avg']}")
        
        input("\n按回车键继续...")
    
    def show_course_grades(self):
        """显示课程成绩界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("查看课程成绩")
        
        # 输入课程编号
        course_id = input("请输入课程编号: ").strip()
        if not course_id:
            self.cli_view.show_message("课程编号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取课程信息
        if self.course_controller:
            course_result = self.course_controller.get_course(course_id)
            if not course_result['success']:
                self.cli_view.show_message(course_result['message'], "error")
                input("\n按回车键继续...")
                return
            
            course = course_result['data']
            print(f"\n课程信息: {course['course_name']} ({course['course_id']}), 学分: {course['credit']}")
        
        # 输入学期
        semester = input("\n请输入学期 (例如: 2023-2024-1): ").strip()
        if not semester:
            self.cli_view.show_message("学期不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取课程成绩
        result = self.grade_controller.get_course_grades(course_id, semester)
        
        if not result['success']:
            self.cli_view.show_message(result['message'], "error")
            input("\n按回车键继续...")
            return
        
        grades = result['data']['items']
        
        if not grades:
            self.cli_view.show_message(f"没有找到该课程在 {semester} 学期的成绩记录！", "info")
            input("\n按回车键继续...")
            return
        
        # 显示成绩记录
        print(f"\n{semester} 学期 {course_id} 课程成绩记录:")
        print(f"{'学号':<15} {'姓名':<10} {'班级':<15} {'成绩':<5} {'绩点':<5}")
        print("-" * 60)
        
        for grade in grades:
            print(f"{grade['student_id']:<15} {grade.get('student_name', ''):<10} {grade.get('class_name', ''):<15} {grade['score']:<5} {grade.get('grade_point', ''):<5}")
        
        # 获取课程统计信息
        stats_result = self.grade_controller.get_course_statistics(course_id, semester)
        if stats_result['success']:
            stats = stats_result['data']
            print("\n成绩统计:")
            print(f"总人数: {stats['total_students']}")
            print(f"最高分: {stats['max_score']}")
            print(f"最低分: {stats['min_score']}")
            print(f"平均分: {stats['avg_score']}")
            print(f"及格率: {stats['pass_rate']}%")
            
            print("\n分数段分布:")
            for score_range, count in stats.get('score_distribution', {}).items():
                print(f"{score_range}: {count}人")
        
        input("\n按回车键继续...")
    
    def show_add_grade(self):
        """显示添加成绩界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("添加成绩记录")
        
        # 收集成绩信息
        grade_data = {}
        
        grade_data['student_id'] = input("学生学号 (必填): ").strip()
        if not grade_data['student_id']:
            self.cli_view.show_message("学生学号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 验证学生是否存在
        if self.student_controller:
            student_result = self.student_controller.get_student(grade_data['student_id'])
            if not student_result['success']:
                self.cli_view.show_message(student_result['message'], "error")
                input("\n按回车键继续...")
                return
            
            student = student_result['data']
            print(f"学生信息: {student['name']} ({student['student_id']}), 班级: {student.get('class_name', '未知')}")
        
        grade_data['course_id'] = input("课程编号 (必填): ").strip()
        if not grade_data['course_id']:
            self.cli_view.show_message("课程编号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 验证课程是否存在
        if self.course_controller:
            course_result = self.course_controller.get_course(grade_data['course_id'])
            if not course_result['success']:
                self.cli_view.show_message(course_result['message'], "error")
                input("\n按回车键继续...")
                return
            
            course = course_result['data']
            print(f"课程信息: {course['course_name']} ({course['course_id']}), 学分: {course['credit']}")
        
        grade_data['semester'] = input("学期 (必填，例如: 2023-2024-1): ").strip()
        if not grade_data['semester']:
            self.cli_view.show_message("学期不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        score = input("成绩 (必填，0-100): ").strip()
        if not score:
            self.cli_view.show_message("成绩不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        try:
            grade_data['score'] = float(score)
            if grade_data['score'] < 0 or grade_data['score'] > 100:
                self.cli_view.show_message("成绩必须在0-100之间！", "error")
                input("\n按回车键继续...")
                return
        except ValueError:
            self.cli_view.show_message("成绩必须为数字！", "error")
            input("\n按回车键继续...")
            return
        
        # 确认添加
        print("\n成绩信息:")
        for key, value in grade_data.items():
            print(f"{key}: {value}")
        
        if not self.cli_view.show_confirmation("确认添加该成绩记录?"):
            self.cli_view.show_message("已取消添加成绩记录！", "info")
            input("\n按回车键继续...")
            return
        
        # 添加成绩
        result = self.grade_controller.add_grade(grade_data)
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")
    
    def show_edit_grade(self):
        """显示修改成绩界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("修改成绩记录")
        
        # 输入学生学号、课程编号和学期
        student_id = input("请输入学生学号: ").strip()
        if not student_id:
            self.cli_view.show_message("学生学号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        course_id = input("请输入课程编号: ").strip()
        if not course_id:
            self.cli_view.show_message("课程编号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        semester = input("请输入学期 (例如: 2023-2024-1): ").strip()
        if not semester:
            self.cli_view.show_message("学期不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取成绩记录
        # 这里假设 grade_controller 有一个 get_grade_by_keys 方法
        # 如果没有，可以通过 get_student_grades 方法获取学生成绩，然后筛选出对应课程和学期的成绩
        student_grades_result = self.grade_controller.get_student_grades(student_id)
        if not student_grades_result['success']:
            self.cli_view.show_message(student_grades_result['message'], "error")
            input("\n按回车键继续...")
            return
        
        found_grade = None
        for grade in student_grades_result['data']['items']:
            if grade['course_id'] == course_id and grade['semester'] == semester:
                found_grade = grade
                break
        
        if not found_grade:
            self.cli_view.show_message(f"未找到该学生在 {semester} 学期 {course_id} 课程的成绩记录！", "error")
            input("\n按回车键继续...")
            return
        
        # 显示当前成绩信息
        print("\n当前成绩信息:")
        print(f"学生: {found_grade.get('student_name', student_id)} ({student_id})")
        print(f"课程: {found_grade.get('course_name', course_id)} ({course_id})")
        print(f"学期: {semester}")
        print(f"成绩: {found_grade['score']}")
        
        # 输入新成绩
        new_score = input("\n请输入新成绩 (0-100): ").strip()
        if not new_score:
            self.cli_view.show_message("新成绩不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        try:
            score_value = float(new_score)
            if score_value < 0 or score_value > 100:
                self.cli_view.show_message("成绩必须在0-100之间！", "error")
                input("\n按回车键继续...")
                return
        except ValueError:
            self.cli_view.show_message("成绩必须为数字！", "error")
            input("\n按回车键继续...")
            return
        
        # 确认修改
        if not self.cli_view.show_confirmation(f"确认将成绩从 {found_grade['score']} 修改为 {new_score}?"):
            self.cli_view.show_message("已取消修改成绩！", "info")
            input("\n按回车键继续...")
            return
        
        # 更新成绩
        update_data = {'score': score_value}
        result = self.grade_controller.update_grade_by_keys(student_id, course_id, semester, update_data)
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")
    
    def show_delete_grade(self):
        """显示删除成绩界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("删除成绩记录")
        
        # 输入学生学号、课程编号和学期
        student_id = input("请输入学生学号: ").strip()
        if not student_id:
            self.cli_view.show_message("学生学号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        course_id = input("请输入课程编号: ").strip()
        if not course_id:
            self.cli_view.show_message("课程编号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        semester = input("请输入学期 (例如: 2023-2024-1): ").strip()
        if not semester:
            self.cli_view.show_message("学期不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取成绩记录
        student_grades_result = self.grade_controller.get_student_grades(student_id)
        if not student_grades_result['success']:
            self.cli_view.show_message(student_grades_result['message'], "error")
            input("\n按回车键继续...")
            return
        
        found_grade = None
        for grade in student_grades_result['data']['items']:
            if grade['course_id'] == course_id and grade['semester'] == semester:
                found_grade = grade
                break
        
        if not found_grade:
            self.cli_view.show_message(f"未找到该学生在 {semester} 学期 {course_id} 课程的成绩记录！", "error")
            input("\n按回车键继续...")
            return
        
        # 显示成绩信息
        print("\n成绩信息:")
        print(f"学生: {found_grade.get('student_name', student_id)} ({student_id})")
        print(f"课程: {found_grade.get('course_name', course_id)} ({course_id})")
        print(f"学期: {semester}")
        print(f"成绩: {found_grade['score']}")
        
        # 确认删除
        if not self.cli_view.show_confirmation("确认删除该成绩记录? 此操作不可恢复!"):
            self.cli_view.show_message("已取消删除成绩记录！", "info")
            input("\n按回车键继续...")
            return
        
        # 删除成绩
        # 这里假设 grade_controller 有一个 delete_grade_by_keys 方法
        # 如果没有，可以通过 grade_id 删除成绩
        if 'id' in found_grade:
            result = self.grade_controller.delete_grade(found_grade['id'])
        else:
            self.cli_view.show_message("无法删除成绩记录，未找到成绩ID！", "error")
            input("\n按回车键继续...")
            return
        
        self.cli_view.show_message(result['message'], "success" if result['success'] else "error")
        input("\n按回车键继续...")
    
    def show_grade_statistics(self):
        """显示成绩统计分析界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("成绩统计分析")
        
        print("1. 学生GPA分析")
        print("2. 课程成绩分析")
        print("0. 返回")
        print()
        
        choice = input("请选择操作 [0-2]: ").strip()
        
        if choice == "1":
            self.show_student_gpa_analysis()
        elif choice == "2":
            self.show_course_grade_analysis()
        elif choice == "0":
            return
        else:
            self.cli_view.show_message("无效的选择，请重新输入！", "warning")
            input("\n按回车键继续...")
            self.show_grade_statistics()
    
    def show_student_gpa_analysis(self):
        """显示学生GPA分析界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("学生GPA分析")
        
        # 输入学号
        student_id = input("请输入学生学号: ").strip()
        if not student_id:
            self.cli_view.show_message("学号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取学生信息
        if self.student_controller:
            student_result = self.student_controller.get_student(student_id)
            if not student_result['success']:
                self.cli_view.show_message(student_result['message'], "error")
                input("\n按回车键继续...")
                return
            
            student = student_result['data']
            print(f"\n学生信息: {student['name']} ({student['student_id']}), 班级: {student.get('class_name', '未知')}")
        
        # 计算总体GPA
        gpa_result = self.grade_controller.calculate_student_gpa(student_id)
        if not gpa_result['success']:
            self.cli_view.show_message(gpa_result['message'], "error")
            input("\n按回车键继续...")
            return
        
        gpa_data = gpa_result['data']
        
        print("\n总体GPA统计:")
        print(f"总学分: {gpa_data['total_credit']}")
        print(f"GPA: {gpa_data['gpa']}")
        print(f"加权平均分: {gpa_data['weighted_avg']}")
        
        # 获取学期列表
        student_grades_result = self.grade_controller.get_student_grades(student_id)
        if student_grades_result['success']:
            semesters = set()
            for grade in student_grades_result['data']['items']:
                semesters.add(grade['semester'])
            
            if semesters:
                print("\n各学期GPA:")
                for semester in sorted(semesters):
                    semester_gpa_result = self.grade_controller.calculate_student_gpa(student_id, semester)
                    if semester_gpa_result['success']:
                        semester_gpa_data = semester_gpa_result['data']
                        print(f"{semester}: GPA {semester_gpa_data['gpa']}, 加权平均分 {semester_gpa_data['weighted_avg']}, 学分 {semester_gpa_data['total_credit']}")
        
        input("\n按回车键继续...")
    
    def show_course_grade_analysis(self):
        """显示课程成绩分析界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("课程成绩分析")
        
        # 输入课程编号
        course_id = input("请输入课程编号: ").strip()
        if not course_id:
            self.cli_view.show_message("课程编号不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取课程信息
        if self.course_controller:
            course_result = self.course_controller.get_course(course_id)
            if not course_result['success']:
                self.cli_view.show_message(course_result['message'], "error")
                input("\n按回车键继续...")
                return
            
            course = course_result['data']
            print(f"\n课程信息: {course['course_name']} ({course['course_id']}), 学分: {course['credit']}")
        
        # 输入学期
        semester = input("\n请输入学期 (例如: 2023-2024-1): ").strip()
        if not semester:
            self.cli_view.show_message("学期不能为空！", "error")
            input("\n按回车键继续...")
            return
        
        # 获取课程统计信息
        stats_result = self.grade_controller.get_course_statistics(course_id, semester)
        if not stats_result['success']:
            self.cli_view.show_message(stats_result['message'], "error")
            input("\n按回车键继续...")
            return
        
        stats = stats_result['data']
        
        print(f"\n{semester} 学期 {stats.get('course_name', course_id)} 课程成绩统计:")
        print(f"总人数: {stats['total_students']}")
        print(f"最高分: {stats['max_score']}")
        print(f"最低分: {stats['min_score']}")
        print(f"平均分: {stats['avg_score']}")
        print(f"及格率: {stats['pass_rate']}%")
        
        print("\n分数段分布:")
        for score_range, count in stats.get('score_distribution', {}).items():
            print(f"{score_range}: {count}人 ({count/stats['total_students']*100:.2f}%)")
        
        input("\n按回车键继续...")
    
    def show_import_grades(self):
        """显示导入成绩数据界面"""
        self.cli_view.clear_screen()
        self.cli_view.show_header("导入成绩数据")
        
        self.cli_view.show_message("此功能需要准备CSV文件，然后通过程序导入。", "info")
        self.cli_view.show_message("CSV文件格式应包含以下字段: student_id,course_id,semester,score", "info")
        
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
            grades_data = []
            
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    grades_data.append(row)
            
            if not grades_data:
                self.cli_view.show_message("CSV文件中没有数据！", "error")
                input("\n按回车键继续...")
                return
            
            # 确认导入
            print(f"\n找到 {len(grades_data)} 条成绩记录，前5条记录预览:")
            for i, grade in enumerate(grades_data[:5]):
                print(f"{i+1}. 学号: {grade.get('student_id', '')}, 课程: {grade.get('course_id', '')}, 学期: {grade.get('semester', '')}, 成绩: {grade.get('score', '')}")
            
            if not self.cli_view.show_confirmation("确认导入这些成绩数据?"):
                self.cli_view.show_message("已取消导入成绩数据！", "info")
                input("\n按回车键继续...")
                return
            
            # 导入成绩数据
            result = self.grade_controller.import_grades(grades_data)
            
            if result['success']:
                self.cli_view.show_message(result['message'], "success")
                
                # 显示导入结果
                data = result['data']
                print(f"\n成功导入: {data['success_count']} 条记录")
                print(f"导入失败: {data['failed_count']} 条记录")
                
                if data['failed_count'] > 0 and self.cli_view.show_confirmation("是否查看失败记录详情?"):
                    print("\n失败记录详情:")
                    for i, record in enumerate(data['failed_records']):
                        print(f"{i+1}. 学号: {record['data'].get('student_id', '')}, 课程: {record['data'].get('course_id', '')}")
                        print(f"   原因: {record['reason']}")
            else:
                self.cli_view.show_message(result['message'], "error")
            
            input("\n按回车键继续...")
        except Exception as e:
            self.cli_view.show_message(f"导入过程中出错: {str(e)}", "error")
            input("\n按回车键继续...")