"""
课程表控制器模块
"""
import logging
from datetime import datetime

from controllers.base_controller import BaseController
from models.schedule import Schedule
from models.course import Course

logger = logging.getLogger(__name__)

class ScheduleController(BaseController):
    """课程表控制器类，处理课程表相关的业务逻辑"""
    
    def __init__(self, db, current_user=None):
        """
        初始化课程表控制器
        
        参数:
            db (Database): 数据库实例
            current_user (dict): 当前用户信息
        """
        super().__init__(db, current_user)
        self.schedule_model = Schedule(self.db)
        self.course_model = Course(self.db)
    
    def add_schedule_item(self, schedule_data):
        """
        添加课程表项
        
        参数:
            schedule_data (dict): 课程表信息
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('teacher'):
            return self.format_response(False, message="权限不足，需要教师或管理员权限")
        
        # 验证必填字段
        required_fields = ['course_id', 'semester', 'day_of_week', 'start_section', 
                          'end_section', 'location', 'start_week', 'end_week']
        valid, error_message = self.validate_required_fields(schedule_data, required_fields)
        if not valid:
            return self.format_response(False, message=error_message)
        
        # 添加课程表项
        success, error_msg = self.schedule_model.add_schedule_item(schedule_data)
        
        if success:
            # 获取课程名称，用于日志
            course = self.course_model.get_course(schedule_data['course_id'])
            course_name = course['course_name'] if course else schedule_data['course_id']
            
            # 记录操作日志
            self.log_operation(
                operation="添加课程表项",
                target=f"课程: {course_name}",
                details=f"添加了课程 {course_name} 的课程表项，位置：{schedule_data['location']}，" +
                        f"时间：星期{schedule_data['day_of_week']} 第{schedule_data['start_section']}-{schedule_data['end_section']}节，" +
                        f"周次：第{schedule_data['start_week']}-{schedule_data['end_week']}周"
            )
            return self.format_response(True, message=f"成功添加课程表项")
        else:
            # 使用模型返回的具体错误信息
            return self.format_response(False, message=error_msg or "添加课程表项失败，请稍后重试或联系管理员")
    
    def update_schedule_item(self, schedule_id, update_data):
        """
        更新课程表项
        
        参数:
            schedule_id (int): 课程表项ID
            update_data (dict): 更新的课程表信息
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('teacher'):
            return self.format_response(False, message="权限不足，需要教师或管理员权限")
        
        # 检查课程表项是否存在
        schedule_item = self.schedule_model.get_schedule_item(schedule_id)
        if not schedule_item:
            return self.format_response(False, message=f"未找到ID为 {schedule_id} 的课程表项")
        
        # 更新课程表项
        success, error_msg = self.schedule_model.update_schedule_item(schedule_id, update_data)
        
        if success:
            # 获取课程名称，用于日志
            course_id = update_data.get('course_id', schedule_item['course_id'])
            course = self.course_model.get_course(course_id)
            course_name = course['course_name'] if course else course_id
            
            # 记录操作日志
            self.log_operation(
                operation="更新课程表项",
                target=f"课程表项: ID {schedule_id}",
                details=f"更新了课程 {course_name} 的课程表项信息: {update_data}"
            )
            return self.format_response(True, message=f"成功更新课程表项")
        else:
            # 使用模型返回的具体错误信息
            return self.format_response(False, message=error_msg or "更新课程表项失败，请稍后重试或联系管理员")
    
    def delete_schedule_item(self, schedule_id):
        """
        删除课程表项
        
        参数:
            schedule_id (int): 课程表项ID
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('teacher'):
            return self.format_response(False, message="权限不足，需要教师或管理员权限")
        
        # 检查课程表项是否存在
        schedule_item = self.schedule_model.get_schedule_item(schedule_id)
        if not schedule_item:
            return self.format_response(False, message=f"未找到ID为 {schedule_id} 的课程表项")
        
        # 删除课程表项
        success, error_msg = self.schedule_model.delete_schedule_item(schedule_id)
        
        if success:
            # 获取课程名称，用于日志
            course = self.course_model.get_course(schedule_item['course_id'])
            course_name = course['course_name'] if course else schedule_item['course_id']
            
            # 记录操作日志
            self.log_operation(
                operation="删除课程表项",
                target=f"课程表项: ID {schedule_id}",
                details=f"删除了课程 {course_name} 的课程表项，位置：{schedule_item['location']}，" +
                        f"时间：星期{schedule_item['day_of_week']} 第{schedule_item['start_section']}-{schedule_item['end_section']}节"
            )
            return self.format_response(True, message=f"成功删除课程表项")
        else:
            # 使用模型返回的具体错误信息
            return self.format_response(False, message=error_msg or "删除课程表项失败，请稍后重试或联系管理员")
    
    def get_schedule_item(self, schedule_id):
        """
        获取课程表项详情
        
        参数:
            schedule_id (int): 课程表项ID
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('student'):
            return self.format_response(False, message="权限不足，需要登录")
        
        # 获取课程表项
        schedule_item = self.schedule_model.get_schedule_item(schedule_id)
        
        if schedule_item:
            return self.format_response(True, data=schedule_item)
        else:
            return self.format_response(False, message=f"未找到ID为 {schedule_id} 的课程表项")
    
    def get_schedule(self, semester, week=None, day=None, course_id=None):
        """
        获取课程表
        
        参数:
            semester (str): 学期
            week (int): 周次，不提供则获取所有周次
            day (int): 星期几(1-7)，不提供则获取所有天
            course_id (str): 课程编号，不提供则获取所有课程
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('student'):
            return self.format_response(False, message="权限不足，需要登录")
        
        # 构建过滤条件
        filters = {}
        if day:
            try:
                day = int(day)
                if not (1 <= day <= 7):
                    return self.format_response(False, message="星期几必须在1-7之间")
                filters['day_of_week'] = day
            except (ValueError, TypeError):
                return self.format_response(False, message="星期几必须为整数")
                
        if course_id:
            # 检查课程是否存在
            course = self.course_model.get_course(course_id)
            if not course:
                return self.format_response(False, message=f"未找到课程编号为 {course_id} 的课程")
            filters['course_id'] = course_id
        
        # 获取课程表数据
        if week:
            try:
                week = int(week)
                if week <= 0:
                    return self.format_response(False, message="周次必须为正整数")
                schedule_items = self.schedule_model.get_schedule_by_week(semester, week)
            except (ValueError, TypeError):
                return self.format_response(False, message="周次必须为整数")
        else:
            schedule_items = self.schedule_model.get_schedule(semester, filters)
        
        # 格式化数据为前端所需格式
        formatted_data = self._format_schedule_data(schedule_items)
        
        return self.format_response(True, data=formatted_data)
    
    def get_course_schedules(self, course_id, semester=None):
        """
        获取指定课程的所有课程表项
        
        参数:
            course_id (str): 课程编号
            semester (str, optional): 学期
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('student'):
            return self.format_response(False, message="权限不足，需要登录")
        
        # 检查课程是否存在
        course = self.course_model.get_course(course_id)
        if not course:
            return self.format_response(False, message=f"未找到课程编号为 {course_id} 的课程")
        
        # 获取课程表项
        schedule_items = self.schedule_model.get_course_schedules(course_id, semester)
        
        return self.format_response(True, data=schedule_items)
    
    def get_semesters(self):
        """
        获取所有学期列表
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('student'):
            return self.format_response(False, message="权限不足，需要登录")
        
        # 获取学期列表
        semesters = self.schedule_model.get_semesters()
        
        return self.format_response(True, data=semesters)
    
    def _format_schedule_data(self, schedule_items):
        """
        将课程表数据格式化为前端所需格式
        
        参数:
            schedule_items (list): 课程表项列表
        
        返回:
            dict: 格式化后的数据
        """
        # 课程节次配置
        section_times = {
            1: {"start": "08:00", "end": "08:45"},
            2: {"start": "08:55", "end": "09:40"},
            3: {"start": "10:00", "end": "10:45"},
            4: {"start": "10:55", "end": "11:40"},
            5: {"start": "14:00", "end": "14:45"},
            6: {"start": "14:55", "end": "15:40"},
            7: {"start": "16:00", "end": "16:45"},
            8: {"start": "16:55", "end": "17:40"},
            9: {"start": "19:00", "end": "19:45"},
            10: {"start": "19:55", "end": "20:40"},
            11: {"start": "20:50", "end": "21:35"}
        }
        
        # 按天组织数据
        days = {day: [] for day in range(1, 8)}  # 1-7对应周一到周日
        
        for item in schedule_items:
            day = item['day_of_week']
            
            # 计算上课时间
            start_time = section_times.get(item['start_section'], {}).get('start', '')
            end_time = section_times.get(item['end_section'], {}).get('end', '')
            
            # 构建课程信息
            course_info = {
                'id': item['id'],
                'course_id': item['course_id'],
                'course_name': item['course_name'],
                'location': item['location'],
                'start_section': item['start_section'],
                'end_section': item['end_section'],
                'section_span': item['end_section'] - item['start_section'] + 1,
                'start_time': start_time,
                'end_time': end_time,
                'week_type': item['week_type'],  # 0:全部周, 1:单周, 2:双周
                'start_week': item['start_week'],
                'end_week': item['end_week'],
                'teacher': item.get('teacher', '')
            }
            
            days[day].append(course_info)
        
        # 为每天的课程按节次排序
        for day in days:
            days[day] = sorted(days[day], key=lambda x: x['start_section'])
        
        # 构建课程节次信息
        sections = []
        for section_num, times in section_times.items():
            sections.append({
                'number': section_num,
                'start_time': times['start'],
                'end_time': times['end']
            })
        
        # 返回完整的格式化数据
        return {
            'days': days,
            'sections': sections,
            'week_types': [
                {'id': 0, 'name': '全部周'},
                {'id': 1, 'name': '单周'},
                {'id': 2, 'name': '双周'}
            ]
        }
    
    def batch_import_schedule(self, schedule_data_list):
        """
        批量导入课程表
        
        参数:
            schedule_data_list (list): 课程表数据列表
        
        返回:
            dict: 响应结果
        """
        # 检查权限
        if not self.check_permission('admin'):
            return self.format_response(False, message="权限不足，需要管理员权限")
        
        if not schedule_data_list:
            return self.format_response(False, message="没有提供课程表数据")
        
        success_count = 0
        failed_count = 0
        failed_records = []
        
        for schedule_data in schedule_data_list:
            # 添加课程表项
            success, error_msg = self.schedule_model.add_schedule_item(schedule_data)
            
            if success:
                success_count += 1
            else:
                failed_count += 1
                failed_records.append({
                    'data': schedule_data,
                    'reason': error_msg or "添加失败，未知错误"
                })
        
        # 记录操作日志
        self.log_operation(
            operation="批量导入课程表",
            target="课程表批量导入",
            details=f"成功导入 {success_count} 条课程表数据，失败 {failed_count} 条"
        )
        
        return self.format_response(
            True,
            data={
                'success_count': success_count,
                'failed_count': failed_count,
                'failed_records': failed_records
            },
            message=f"成功导入 {success_count} 条课程表数据，失败 {failed_count} 条"
        )