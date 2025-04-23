"""
课程控制器模块
"""
import logging
from datetime import datetime
import re

from controllers.base_controller import BaseController
from models.course import Course

logger = logging.getLogger(__name__)

class CourseController(BaseController):
    """课程控制器类，处理课程相关的业务逻辑"""
    
    def __init__(self, db, current_user=None):
        """
        初始化课程控制器
        
        参数:
            db (Database): 数据库实例
            current_user (dict): 当前用户信息
        """
        super().__init__(db, current_user)
        self.course_model = Course(self.db)
    
    def add_course(self, course_data):
        """
        添加新课程
        
        参数:
            course_data (dict): 课程信息
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('teacher'):
            return self.format_response(False, message="权限不足，需要教师或管理员权限")
        
        # 验证必填字段
        required_fields = ['course_id', 'course_name', 'credit']
        valid, error_message = self.validate_required_fields(course_data, required_fields)
        if not valid:
            return self.format_response(False, message=error_message)
        
        # 验证课程编号格式
        if not self._validate_course_id(course_data['course_id']):
            return self.format_response(False, message="课程编号格式不正确，应为字母和数字的组合")
            
        # 检查课程编号是否已存在
        existing_course = self.course_model.get_course(course_data['course_id'])
        if existing_course:
            return self.format_response(False, message=f"课程编号 {course_data['course_id']} 已存在，请使用其他编号")
        
        # 验证学分
        try:
            credit = float(course_data['credit'])
            if credit <= 0:
                return self.format_response(False, message="学分必须为正数")
            course_data['credit'] = credit
        except ValueError:
            return self.format_response(False, message="学分必须为数字")
        
        # 添加创建时间和更新时间
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        course_data['created_at'] = now
        course_data['updated_at'] = now
        
        # 添加课程
        success, error_msg = self.course_model.add_course(course_data)
        
        if success:
            # 记录操作日志
            self.log_operation(
                operation="添加课程",
                target=f"课程: {course_data['course_name']}({course_data['course_id']})",
                details=f"添加了课程 {course_data['course_name']}，编号 {course_data['course_id']}"
            )
            return self.format_response(True, message=f"成功添加课程: {course_data['course_name']}")
        else:
            # 使用模型返回的具体错误信息
            return self.format_response(False, message=error_msg or "添加课程失败，请稍后重试或联系管理员")
    
    def update_course(self, course_id, update_data):
        """
        更新课程信息
        
        参数:
            course_id (str): 课程编号
            update_data (dict): 更新的课程信息
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('teacher'):
            return self.format_response(False, message="权限不足，需要教师或管理员权限")
        
        # 检查课程是否存在
        course = self.course_model.get_course(course_id)
        if not course:
            return self.format_response(False, message=f"未找到课程编号为 {course_id} 的课程")
        
        # 验证学分
        if 'credit' in update_data:
            try:
                credit = float(update_data['credit'])
                if credit <= 0:
                    return self.format_response(False, message="学分必须为正数")
                update_data['credit'] = credit
            except ValueError:
                return self.format_response(False, message="学分必须为数字")
        
        # 更新课程信息
        success = self.course_model.update_course(course_id, update_data)
        
        if success:
            # 记录操作日志
            self.log_operation(
                operation="更新课程信息",
                target=f"课程: {course['course_name']}({course_id})",
                details=f"更新了课程 {course['course_name']} 的信息: {update_data}"
            )
            return self.format_response(True, message=f"成功更新课程信息: {course['course_name']}")
        else:
            return self.format_response(False, message="更新课程信息失败")
    
    def delete_course(self, course_id):
        """
        删除课程
        
        参数:
            course_id (str): 课程编号
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin'):
            return self.format_response(False, message="权限不足，需要管理员权限")
        
        # 检查课程是否存在
        course = self.course_model.get_course(course_id)
        if not course:
            return self.format_response(False, message=f"未找到课程编号为 {course_id} 的课程")
        
        # 删除课程
        success = self.course_model.delete_course(course_id)
        
        if success:
            # 记录操作日志
            self.log_operation(
                operation="删除课程",
                target=f"课程: {course['course_name']}({course_id})",
                details=f"删除了课程 {course['course_name']}，编号 {course_id}"
            )
            return self.format_response(True, message=f"成功删除课程: {course['course_name']}")
        else:
            return self.format_response(False, message="删除课程失败")
    
    def get_course(self, course_id):
        """
        获取课程信息
        
        参数:
            course_id (str): 课程编号
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('student'):
            return self.format_response(False, message="权限不足，需要登录")
        
        # 获取课程信息
        course = self.course_model.get_course(course_id)
        
        if course:
            return self.format_response(True, data=course)
        else:
            return self.format_response(False, message=f"未找到课程编号为 {course_id} 的课程")
    
    def get_all_courses(self, filters=None, page=1, page_size=20, order_by='course_name'):
        """
        获取课程列表
        
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
        
        # 获取课程总数
        total = self.course_model.count_courses(filters)
        
        # 计算分页参数
        offset = (page - 1) * page_size
        
        # 获取课程列表
        courses = self.course_model.get_all_courses(
            filters=filters,
            order_by=order_by,
            limit=page_size,
            offset=offset
        )
        
        # 构建分页结果
        pagination = {
            'items': courses,
            'page': page,
            'page_size': page_size,
            'total_items': total,
            'total_pages': (total + page_size - 1) // page_size
        }
        
        return self.format_response(True, data=pagination)
    
    def search_courses(self, keyword, page=1, page_size=20):
        """
        搜索课程
        
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
        
        # 搜索课程
        courses = self.course_model.search_courses(keyword)
        
        # 对结果进行分页
        paginated_results = self.paginate(courses, page, page_size)
        
        return self.format_response(True, data=paginated_results)
    
    def import_courses(self, courses_data):
        """
        批量导入课程
        
        参数:
            courses_data (list): 课程数据列表
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin'):
            return self.format_response(False, message="权限不足，需要管理员权限")
        
        if not courses_data:
            return self.format_response(False, message="没有提供课程数据")
        
        success_count = 0
        failed_count = 0
        failed_records = []
        
        # 添加创建时间和更新时间
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for course_data in courses_data:
            # 验证必填字段
            required_fields = ['course_id', 'course_name', 'credit']
            valid, error_message = self.validate_required_fields(course_data, required_fields)
            
            if not valid:
                failed_count += 1
                failed_records.append({
                    'data': course_data,
                    'reason': error_message
                })
                continue
            
            # 验证课程编号格式
            if not self._validate_course_id(course_data['course_id']):
                failed_count += 1
                failed_records.append({
                    'data': course_data,
                    'reason': "课程编号格式不正确，应为字母和数字的组合"
                })
                continue
                
            # 检查课程编号是否已存在
            existing_course = self.course_model.get_course(course_data['course_id'])
            if existing_course:
                failed_count += 1
                failed_records.append({
                    'data': course_data,
                    'reason': f"课程编号 {course_data['course_id']} 已存在，请使用其他编号"
                })
                continue
            
            # 验证学分
            try:
                credit = float(course_data['credit'])
                if credit <= 0:
                    failed_count += 1
                    failed_records.append({
                        'data': course_data,
                        'reason': "学分必须为正数"
                    })
                    continue
                course_data['credit'] = credit
            except ValueError:
                failed_count += 1
                failed_records.append({
                    'data': course_data,
                    'reason': "学分必须为数字"
                })
                continue
            
            # 添加时间戳
            course_data['created_at'] = now
            course_data['updated_at'] = now
            
            # 添加课程
            success, error_msg = self.course_model.add_course(course_data)
            if success:
                success_count += 1
            else:
                failed_count += 1
                failed_records.append({
                    'data': course_data,
                    'reason': error_msg or "添加失败，未知错误"
                })
        
        # 记录操作日志
        self.log_operation(
            operation="批量导入课程",
            target="课程批量导入",
            details=f"成功导入 {success_count} 门课程，失败 {failed_count} 门"
        )
        
        return self.format_response(
            True,
            data={
                'success_count': success_count,
                'failed_count': failed_count,
                'failed_records': failed_records
            },
            message=f"成功导入 {success_count} 门课程，失败 {failed_count} 门"
        )
    
    def _validate_course_id(self, course_id):
        """
        验证课程编号格式
        
        参数:
            course_id (str): 课程编号
        
        返回:
            bool: 格式正确返回True，否则返回False
        """
        # 课程编号应为字母和数字的组合，长度在2-20之间
        pattern = r'^[A-Za-z0-9]{2,20}$'
        return bool(re.match(pattern, course_id))
        
    def get_semester_list(self):
        """
        获取所有学期列表
        
        返回:
            dict: 响应结果，包含学期列表
        """
        # 检查权限
        if not self.check_permission('student'):
            return self.format_response(False, message="权限不足，需要登录")
        
        try:
            # 查询所有不同的学期
            self.db.execute("""
            SELECT DISTINCT semester
            FROM grades
            WHERE semester IS NOT NULL AND semester != ''
            ORDER BY semester DESC
            """)
            
            semesters = [row['semester'] for row in self.db.fetchall()]
            return self.format_response(True, data=semesters)
        except Exception as e:
            logger.error(f"获取学期列表失败: {e}")
            return self.format_response(False, message=f"获取学期列表失败: {str(e)}")