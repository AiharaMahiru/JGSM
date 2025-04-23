"""
成绩控制器模块
"""
import logging
from datetime import datetime

from controllers.base_controller import BaseController
from models.grade import Grade
from models.student import Student
from models.course import Course

logger = logging.getLogger(__name__)

class GradeController(BaseController):
    """成绩控制器类，处理成绩相关的业务逻辑"""
    
    def __init__(self, db, current_user=None):
        """
        初始化成绩控制器
        
        参数:
            db (Database): 数据库实例
            current_user (dict): 当前用户信息
        """
        super().__init__(db, current_user)
        self.grade_model = Grade(self.db)
        self.student_model = Student(self.db)
        self.course_model = Course(self.db)
    
    def add_grade(self, grade_data):
        """
        添加新成绩
        
        参数:
            grade_data (dict): 成绩信息
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('teacher'):
            return self.format_response(False, message="权限不足，需要教师或管理员权限")
        
        # 验证必填字段
        required_fields = ['student_id', 'course_id', 'semester', 'score']
        valid, error_message = self.validate_required_fields(grade_data, required_fields)
        if not valid:
            return self.format_response(False, message=error_message)
        
        # 验证学生是否存在
        student = self.student_model.get_student(grade_data['student_id'])
        if not student:
            return self.format_response(False, message=f"未找到学号为 {grade_data['student_id']} 的学生")
        
        # 验证课程是否存在
        course = self.course_model.get_course(grade_data['course_id'])
        if not course:
            return self.format_response(False, message=f"未找到课程编号为 {grade_data['course_id']} 的课程")
        
        # 验证分数
        try:
            score = float(grade_data['score'])
            if score < 0 or score > 100:
                return self.format_response(False, message="分数必须在0-100之间")
            grade_data['score'] = score
        except ValueError:
            return self.format_response(False, message="分数必须为数字")
        
        # 添加成绩
        success = self.grade_model.add_grade(grade_data)
        
        if success:
            # 记录操作日志
            self.log_operation(
                operation="添加成绩",
                target=f"学生 {student['name']} 的 {course['course_name']} 课程成绩",
                details=f"添加了学生 {student['name']}({grade_data['student_id']}) 在 {grade_data['semester']} 学期 {course['course_name']}({grade_data['course_id']}) 课程的成绩: {grade_data['score']}"
            )
            return self.format_response(True, message=f"成功添加成绩")
        else:
            return self.format_response(False, message="添加成绩失败，可能是该学生在该学期已有该课程的成绩记录")
    
    def update_grade(self, grade_id, update_data):
        """
        更新成绩
        
        参数:
            grade_id (int): 成绩记录ID
            update_data (dict): 更新的成绩信息
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('teacher'):
            return self.format_response(False, message="权限不足，需要教师或管理员权限")
        
        # 获取成绩记录
        grade = self.grade_model.get_grade(grade_id)
        if not grade:
            return self.format_response(False, message=f"未找到ID为 {grade_id} 的成绩记录")
        
        # 验证分数
        if 'score' in update_data:
            try:
                score = float(update_data['score'])
                if score < 0 or score > 100:
                    return self.format_response(False, message="分数必须在0-100之间")
                update_data['score'] = score
            except ValueError:
                return self.format_response(False, message="分数必须为数字")
        
        # 更新成绩
        success = self.grade_model.update_grade(grade_id, update_data)
        
        if success:
            # 获取学生和课程信息用于日志记录
            student = self.student_model.get_student(grade['student_id'])
            course = self.course_model.get_course(grade['course_id'])
            
            # 记录操作日志
            self.log_operation(
                operation="更新成绩",
                target=f"学生 {student['name']} 的 {course['course_name']} 课程成绩",
                details=f"更新了学生 {student['name']}({grade['student_id']}) 在 {grade['semester']} 学期 {course['course_name']}({grade['course_id']}) 课程的成绩: {update_data}"
            )
            return self.format_response(True, message=f"成功更新成绩")
        else:
            return self.format_response(False, message="更新成绩失败")
    
    def update_grade_by_keys(self, student_id, course_id, semester, update_data):
        """
        通过学号、课程编号和学期更新成绩
        
        参数:
            student_id (str): 学号
            course_id (str): 课程编号
            semester (str): 学期
            update_data (dict): 更新的成绩信息
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('teacher'):
            return self.format_response(False, message="权限不足，需要教师或管理员权限")
        
        # 获取成绩记录
        grade = self.grade_model.get_grade_by_keys(student_id, course_id, semester)
        if not grade:
            return self.format_response(False, message=f"未找到对应的成绩记录")
        
        # 验证分数
        if 'score' in update_data:
            try:
                score = float(update_data['score'])
                if score < 0 or score > 100:
                    return self.format_response(False, message="分数必须在0-100之间")
                update_data['score'] = score
            except ValueError:
                return self.format_response(False, message="分数必须为数字")
        
        # 更新成绩
        success = self.grade_model.update_grade_by_keys(student_id, course_id, semester, update_data)
        
        if success:
            # 获取学生和课程信息用于日志记录
            student = self.student_model.get_student(student_id)
            course = self.course_model.get_course(course_id)
            
            # 记录操作日志
            self.log_operation(
                operation="更新成绩",
                target=f"学生 {student['name']} 的 {course['course_name']} 课程成绩",
                details=f"更新了学生 {student['name']}({student_id}) 在 {semester} 学期 {course['course_name']}({course_id}) 课程的成绩: {update_data}"
            )
            return self.format_response(True, message=f"成功更新成绩")
        else:
            return self.format_response(False, message="更新成绩失败")
    
    def delete_grade(self, grade_id):
        """
        删除成绩记录
        
        参数:
            grade_id (int): 成绩记录ID
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin'):
            return self.format_response(False, message="权限不足，需要管理员权限")
        
        # 获取成绩记录
        grade = self.grade_model.get_grade(grade_id)
        if not grade:
            return self.format_response(False, message=f"未找到ID为 {grade_id} 的成绩记录")
        
        # 获取学生和课程信息用于日志记录
        student = self.student_model.get_student(grade['student_id'])
        course = self.course_model.get_course(grade['course_id'])
        
        # 删除成绩
        success = self.grade_model.delete_grade(grade_id)
        
        if success:
            # 记录操作日志
            self.log_operation(
                operation="删除成绩",
                target=f"学生 {student['name']} 的 {course['course_name']} 课程成绩",
                details=f"删除了学生 {student['name']}({grade['student_id']}) 在 {grade['semester']} 学期 {course['course_name']}({grade['course_id']}) 课程的成绩"
            )
            return self.format_response(True, message=f"成功删除成绩记录")
        else:
            return self.format_response(False, message="删除成绩记录失败")
    
    def get_student_grades(self, student_id, semester=None, page=1, page_size=20):
        """
        获取学生成绩
        
        参数:
            student_id (str): 学号
            semester (str, optional): 学期
            page (int): 页码
            page_size (int): 每页大小
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('student'):
            return self.format_response(False, message="权限不足，需要登录")
        
        # 如果当前用户是学生，只能查看自己的成绩
        if self.user_role == 'student' and self.username != student_id:
            return self.format_response(False, message="权限不足，学生只能查看自己的成绩")
        
        # 验证学生是否存在
        student = self.student_model.get_student(student_id)
        if not student:
            return self.format_response(False, message=f"未找到学号为 {student_id} 的学生")
        
        # 获取学生成绩
        grades = self.grade_model.get_student_grades(student_id, semester)
        
        # 对结果进行分页
        paginated_results = self.paginate(grades, page, page_size)
        
        # 添加学生信息
        paginated_results['student'] = student
        
        return self.format_response(True, data=paginated_results)
    
    def get_course_grades(self, course_id, semester, page=1, page_size=20):
        """
        获取课程成绩
        
        参数:
            course_id (str): 课程编号
            semester (str): 学期
            page (int): 页码
            page_size (int): 每页大小
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('teacher'):
            return self.format_response(False, message="权限不足，需要教师或管理员权限")
        
        # 验证课程是否存在
        course = self.course_model.get_course(course_id)
        if not course:
            return self.format_response(False, message=f"未找到课程编号为 {course_id} 的课程")
        
        # 获取课程成绩
        grades = self.grade_model.get_course_grades(course_id, semester)
        
        # 对结果进行分页
        paginated_results = self.paginate(grades, page, page_size)
        
        # 添加课程信息
        paginated_results['course'] = course
        paginated_results['semester'] = semester
        
        return self.format_response(True, data=paginated_results)
    
    def calculate_student_gpa(self, student_id, semester=None):
        """
        计算学生GPA
        
        参数:
            student_id (str): 学号
            semester (str, optional): 学期
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('student'):
            return self.format_response(False, message="权限不足，需要登录")
        
        # 如果当前用户是学生，只能查看自己的GPA
        if self.user_role == 'student' and self.username != student_id:
            return self.format_response(False, message="权限不足，学生只能查看自己的GPA")
        
        # 验证学生是否存在
        student = self.student_model.get_student(student_id)
        if not student:
            return self.format_response(False, message=f"未找到学号为 {student_id} 的学生")
        
        # 计算GPA
        gpa_data = self.grade_model.calculate_student_gpa(student_id, semester)
        
        # 添加学生信息
        gpa_data['student_name'] = student['name']
        gpa_data['class_name'] = student['class_name']
        
        return self.format_response(True, data=gpa_data)
    
    def get_course_statistics(self, course_id, semester):
        """
        获取课程统计信息
        
        参数:
            course_id (str): 课程编号
            semester (str): 学期
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('teacher'):
            return self.format_response(False, message="权限不足，需要教师或管理员权限")
        
        # 验证课程是否存在
        course = self.course_model.get_course(course_id)
        if not course:
            return self.format_response(False, message=f"未找到课程编号为 {course_id} 的课程")
        
        # 获取课程统计信息
        stats = self.grade_model.get_course_statistics(course_id, semester)
        
        # 添加课程信息
        stats['course_name'] = course['course_name']
        stats['teacher'] = course['teacher']
        stats['credit'] = course['credit']
        
        return self.format_response(True, data=stats)
    
    def import_grades(self, grades_data):
        """
        批量导入成绩
        
        参数:
            grades_data (list): 成绩数据列表
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('teacher'):
            return self.format_response(False, message="权限不足，需要教师或管理员权限")
        
        if not grades_data:
            return self.format_response(False, message="没有提供成绩数据")
        
        success_count = 0
        failed_count = 0
        failed_records = []
        
        for grade_data in grades_data:
            # 验证必填字段
            required_fields = ['student_id', 'course_id', 'semester', 'score']
            valid, error_message = self.validate_required_fields(grade_data, required_fields)
            
            if not valid:
                failed_count += 1
                failed_records.append({
                    'data': grade_data,
                    'reason': error_message
                })
                continue
            
            # 验证学生是否存在
            student = self.student_model.get_student(grade_data['student_id'])
            if not student:
                failed_count += 1
                failed_records.append({
                    'data': grade_data,
                    'reason': f"未找到学号为 {grade_data['student_id']} 的学生"
                })
                continue
            
            # 验证课程是否存在
            course = self.course_model.get_course(grade_data['course_id'])
            if not course:
                failed_count += 1
                failed_records.append({
                    'data': grade_data,
                    'reason': f"未找到课程编号为 {grade_data['course_id']} 的课程"
                })
                continue
            
            # 验证分数
            try:
                score = float(grade_data['score'])
                if score < 0 or score > 100:
                    failed_count += 1
                    failed_records.append({
                        'data': grade_data,
                        'reason': "分数必须在0-100之间"
                    })
                    continue
                grade_data['score'] = score
            except ValueError:
                failed_count += 1
                failed_records.append({
                    'data': grade_data,
                    'reason': "分数必须为数字"
                })
                continue
            
            # 添加成绩
            if self.grade_model.add_grade(grade_data):
                success_count += 1
            else:
                failed_count += 1
                failed_records.append({
                    'data': grade_data,
                    'reason': "添加失败，可能是该学生在该学期已有该课程的成绩记录"
                })
        
        # 记录操作日志
        self.log_operation(
            operation="批量导入成绩",
            target="成绩批量导入",
            details=f"成功导入 {success_count} 条成绩记录，失败 {failed_count} 条"
        )
        
        return self.format_response(
            True,
            data={
                'success_count': success_count,
                'failed_count': failed_count,
                'failed_records': failed_records
            },
            message=f"成功导入 {success_count} 条成绩记录，失败 {failed_count} 条"
        )
        
    def get_all_grades(self, filters=None, page=1, page_size=20, order_by='id'):
        """
        获取成绩列表
        
        参数:
            filters (dict): 过滤条件
            page (int): 页码
            page_size (int): 每页大小
            order_by (str): 排序字段
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('student'):
            return self.format_response(False, message="权限不足，需要登录")
        
        # 如果当前用户是学生，只能查看自己的成绩
        if self.user_role == 'student':
            if not filters:
                filters = {}
            filters['student_id'] = self.username
        
        try:
            # 获取成绩总数
            total = self.grade_model.count_grades(filters)
            
            # 计算分页参数
            offset = (page - 1) * page_size
            
            # 获取成绩列表
            grades = self.grade_model.get_grades(
                filters=filters,
                order_by=order_by,
                limit=page_size,
                offset=offset
            )
            
            # 构建分页结果
            pagination = {
                'items': grades,
                'page': page,
                'page_size': page_size,
                'total_items': total,
                'total_pages': (total + page_size - 1) // page_size
            }
            
            return self.format_response(True, data=pagination)
        except Exception as e:
            logger.error(f"获取成绩列表失败: {e}")
            return self.format_response(False, message=f"获取成绩列表失败: {str(e)}")
            
    def get_grade(self, grade_id):
        """
        获取成绩详情
        
        参数:
            grade_id (int): 成绩ID
            
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('student'):
            return self.format_response(False, message="权限不足，需要登录")
            
        try:
            # 获取成绩详情
            grade = self.grade_model.get_grade(grade_id)
            
            if not grade:
                return self.format_response(False, message=f"未找到ID为 {grade_id} 的成绩记录")
                
            # 如果当前用户是学生，只能查看自己的成绩
            if self.user_role == 'student' and grade['student_id'] != self.username:
                return self.format_response(False, message="权限不足，学生只能查看自己的成绩")
                
            return self.format_response(True, data=grade)
        except Exception as e:
            logger.error(f"获取成绩详情失败: {e}")
            return self.format_response(False, message=f"获取成绩详情失败: {str(e)}")
            
    def get_grade_statistics(self, filters=None):
        """
        获取成绩统计数据
        
        参数:
            filters (dict): 过滤条件
            
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('teacher'):
            return self.format_response(False, message="权限不足，需要教师或管理员权限")
            
        try:
            # 获取成绩统计数据
            stats = self.grade_model.get_statistics(filters)
            return self.format_response(True, data=stats)
        except Exception as e:
            logger.error(f"获取成绩统计数据失败: {e}")
            return self.format_response(False, message=f"获取成绩统计数据失败: {str(e)}")