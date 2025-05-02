"""
学生模型模块
"""
import logging
import sqlite3
from datetime import datetime

from config.database import TABLES
from models.database import Database

logger = logging.getLogger(__name__)

class Student:
    """学生模型类，处理学生信息的CRUD操作"""
    
    def __init__(self, db=None):
        """初始化学生模型"""
        self.db = db if db else Database()
        if not hasattr(self.db, 'connection') or self.db.connection is None:
            self.db.connect()
    
    def add_student(self, student_data):
        """
        添加新学生
        
        参数:
            student_data (dict): 学生信息字典，包含以下字段:
                - student_id: 学号
                - name: 姓名
                - gender: 性别
                - birth_date: 出生日期
                - class_name: 班级
                - admission_date: 入学日期
                - contact_phone: 联系电话
                - email: 电子邮箱
                - address: 地址
                - status: 状态（在读、休学、退学、毕业）
        
        返回:
            bool: 添加成功返回True，否则返回False
        """
        try:
            # 验证必填字段
            if not student_data.get('student_id') or not student_data.get('name'):
                logger.error("添加学生失败: 学号和姓名为必填项")
                return False
            
            # 先检查学号是否已存在
            existing_student = self.get_student(student_data['student_id'])
            if existing_student:
                logger.error(f"添加学生失败: 学号 {student_data['student_id']} 已存在")
                return False
            
            # 准备SQL语句和参数
            fields = ', '.join(student_data.keys())
            placeholders = ', '.join(['?'] * len(student_data))
            values = list(student_data.values())
            
            # 执行插入操作
            sql = f"INSERT INTO {TABLES['students']} ({fields}) VALUES ({placeholders})"
            self.db.execute(sql, values)
            self.db.commit()
            
            logger.info(f"成功添加学生: {student_data['name']}({student_data['student_id']})")
            return True
        except sqlite3.IntegrityError:
            self.db.rollback()
            logger.error(f"添加学生失败: 学号 {student_data.get('student_id')} 已存在")
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"添加学生失败: {e}")
            return False
    
    def update_student(self, student_id, update_data):
        """
        更新学生信息
        
        参数:
            student_id (str): 学号
            update_data (dict): 需要更新的字段和值
        
        返回:
            bool: 更新成功返回True，否则返回False
        """
        try:
            if not update_data:
                logger.warning("更新学生信息失败: 没有提供更新数据")
                return False
            
            # 添加更新时间
            update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 准备SQL语句和参数
            set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(student_id)  # WHERE子句的参数
            
            # 执行更新操作
            sql = f"UPDATE {TABLES['students']} SET {set_clause} WHERE student_id = ?"
            self.db.execute(sql, values)
            self.db.commit()
            
            # 检查是否有记录被更新
            if self.db.cursor.rowcount > 0:
                logger.info(f"成功更新学生信息: {student_id}")
                return True
            else:
                logger.warning(f"更新学生信息失败: 未找到学号为 {student_id} 的学生")
                return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新学生信息失败: {e}")
            return False
    
    def delete_student(self, student_id):
        """
        删除学生
        
        参数:
            student_id (str): 学号
        
        返回:
            bool: 删除成功返回True，否则返回False
        """
        try:
            # 执行删除操作
            sql = f"DELETE FROM {TABLES['students']} WHERE student_id = ?"
            self.db.execute(sql, (student_id,))
            self.db.commit()
            
            # 检查是否有记录被删除
            if self.db.cursor.rowcount > 0:
                logger.info(f"成功删除学生: {student_id}")
                return True
            else:
                logger.warning(f"删除学生失败: 未找到学号为 {student_id} 的学生")
                return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除学生失败: {e}")
            return False
    
    def get_student(self, student_id):
        """
        获取单个学生信息
        
        参数:
            student_id (str): 学号
        
        返回:
            dict: 学生信息字典，未找到返回None
        """
        try:
            sql = f"SELECT * FROM {TABLES['students']} WHERE student_id = ?"
            self.db.execute(sql, (student_id,))
            student = self.db.fetchone()
            
            if student:
                # 将Row对象转换为字典
                return dict(student)
            else:
                logger.warning(f"未找到学号为 {student_id} 的学生")
                return None
        except Exception as e:
            logger.error(f"获取学生信息失败: {e}")
            return None
    
    def get_all_students(self, filters=None, order_by='name', limit=None, offset=None):
        """
        获取学生列表
        
        参数:
            filters (dict): 过滤条件，如 {'class_name': '计算机1班', 'status': '在读'}
            order_by (str): 排序字段
            limit (int): 限制返回记录数
            offset (int): 偏移量
        
        返回:
            list: 学生信息字典列表
        """
        try:
            # 构建基本SQL
            sql = f"SELECT * FROM {TABLES['students']}"
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
            students = self.db.fetchall()
            
            # 将Row对象列表转换为字典列表
            return [dict(student) for student in students]
        except Exception as e:
            logger.error(f"获取学生列表失败: {e}")
            return []
    
    def search_students(self, keyword):
        """
        搜索学生
        
        参数:
            keyword (str): 搜索关键词，可匹配学号、姓名、班级等
        
        返回:
            list: 匹配的学生信息字典列表
        """
        try:
            # 构建模糊搜索SQL
            sql = f"""
            SELECT * FROM {TABLES['students']} 
            WHERE student_id LIKE ? OR name LIKE ? OR class_name LIKE ? OR contact_phone LIKE ?
            """
            pattern = f"%{keyword}%"
            params = [pattern, pattern, pattern, pattern]
            
            # 执行查询
            self.db.execute(sql, params)
            students = self.db.fetchall()
            
            # 将Row对象列表转换为字典列表
            return [dict(student) for student in students]
        except Exception as e:
            logger.error(f"搜索学生失败: {e}")
            return []
    
    def count_students(self, filters=None):
        """
        统计学生数量
        
        参数:
            filters (dict): 过滤条件，如 {'class_name': '计算机1班', 'status': '在读'}
        
        返回:
            int: 学生数量
        """
        try:
            # 构建基本SQL
            sql = f"SELECT COUNT(*) as count FROM {TABLES['students']}"
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
            logger.error(f"统计学生数量失败: {e}")
            return 0