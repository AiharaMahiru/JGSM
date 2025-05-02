"""
课程表模型模块
"""
import logging
import sqlite3
from datetime import datetime

from config.database import TABLES
from models.database import Database
from models.course import Course

logger = logging.getLogger(__name__)

class Schedule:
    """课程表模型类，处理课程表信息的CRUD操作"""
    
    def __init__(self, db=None):
        """初始化课程表模型"""
        self.db = db if db else Database()
        if not hasattr(self.db, 'connection') or self.db.connection is None:
            self.db.connect()
        self.course_model = Course(self.db)
    
    def add_schedule_item(self, schedule_data):
        """
        添加课程表项
        
        参数:
            schedule_data (dict): 课程表项信息字典，包含以下字段:
                - course_id: 课程编号
                - semester: 学期(如: 2024-2025-1)
                - day_of_week: 星期几(1-7)
                - start_section: 开始节数
                - end_section: 结束节数
                - location: 教室位置
                - teacher: 任课教师(可选)
                - week_type: 周类型(0:全部周, 1:单周, 2:双周)
                - start_week: 开始周次
                - end_week: 结束周次
        
        返回:
            tuple: (成功标志, 错误信息)，成功时返回(True, None)，失败时返回(False, 错误信息)
        """
        try:
            # 验证必填字段
            required_fields = ['course_id', 'semester', 'day_of_week', 'start_section', 
                              'end_section', 'location', 'start_week', 'end_week']
            
            for field in required_fields:
                if field not in schedule_data or not schedule_data[field]:
                    error_msg = f"添加课程表项失败: {field} 为必填项"
                    logger.error(error_msg)
                    return False, error_msg
            
            # 验证课程是否存在
            course = self.course_model.get_course(schedule_data['course_id'])
            if not course:
                error_msg = f"添加课程表项失败: 课程编号 {schedule_data['course_id']} 不存在"
                logger.error(error_msg)
                return False, error_msg
            
            # 验证数值类型字段
            int_fields = ['day_of_week', 'start_section', 'end_section', 'start_week', 'end_week']
            for field in int_fields:
                try:
                    schedule_data[field] = int(schedule_data[field])
                except (ValueError, TypeError):
                    error_msg = f"添加课程表项失败: {field} 必须为整数"
                    logger.error(error_msg)
                    return False, error_msg
            
            # 验证数值范围
            if not (1 <= schedule_data['day_of_week'] <= 7):
                error_msg = "添加课程表项失败: day_of_week 必须在 1-7 之间"
                logger.error(error_msg)
                return False, error_msg
                
            if schedule_data['start_section'] > schedule_data['end_section']:
                error_msg = "添加课程表项失败: 开始节数不能大于结束节数"
                logger.error(error_msg)
                return False, error_msg
                
            if schedule_data['start_week'] > schedule_data['end_week']:
                error_msg = "添加课程表项失败: 开始周次不能大于结束周次"
                logger.error(error_msg)
                return False, error_msg
            
            # 设置默认值
            if 'week_type' not in schedule_data:
                schedule_data['week_type'] = 0  # 默认为全部周
            else:
                try:
                    schedule_data['week_type'] = int(schedule_data['week_type'])
                    if schedule_data['week_type'] not in [0, 1, 2]:
                        error_msg = "添加课程表项失败: week_type 必须为 0(全部周), 1(单周) 或 2(双周)"
                        logger.error(error_msg)
                        return False, error_msg
                except (ValueError, TypeError):
                    error_msg = "添加课程表项失败: week_type 必须为整数"
                    logger.error(error_msg)
                    return False, error_msg
            
            # 添加创建时间和更新时间
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            schedule_data['created_at'] = now
            schedule_data['updated_at'] = now
            
            # 检查时间冲突
            conflicts = self._check_schedule_conflict(
                schedule_data['semester'], 
                schedule_data['day_of_week'],
                schedule_data['start_section'],
                schedule_data['end_section'],
                schedule_data['start_week'],
                schedule_data['end_week'],
                schedule_data['week_type']
            )
            if conflicts:
                conflict_details = ", ".join([f"{conflict['course_name']}({conflict['location']})" for conflict in conflicts])
                error_msg = f"添加课程表项失败: 与现有课程时间冲突: {conflict_details}"
                logger.error(error_msg)
                return False, error_msg
            
            # 准备SQL语句和参数
            fields = ', '.join(schedule_data.keys())
            placeholders = ', '.join(['?'] * len(schedule_data))
            values = list(schedule_data.values())
            
            # 执行插入操作
            sql = f"INSERT INTO {TABLES['schedules']} ({fields}) VALUES ({placeholders})"
            self.db.execute(sql, values)
            self.db.commit()
            
            logger.info(f"成功添加课程表项: {course['course_name']}({schedule_data['location']})")
            return True, None
        except sqlite3.IntegrityError as e:
            self.db.rollback()
            error_msg = f"添加课程表项失败: 数据库完整性错误 - {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            self.db.rollback()
            error_msg = f"添加课程表项失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def update_schedule_item(self, schedule_id, update_data):
        """
        更新课程表项
        
        参数:
            schedule_id (int): 课程表项ID
            update_data (dict): 需要更新的字段和值
        
        返回:
            tuple: (成功标志, 错误信息)，成功时返回(True, None)，失败时返回(False, 错误信息)
        """
        try:
            # 检查课程表项是否存在
            schedule_item = self.get_schedule_item(schedule_id)
            if not schedule_item:
                error_msg = f"更新课程表项失败: ID {schedule_id} 不存在"
                logger.error(error_msg)
                return False, error_msg
            
            if not update_data:
                error_msg = "更新课程表项失败: 没有提供更新数据"
                logger.warning(error_msg)
                return False, error_msg
            
            # 如果更新课程ID，验证课程是否存在
            if 'course_id' in update_data and update_data['course_id'] != schedule_item['course_id']:
                course = self.course_model.get_course(update_data['course_id'])
                if not course:
                    error_msg = f"更新课程表项失败: 课程编号 {update_data['course_id']} 不存在"
                    logger.error(error_msg)
                    return False, error_msg
            
            # 验证数值类型字段
            int_fields = ['day_of_week', 'start_section', 'end_section', 'week_type', 'start_week', 'end_week']
            for field in int_fields:
                if field in update_data:
                    try:
                        update_data[field] = int(update_data[field])
                    except (ValueError, TypeError):
                        error_msg = f"更新课程表项失败: {field} 必须为整数"
                        logger.error(error_msg)
                        return False, error_msg
            
            # 验证数值范围
            if 'day_of_week' in update_data and not (1 <= update_data['day_of_week'] <= 7):
                error_msg = "更新课程表项失败: day_of_week 必须在 1-7 之间"
                logger.error(error_msg)
                return False, error_msg
                
            if 'start_section' in update_data and 'end_section' in update_data:
                if update_data['start_section'] > update_data['end_section']:
                    error_msg = "更新课程表项失败: 开始节数不能大于结束节数"
                    logger.error(error_msg)
                    return False, error_msg
            elif 'start_section' in update_data and update_data['start_section'] > schedule_item['end_section']:
                error_msg = "更新课程表项失败: 开始节数不能大于结束节数"
                logger.error(error_msg)
                return False, error_msg
            elif 'end_section' in update_data and update_data['end_section'] < schedule_item['start_section']:
                error_msg = "更新课程表项失败: 结束节数不能小于开始节数"
                logger.error(error_msg)
                return False, error_msg
                
            if 'start_week' in update_data and 'end_week' in update_data:
                if update_data['start_week'] > update_data['end_week']:
                    error_msg = "更新课程表项失败: 开始周次不能大于结束周次"
                    logger.error(error_msg)
                    return False, error_msg
            elif 'start_week' in update_data and update_data['start_week'] > schedule_item['end_week']:
                error_msg = "更新课程表项失败: 开始周次不能大于结束周次"
                logger.error(error_msg)
                return False, error_msg
            elif 'end_week' in update_data and update_data['end_week'] < schedule_item['start_week']:
                error_msg = "更新课程表项失败: 结束周次不能小于开始周次"
                logger.error(error_msg)
                return False, error_msg
            
            if 'week_type' in update_data and update_data['week_type'] not in [0, 1, 2]:
                error_msg = "更新课程表项失败: week_type 必须为 0(全部周), 1(单周) 或 2(双周)"
                logger.error(error_msg)
                return False, error_msg
            
            # 添加更新时间
            update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 检查时间冲突
            day_of_week = update_data.get('day_of_week', schedule_item['day_of_week'])
            start_section = update_data.get('start_section', schedule_item['start_section'])
            end_section = update_data.get('end_section', schedule_item['end_section'])
            semester = update_data.get('semester', schedule_item['semester'])
            start_week = update_data.get('start_week', schedule_item['start_week'])
            end_week = update_data.get('end_week', schedule_item['end_week'])
            week_type = update_data.get('week_type', schedule_item['week_type'])
            
            conflicts = self._check_schedule_conflict(
                semester, day_of_week, start_section, end_section,
                start_week, end_week, week_type, exclude_id=schedule_id
            )
            if conflicts:
                conflict_details = ", ".join([f"{conflict['course_name']}({conflict['location']})" for conflict in conflicts])
                error_msg = f"更新课程表项失败: 与现有课程时间冲突: {conflict_details}"
                logger.error(error_msg)
                return False, error_msg
            
            # 准备SQL语句和参数
            set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(schedule_id)  # WHERE子句的参数
            
            # 执行更新操作
            sql = f"UPDATE {TABLES['schedules']} SET {set_clause} WHERE id = ?"
            self.db.execute(sql, values)
            self.db.commit()
            
            # 获取更新后的课程信息
            course = self.course_model.get_course(
                update_data.get('course_id', schedule_item['course_id'])
            )
            course_name = course['course_name'] if course else "未知课程"
            
            logger.info(f"成功更新课程表项: {course_name}")
            return True, None
        except Exception as e:
            self.db.rollback()
            error_msg = f"更新课程表项失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def delete_schedule_item(self, schedule_id):
        """
        删除课程表项
        
        参数:
            schedule_id (int): 课程表项ID
        
        返回:
            tuple: (成功标志, 错误信息)，成功时返回(True, None)，失败时返回(False, 错误信息)
        """
        try:
            # 检查课程表项是否存在
            schedule_item = self.get_schedule_item(schedule_id)
            if not schedule_item:
                error_msg = f"删除课程表项失败: ID {schedule_id} 不存在"
                logger.error(error_msg)
                return False, error_msg
            
            # 执行删除操作
            sql = f"DELETE FROM {TABLES['schedules']} WHERE id = ?"
            self.db.execute(sql, (schedule_id,))
            self.db.commit()
            
            logger.info(f"成功删除课程表项: ID {schedule_id}")
            return True, None
        except Exception as e:
            self.db.rollback()
            error_msg = f"删除课程表项失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_schedule_item(self, schedule_id):
        """
        获取单个课程表项信息
        
        参数:
            schedule_id (int): 课程表项ID
        
        返回:
            dict: 课程表项信息字典，未找到返回None
        """
        try:
            sql = f"""
            SELECT s.*, c.course_name
            FROM {TABLES['schedules']} s
            LEFT JOIN {TABLES['courses']} c ON s.course_id = c.course_id
            WHERE s.id = ?
            """
            self.db.execute(sql, (schedule_id,))
            item = self.db.fetchone()
            
            if item:
                return dict(item)
            else:
                logger.warning(f"未找到ID为 {schedule_id} 的课程表项")
                return None
        except Exception as e:
            logger.error(f"获取课程表项信息失败: {str(e)}")
            return None
    
    def get_schedule(self, semester, filters=None):
        """
        获取指定学期的完整课程表
        
        参数:
            semester (str): 学期
            filters (dict): 过滤条件，如 {'course_id': 'CS101', 'week_type': 1}
        
        返回:
            list: 课程表项信息字典列表
        """
        try:
            # 构建基本SQL
            sql = f"""
            SELECT s.*, c.course_name
            FROM {TABLES['schedules']} s
            LEFT JOIN {TABLES['courses']} c ON s.course_id = c.course_id
            WHERE s.semester = ?
            """
            params = [semester]
            
            # 添加过滤条件
            if filters:
                for key, value in filters.items():
                    if key in ['course_id', 'location', 'teacher', 'day_of_week', 'week_type']:
                        sql += f" AND s.{key} = ?"
                        params.append(value)
            
            # 按星期几和开始节数排序
            sql += " ORDER BY s.day_of_week, s.start_section"
            
            # 执行查询
            self.db.execute(sql, params)
            items = self.db.fetchall()
            
            # 将Row对象列表转换为字典列表
            return [dict(item) for item in items]
        except Exception as e:
            logger.error(f"获取课程表失败: {str(e)}")
            return []
    
    def get_schedule_by_week(self, semester, week_number):
        """
        获取指定学期指定周次的课程表
        
        参数:
            semester (str): 学期
            week_number (int): 周次
        
        返回:
            list: 课程表项信息字典列表
        """
        try:
            # 构建查询SQL
            sql = f"""
            SELECT s.*, c.course_name
            FROM {TABLES['schedules']} s
            LEFT JOIN {TABLES['courses']} c ON s.course_id = c.course_id
            WHERE s.semester = ?
              AND s.start_week <= ?
              AND s.end_week >= ?
              AND (
                  s.week_type = 0  -- 全部周
                  OR (s.week_type = 1 AND ? % 2 = 1)  -- 单周
                  OR (s.week_type = 2 AND ? % 2 = 0)  -- 双周
              )
            ORDER BY s.day_of_week, s.start_section
            """
            params = [semester, week_number, week_number, week_number, week_number]
            
            # 执行查询
            self.db.execute(sql, params)
            items = self.db.fetchall()
            
            # 将Row对象列表转换为字典列表
            return [dict(item) for item in items]
        except Exception as e:
            logger.error(f"获取指定周次课程表失败: {str(e)}")
            return []
    
    def get_course_schedules(self, course_id, semester=None):
        """
        获取指定课程的所有课程表项
        
        参数:
            course_id (str): 课程编号
            semester (str, optional): 学期，不提供则获取所有学期
        
        返回:
            list: 课程表项信息字典列表
        """
        try:
            # 构建基本SQL
            sql = f"""
            SELECT s.*, c.course_name
            FROM {TABLES['schedules']} s
            LEFT JOIN {TABLES['courses']} c ON s.course_id = c.course_id
            WHERE s.course_id = ?
            """
            params = [course_id]
            
            # 添加学期过滤
            if semester:
                sql += " AND s.semester = ?"
                params.append(semester)
            
            # 按学期和星期几排序
            sql += " ORDER BY s.semester DESC, s.day_of_week, s.start_section"
            
            # 执行查询
            self.db.execute(sql, params)
            items = self.db.fetchall()
            
            # 将Row对象列表转换为字典列表
            return [dict(item) for item in items]
        except Exception as e:
            logger.error(f"获取课程的所有课程表项失败: {str(e)}")
            return []
    
    def get_semesters(self):
        """
        获取所有学期列表
        
        返回:
            list: 学期列表，按学期降序排序
        """
        try:
            sql = f"""
            SELECT DISTINCT semester
            FROM {TABLES['schedules']}
            WHERE semester IS NOT NULL AND semester != ''
            ORDER BY semester DESC
            """
            self.db.execute(sql)
            results = self.db.fetchall()
            
            return [row['semester'] for row in results]
        except Exception as e:
            logger.error(f"获取学期列表失败: {str(e)}")
            return []
    
    def _check_schedule_conflict(self, semester, day_of_week, start_section, end_section,
                               start_week, end_week, week_type, exclude_id=None):
        """
        检查课程表时间冲突
        
        参数:
            semester (str): 学期
            day_of_week (int): 星期几(1-7)
            start_section (int): 开始节数
            end_section (int): 结束节数
            start_week (int): 开始周次
            end_week (int): 结束周次
            week_type (int): 周类型(0:全部周, 1:单周, 2:双周)
            exclude_id (int, optional): 需要排除的课程表项ID
            
        返回:
            list: 冲突的课程表项列表，无冲突则返回空列表
        """
        try:
            # 构建查询SQL
            sql = f"""
            SELECT s.*, c.course_name
            FROM {TABLES['schedules']} s
            LEFT JOIN {TABLES['courses']} c ON s.course_id = c.course_id
            WHERE s.semester = ?
              AND s.day_of_week = ?
              AND NOT (s.end_section < ? OR s.start_section > ?)
              AND NOT (s.end_week < ? OR s.start_week > ?)
            """
            params = [semester, day_of_week, start_section, end_section, start_week, end_week]
            
            # 添加排除条件
            if exclude_id is not None:
                sql += " AND s.id != ?"
                params.append(exclude_id)
            
            # 处理单双周的冲突检查
            # 如果是全部周，则与所有周类型冲突
            # 如果是单周，则与全部周和单周冲突
            # 如果是双周，则与全部周和双周冲突
            if week_type == 0:
                # 全部周与所有类型冲突
                pass
            elif week_type == 1:
                # 单周与全部周和单周冲突
                sql += " AND (s.week_type = 0 OR s.week_type = 1)"
            elif week_type == 2:
                # 双周与全部周和双周冲突
                sql += " AND (s.week_type = 0 OR s.week_type = 2)"
            
            # 执行查询
            self.db.execute(sql, params)
            conflicts = self.db.fetchall()
            
            # 将Row对象列表转换为字典列表
            return [dict(item) for item in conflicts]
        except Exception as e:
            logger.error(f"检查课程表冲突失败: {str(e)}")
            return []