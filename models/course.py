"""
课程模型模块
"""
import logging
import sqlite3
from datetime import datetime

from config.database import TABLES
from models.database import Database

logger = logging.getLogger(__name__)

class Course:
    """课程模型类，处理课程信息的CRUD操作"""
    
    def __init__(self, db=None):
        """初始化课程模型"""
        self.db = db if db else Database()
        if not hasattr(self.db, 'connection') or self.db.connection is None:
            self.db.connect()
    
    def add_course(self, course_data):
        """
        添加新课程
        
        参数:
            course_data (dict): 课程信息字典，包含以下字段:
                - course_id: 课程编号
                - course_name: 课程名称
                - credit: 学分
                - teacher: 任课教师
                - description: 课程描述
        
        返回:
            tuple: (成功标志, 错误信息)，成功时返回(True, None)，失败时返回(False, 错误信息)
        """
        try:
            # 验证必填字段
            if not course_data.get('course_id') or not course_data.get('course_name') or 'credit' not in course_data:
                error_msg = "添加课程失败: 课程编号、课程名称和学分为必填项"
                logger.error(error_msg)
                return False, error_msg
            
            # 准备SQL语句和参数
            fields = ', '.join(course_data.keys())
            placeholders = ', '.join(['?'] * len(course_data))
            values = list(course_data.values())
            
            # 执行插入操作
            sql = f"INSERT INTO {TABLES['courses']} ({fields}) VALUES ({placeholders})"
            self.db.execute(sql, values)
            self.db.commit()
            
            logger.info(f"成功添加课程: {course_data['course_name']}({course_data['course_id']})")
            return True, None
        except sqlite3.IntegrityError:
            self.db.rollback()
            error_msg = f"添加课程失败: 课程编号 {course_data.get('course_id')} 已存在"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            self.db.rollback()
            error_msg = f"添加课程失败: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def update_course(self, course_id, update_data):
        """
        更新课程信息
        
        参数:
            course_id (str): 课程编号
            update_data (dict): 需要更新的字段和值
        
        返回:
            bool: 更新成功返回True，否则返回False
        """
        try:
            if not update_data:
                logger.warning("更新课程信息失败: 没有提供更新数据")
                return False
            
            # 添加更新时间
            update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 准备SQL语句和参数
            set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(course_id)  # WHERE子句的参数
            
            # 执行更新操作
            sql = f"UPDATE {TABLES['courses']} SET {set_clause} WHERE course_id = ?"
            self.db.execute(sql, values)
            self.db.commit()
            
            # 检查是否有记录被更新
            if self.db.cursor.rowcount > 0:
                logger.info(f"成功更新课程信息: {course_id}")
                return True
            else:
                logger.warning(f"更新课程信息失败: 未找到课程编号为 {course_id} 的课程")
                return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新课程信息失败: {e}")
            return False
    
    def delete_course(self, course_id):
        """
        删除课程
        
        参数:
            course_id (str): 课程编号
        
        返回:
            bool: 删除成功返回True，否则返回False
        """
        try:
            # 执行删除操作
            sql = f"DELETE FROM {TABLES['courses']} WHERE course_id = ?"
            self.db.execute(sql, (course_id,))
            self.db.commit()
            
            # 检查是否有记录被删除
            if self.db.cursor.rowcount > 0:
                logger.info(f"成功删除课程: {course_id}")
                return True
            else:
                logger.warning(f"删除课程失败: 未找到课程编号为 {course_id} 的课程")
                return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除课程失败: {e}")
            return False
    
    def get_course(self, course_id):
        """
        获取单个课程信息
        
        参数:
            course_id (str): 课程编号
        
        返回:
            dict: 课程信息字典，未找到返回None
        """
        try:
            sql = f"SELECT * FROM {TABLES['courses']} WHERE course_id = ?"
            self.db.execute(sql, (course_id,))
            course = self.db.fetchone()
            
            if course:
                # 将Row对象转换为字典
                return dict(course)
            else:
                logger.warning(f"未找到课程编号为 {course_id} 的课程")
                return None
        except Exception as e:
            logger.error(f"获取课程信息失败: {e}")
            return None
    
    def get_all_courses(self, filters=None, order_by='course_name', limit=None, offset=None):
        """
        获取课程列表
        
        参数:
            filters (dict): 过滤条件，如 {'teacher': '张三'}
            order_by (str): 排序字段
            limit (int): 限制返回记录数
            offset (int): 偏移量
        
        返回:
            list: 课程信息字典列表
        """
        try:
            # 构建基本SQL
            sql = f"SELECT * FROM {TABLES['courses']}"
            params = []
            
            # 添加过滤条件
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
                
                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)
            
            # 添加排序
            if order_by:
                sql += f" ORDER BY {order_by}"
            
            # 添加分页
            if limit:
                sql += " LIMIT ?"
                params.append(limit)
                
                if offset:
                    sql += " OFFSET ?"
                    params.append(offset)
            
            # 执行查询
            self.db.execute(sql, params)
            courses = self.db.fetchall()
            
            # 将Row对象列表转换为字典列表
            return [dict(course) for course in courses]
        except Exception as e:
            logger.error(f"获取课程列表失败: {e}")
            return []
    
    def search_courses(self, keyword):
        """
        搜索课程
        
        参数:
            keyword (str): 搜索关键词，可匹配课程编号、课程名称、教师等
        
        返回:
            list: 匹配的课程信息字典列表
        """
        try:
            # 构建模糊搜索SQL
            sql = f"""
            SELECT * FROM {TABLES['courses']} 
            WHERE course_id LIKE ? OR course_name LIKE ? OR teacher LIKE ? OR description LIKE ?
            """
            pattern = f"%{keyword}%"
            params = [pattern, pattern, pattern, pattern]
            
            # 执行查询
            self.db.execute(sql, params)
            courses = self.db.fetchall()
            
            # 将Row对象列表转换为字典列表
            return [dict(course) for course in courses]
        except Exception as e:
            logger.error(f"搜索课程失败: {e}")
            return []
    
    def count_courses(self, filters=None):
        """
        统计课程数量
        
        参数:
            filters (dict): 过滤条件，如 {'teacher': '张三'}
        
        返回:
            int: 课程数量
        """
        try:
            # 构建基本SQL
            sql = f"SELECT COUNT(*) as count FROM {TABLES['courses']}"
            params = []
            
            # 添加过滤条件
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
                
                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)
            
            # 执行查询
            self.db.execute(sql, params)
            result = self.db.fetchone()
            
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"统计课程数量失败: {e}")
            return 0