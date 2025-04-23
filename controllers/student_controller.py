"""
学生控制器模块
"""
import logging
from datetime import datetime
import re

from controllers.base_controller import BaseController
from models.student import Student

logger = logging.getLogger(__name__)

class StudentController(BaseController):
    """学生控制器类，处理学生相关的业务逻辑"""
    
    def __init__(self, db, current_user=None):
        """
        初始化学生控制器
        
        参数:
            db (Database): 数据库实例
            current_user (dict): 当前用户信息
        """
        super().__init__(db, current_user)
        self.student_model = Student(self.db)
    
    def add_student(self, student_data):
        """
        添加新学生
        
        参数:
            student_data (dict): 学生信息
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('teacher'):
            return self.format_response(False, message="权限不足，需要教师或管理员权限")
        
        # 验证必填字段
        required_fields = ['student_id', 'name']
        valid, error_message = self.validate_required_fields(student_data, required_fields)
        if not valid:
            return self.format_response(False, message=error_message)
        
        # 验证学号格式
        if not self._validate_student_id(student_data['student_id']):
            return self.format_response(False, message="学号格式不正确，应为数字或字母组合")
        
        # 验证电子邮箱格式
        if 'email' in student_data and student_data['email'] and not self._validate_email(student_data['email']):
            return self.format_response(False, message="电子邮箱格式不正确")
        
        # 验证手机号格式
        if 'contact_phone' in student_data and student_data['contact_phone'] and not self._validate_phone(student_data['contact_phone']):
            return self.format_response(False, message="手机号格式不正确")
        
        # 添加创建时间和更新时间
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        student_data['created_at'] = now
        student_data['updated_at'] = now
        
        # 添加学生
        success = self.student_model.add_student(student_data)
        
        if success:
            # 记录操作日志
            self.log_operation(
                operation="添加学生",
                target=f"学生: {student_data['name']}({student_data['student_id']})",
                details=f"添加了学生 {student_data['name']}，学号 {student_data['student_id']}"
            )
            return self.format_response(True, message=f"成功添加学生: {student_data['name']}")
        else:
            return self.format_response(False, message="添加学生失败，可能是学号已存在")
    
    def update_student(self, student_id, update_data):
        """
        更新学生信息
        
        参数:
            student_id (str): 学号
            update_data (dict): 更新的学生信息
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('teacher'):
            return self.format_response(False, message="权限不足，需要教师或管理员权限")
        
        # 检查学生是否存在
        student = self.student_model.get_student(student_id)
        if not student:
            return self.format_response(False, message=f"未找到学号为 {student_id} 的学生")
        
        # 验证电子邮箱格式
        if 'email' in update_data and update_data['email'] and not self._validate_email(update_data['email']):
            return self.format_response(False, message="电子邮箱格式不正确")
        
        # 验证手机号格式
        if 'contact_phone' in update_data and update_data['contact_phone'] and not self._validate_phone(update_data['contact_phone']):
            return self.format_response(False, message="手机号格式不正确")
        
        # 更新学生信息
        success = self.student_model.update_student(student_id, update_data)
        
        if success:
            # 记录操作日志
            self.log_operation(
                operation="更新学生信息",
                target=f"学生: {student['name']}({student_id})",
                details=f"更新了学生 {student['name']} 的信息: {update_data}"
            )
            return self.format_response(True, message=f"成功更新学生信息: {student['name']}")
        else:
            return self.format_response(False, message="更新学生信息失败")
    
    def delete_student(self, student_id):
        """
        删除学生
        
        参数:
            student_id (str): 学号
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin'):
            return self.format_response(False, message="权限不足，需要管理员权限")
        
        # 检查学生是否存在
        student = self.student_model.get_student(student_id)
        if not student:
            return self.format_response(False, message=f"未找到学号为 {student_id} 的学生")
        
        # 删除学生
        success = self.student_model.delete_student(student_id)
        
        if success:
            # 记录操作日志
            self.log_operation(
                operation="删除学生",
                target=f"学生: {student['name']}({student_id})",
                details=f"删除了学生 {student['name']}，学号 {student_id}"
            )
            return self.format_response(True, message=f"成功删除学生: {student['name']}")
        else:
            return self.format_response(False, message="删除学生失败")
    
    def get_student(self, student_id):
        """
        获取学生信息
        
        参数:
            student_id (str): 学号
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('student'):
            return self.format_response(False, message="权限不足，需要登录")
        
        # 获取学生信息
        student = self.student_model.get_student(student_id)
        
        if student:
            return self.format_response(True, data=student)
        else:
            return self.format_response(False, message=f"未找到学号为 {student_id} 的学生")
    
    def get_all_students(self, filters=None, page=1, page_size=20, order_by='name'):
        """
        获取学生列表
        
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
        
        # 获取学生总数
        total = self.student_model.count_students(filters)
        
        # 计算分页参数
        offset = (page - 1) * page_size
        
        # 获取学生列表
        students = self.student_model.get_all_students(
            filters=filters,
            order_by=order_by,
            limit=page_size,
            offset=offset
        )
        
        # 构建分页结果
        pagination = {
            'items': students,
            'page': page,
            'page_size': page_size,
            'total_items': total,
            'total_pages': (total + page_size - 1) // page_size
        }
        
        return self.format_response(True, data=pagination)
    
    def search_students(self, keyword, page=1, page_size=20):
        """
        搜索学生
        
        参数:
            keyword (str): 搜索关键词
            page (int): 页码
            page_size (int): 每页大小
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('student'):
            return self.format_response(False, message="权限不足，需要登录")
        
        # 搜索学生
        students = self.student_model.search_students(keyword)
        
        # 对结果进行分页
        paginated_results = self.paginate(students, page, page_size)
        
        return self.format_response(True, data=paginated_results)
    
    def import_students(self, students_data):
        """
        批量导入学生
        
        参数:
            students_data (list): 学生数据列表
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin'):
            return self.format_response(False, message="权限不足，需要管理员权限")
        
        if not students_data:
            return self.format_response(False, message="没有提供学生数据")
        
        success_count = 0
        failed_count = 0
        failed_records = []
        
        # 添加创建时间和更新时间
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for student_data in students_data:
            # 验证必填字段
            required_fields = ['student_id', 'name']
            valid, error_message = self.validate_required_fields(student_data, required_fields)
            
            if not valid:
                failed_count += 1
                failed_records.append({
                    'data': student_data,
                    'reason': error_message
                })
                continue
            
            # 验证学号格式
            if not self._validate_student_id(student_data['student_id']):
                failed_count += 1
                failed_records.append({
                    'data': student_data,
                    'reason': "学号格式不正确，应为数字或字母组合"
                })
                continue
            
            # 添加时间戳
            student_data['created_at'] = now
            student_data['updated_at'] = now
            
            # 添加学生
            if self.student_model.add_student(student_data):
                success_count += 1
            else:
                failed_count += 1
                failed_records.append({
                    'data': student_data,
                    'reason': "添加失败，可能是学号已存在"
                })
        
        # 记录操作日志
        self.log_operation(
            operation="批量导入学生",
            target="学生批量导入",
            details=f"成功导入 {success_count} 名学生，失败 {failed_count} 名"
        )
        
        return self.format_response(
            True,
            data={
                'success_count': success_count,
                'failed_count': failed_count,
                'failed_records': failed_records
            },
            message=f"成功导入 {success_count} 名学生，失败 {failed_count} 名"
        )
    
    def _validate_student_id(self, student_id):
        """
        验证学号格式
        
        参数:
            student_id (str): 学号
        
        返回:
            bool: 格式正确返回True，否则返回False
        """
        # 学号应为字母和数字的组合，长度在3-20之间
        pattern = r'^[A-Za-z0-9]{3,20}$'
        return bool(re.match(pattern, student_id))
    
    def _validate_email(self, email):
        """
        验证电子邮箱格式
        
        参数:
            email (str): 电子邮箱
        
        返回:
            bool: 格式正确返回True，否则返回False
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_phone(self, phone):
        """
        验证手机号格式
        
        参数:
            phone (str): 手机号
        
        返回:
            bool: 格式正确返回True，否则返回False
        """
        # 简单验证中国大陆手机号
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))
        
    def get_class_list(self):
        """
        获取所有班级列表
        
        返回:
            dict: 响应结果，包含班级列表
        """
        # 检查权限
        if not self.check_permission('student'):
            return self.format_response(False, message="权限不足，需要登录")
        
        try:
            # 查询所有不同的班级名称
            self.db.execute("""
            SELECT DISTINCT class_name
            FROM students
            WHERE class_name IS NOT NULL AND class_name != ''
            ORDER BY class_name
            """)
            
            classes = [row['class_name'] for row in self.db.fetchall()]
            return self.format_response(True, data=classes)
        except Exception as e:
            logger.error(f"获取班级列表失败: {e}")
            return self.format_response(False, message=f"获取班级列表失败: {str(e)}")