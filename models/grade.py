"""
成绩模型模块
"""
import logging
import sqlite3
from datetime import datetime

from config.database import TABLES
from models.database import Database

logger = logging.getLogger(__name__)

class Grade:
    """成绩模型类，处理学生成绩的CRUD操作和统计分析"""
    
    def __init__(self, db=None):
        """初始化成绩模型"""
        self.db = db if db else Database()
        if not hasattr(self.db, 'connection') or self.db.connection is None:
            self.db.connect()
    
    def add_grade(self, grade_data):
        """
        添加新成绩记录
        
        参数:
            grade_data (dict): 成绩信息字典，包含以下字段:
                - student_id: 学号
                - course_id: 课程编号
                - semester: 学期
                - score: 分数
                - grade_point: 绩点（可选）
                - exam_date: 考试日期（可选）
                - remarks: 备注（可选）
        
        返回:
            bool: 添加成功返回True，否则返回False
        """
        try:
            # 验证必填字段
            if not grade_data.get('student_id') or not grade_data.get('course_id') or \
               not grade_data.get('semester') or 'score' not in grade_data:
                logger.error("添加成绩失败: 学号、课程编号、学期和分数为必填项")
                return False
            
            # 如果没有提供绩点，则根据分数计算
            if 'grade_point' not in grade_data and 'score' in grade_data:
                grade_data['grade_point'] = self._calculate_grade_point(grade_data['score'])
            
            # 准备SQL语句和参数
            fields = ', '.join(grade_data.keys())
            placeholders = ', '.join(['?'] * len(grade_data))
            values = list(grade_data.values())
            
            # 执行插入操作
            sql = f"INSERT INTO {TABLES['grades']} ({fields}) VALUES ({placeholders})"
            self.db.execute(sql, values)
            self.db.commit()
            
            logger.info(f"成功添加成绩: 学生 {grade_data['student_id']} 课程 {grade_data['course_id']} 学期 {grade_data['semester']}")
            return True
        except sqlite3.IntegrityError as e:
            self.db.rollback()
            if "UNIQUE constraint failed" in str(e):
                logger.error(f"添加成绩失败: 该学生在该学期已有该课程的成绩记录")
            else:
                logger.error(f"添加成绩失败: 外键约束错误，请确认学号和课程编号存在")
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"添加成绩失败: {e}")
            return False
    
    def update_grade(self, grade_id, update_data):
        """
        更新成绩记录
        
        参数:
            grade_id (int): 成绩记录ID
            update_data (dict): 需要更新的字段和值
        
        返回:
            bool: 更新成功返回True，否则返回False
        """
        try:
            if not update_data:
                logger.warning("更新成绩失败: 没有提供更新数据")
                return False
            
            # 如果更新分数但没有更新绩点，则自动计算绩点
            if 'score' in update_data and 'grade_point' not in update_data:
                update_data['grade_point'] = self._calculate_grade_point(update_data['score'])
            
            # 添加更新时间
            update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 准备SQL语句和参数
            set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(grade_id)  # WHERE子句的参数
            
            # 执行更新操作
            sql = f"UPDATE {TABLES['grades']} SET {set_clause} WHERE id = ?"
            self.db.execute(sql, values)
            self.db.commit()
            
            # 检查是否有记录被更新
            if self.db.cursor.rowcount > 0:
                logger.info(f"成功更新成绩记录: ID {grade_id}")
                return True
            else:
                logger.warning(f"更新成绩失败: 未找到ID为 {grade_id} 的成绩记录")
                return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新成绩失败: {e}")
            return False
    
    def update_grade_by_keys(self, student_id, course_id, semester, update_data):
        """
        通过学号、课程编号和学期更新成绩记录
        
        参数:
            student_id (str): 学号
            course_id (str): 课程编号
            semester (str): 学期
            update_data (dict): 需要更新的字段和值
        
        返回:
            bool: 更新成功返回True，否则返回False
        """
        try:
            if not update_data:
                logger.warning("更新成绩失败: 没有提供更新数据")
                return False
            
            # 如果更新分数但没有更新绩点，则自动计算绩点
            if 'score' in update_data and 'grade_point' not in update_data:
                update_data['grade_point'] = self._calculate_grade_point(update_data['score'])
            
            # 添加更新时间
            update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 准备SQL语句和参数
            set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
            values = list(update_data.values())
            values.extend([student_id, course_id, semester])  # WHERE子句的参数
            
            # 执行更新操作
            sql = f"""
            UPDATE {TABLES['grades']} 
            SET {set_clause} 
            WHERE student_id = ? AND course_id = ? AND semester = ?
            """
            self.db.execute(sql, values)
            self.db.commit()
            
            # 检查是否有记录被更新
            if self.db.cursor.rowcount > 0:
                logger.info(f"成功更新成绩: 学生 {student_id} 课程 {course_id} 学期 {semester}")
                return True
            else:
                logger.warning(f"更新成绩失败: 未找到对应的成绩记录")
                return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新成绩失败: {e}")
            return False
    
    def delete_grade(self, grade_id):
        """
        删除成绩记录
        
        参数:
            grade_id (int): 成绩记录ID
        
        返回:
            bool: 删除成功返回True，否则返回False
        """
        try:
            # 执行删除操作
            sql = f"DELETE FROM {TABLES['grades']} WHERE id = ?"
            self.db.execute(sql, (grade_id,))
            self.db.commit()
            
            # 检查是否有记录被删除
            if self.db.cursor.rowcount > 0:
                logger.info(f"成功删除成绩记录: ID {grade_id}")
                return True
            else:
                logger.warning(f"删除成绩失败: 未找到ID为 {grade_id} 的成绩记录")
                return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除成绩失败: {e}")
            return False
    
    def delete_grade_by_keys(self, student_id, course_id, semester):
        """
        通过学号、课程编号和学期删除成绩记录
        
        参数:
            student_id (str): 学号
            course_id (str): 课程编号
            semester (str): 学期
        
        返回:
            bool: 删除成功返回True，否则返回False
        """
        try:
            # 执行删除操作
            sql = f"""
            DELETE FROM {TABLES['grades']} 
            WHERE student_id = ? AND course_id = ? AND semester = ?
            """
            self.db.execute(sql, (student_id, course_id, semester))
            self.db.commit()
            
            # 检查是否有记录被删除
            if self.db.cursor.rowcount > 0:
                logger.info(f"成功删除成绩: 学生 {student_id} 课程 {course_id} 学期 {semester}")
                return True
            else:
                logger.warning(f"删除成绩失败: 未找到对应的成绩记录")
                return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除成绩失败: {e}")
            return False
    
    def get_grade(self, grade_id):
        """
        获取单个成绩记录
        
        参数:
            grade_id (int): 成绩记录ID
        
        返回:
            dict: 成绩记录字典，未找到返回None
        """
        try:
            sql = f"SELECT * FROM {TABLES['grades']} WHERE id = ?"
            self.db.execute(sql, (grade_id,))
            grade = self.db.fetchone()
            
            if grade:
                # 将Row对象转换为字典
                return dict(grade)
            else:
                logger.warning(f"未找到ID为 {grade_id} 的成绩记录")
                return None
        except Exception as e:
            logger.error(f"获取成绩记录失败: {e}")
            return None
    
    def get_grade_by_keys(self, student_id, course_id, semester):
        """
        通过学号、课程编号和学期获取成绩记录
        
        参数:
            student_id (str): 学号
            course_id (str): 课程编号
            semester (str): 学期
        
        返回:
            dict: 成绩记录字典，未找到返回None
        """
        try:
            sql = f"""
            SELECT * FROM {TABLES['grades']} 
            WHERE student_id = ? AND course_id = ? AND semester = ?
            """
            self.db.execute(sql, (student_id, course_id, semester))
            grade = self.db.fetchone()
            
            if grade:
                # 将Row对象转换为字典
                return dict(grade)
            else:
                logger.warning(f"未找到对应的成绩记录")
                return None
        except Exception as e:
            logger.error(f"获取成绩记录失败: {e}")
            return None
    
    def get_student_grades(self, student_id, semester=None):
        """
        获取学生所有成绩
        
        参数:
            student_id (str): 学号
            semester (str, optional): 学期，如果提供则只返回该学期的成绩
        
        返回:
            list: 成绩记录字典列表
        """
        try:
            # 构建基本SQL
            sql = f"""
            SELECT g.*, c.course_name, c.credit 
            FROM {TABLES['grades']} g
            JOIN {TABLES['courses']} c ON g.course_id = c.course_id
            WHERE g.student_id = ?
            """
            params = [student_id]
            
            # 如果提供了学期，添加学期过滤条件
            if semester:
                sql += " AND g.semester = ?"
                params.append(semester)
            
            # 添加排序
            sql += " ORDER BY g.semester, c.course_id"
            
            # 执行查询
            self.db.execute(sql, params)
            grades = self.db.fetchall()
            
            # 将Row对象列表转换为字典列表
            return [dict(grade) for grade in grades]
        except Exception as e:
            logger.error(f"获取学生成绩失败: {e}")
            return []
    
    def get_course_grades(self, course_id, semester=None):
        """
        获取课程所有学生的成绩
        
        参数:
            course_id (str): 课程编号
            semester (str, optional): 学期，如果提供则只返回该学期的成绩
        
        返回:
            list: 成绩记录字典列表
        """
        try:
            # 构建基本SQL
            sql = f"""
            SELECT g.*, s.name as student_name, s.class_name
            FROM {TABLES['grades']} g
            JOIN {TABLES['students']} s ON g.student_id = s.student_id
            WHERE g.course_id = ?
            """
            params = [course_id]
            
            # 如果提供了学期，添加学期过滤条件
            if semester:
                sql += " AND g.semester = ?"
                params.append(semester)
            
            # 添加排序
            sql += " ORDER BY g.score DESC, s.student_id"
            
            # 执行查询
            self.db.execute(sql, params)
            grades = self.db.fetchall()
            
            # 将Row对象列表转换为字典列表
            return [dict(grade) for grade in grades]
        except Exception as e:
            logger.error(f"获取课程成绩失败: {e}")
            return []
    
    def calculate_student_gpa(self, student_id, semester=None):
        """
        计算学生的GPA
        
        参数:
            student_id (str): 学号
            semester (str, optional): 学期，如果提供则只计算该学期的GPA
        
        返回:
            dict: 包含总学分、平均分、GPA的字典
        """
        try:
            # 构建基本SQL
            sql = f"""
            SELECT 
                SUM(c.credit) as total_credit,
                SUM(g.grade_point * c.credit) as weighted_gpa,
                AVG(g.score) as average_score
            FROM {TABLES['grades']} g
            JOIN {TABLES['courses']} c ON g.course_id = c.course_id
            WHERE g.student_id = ?
            """
            params = [student_id]
            
            # 如果提供了学期，添加学期过滤条件
            if semester:
                sql += " AND g.semester = ?"
                params.append(semester)
            
            # 执行查询
            self.db.execute(sql, params)
            result = self.db.fetchone()
            
            if result and result['total_credit']:
                total_credit = result['total_credit']
                weighted_gpa = result['weighted_gpa']
                average_score = result['average_score']
                
                # 计算GPA
                gpa = weighted_gpa / total_credit if total_credit > 0 else 0
                
                return {
                    'student_id': student_id,
                    'semester': semester,
                    'total_credit': total_credit,
                    'average_score': round(average_score, 2),
                    'gpa': round(gpa, 2)
                }
            else:
                return {
                    'student_id': student_id,
                    'semester': semester,
                    'total_credit': 0,
                    'average_score': 0,
                    'gpa': 0
                }
        except Exception as e:
            logger.error(f"计算学生GPA失败: {e}")
            return {
                'student_id': student_id,
                'semester': semester,
                'total_credit': 0,
                'average_score': 0,
                'gpa': 0,
                'error': str(e)
            }
    
    def get_course_statistics(self, course_id, semester):
        """
        获取课程成绩统计信息
        
        参数:
            course_id (str): 课程编号
            semester (str): 学期
        
        返回:
            dict: 包含最高分、最低分、平均分、及格率等统计信息的字典
        """
        try:
            # 获取基本统计信息
            sql = f"""
            SELECT 
                COUNT(*) as total_students,
                MAX(score) as max_score,
                MIN(score) as min_score,
                AVG(score) as avg_score,
                COUNT(CASE WHEN score >= 60 THEN 1 END) as passed_count
            FROM {TABLES['grades']}
            WHERE course_id = ? AND semester = ?
            """
            self.db.execute(sql, (course_id, semester))
            stats = self.db.fetchone()
            
            if not stats or stats['total_students'] == 0:
                return {
                    'course_id': course_id,
                    'semester': semester,
                    'total_students': 0,
                    'max_score': 0,
                    'min_score': 0,
                    'avg_score': 0,
                    'pass_rate': 0,
                    'score_distribution': {}
                }
            
            # 获取分数段分布
            sql = f"""
            SELECT 
                CASE 
                    WHEN score >= 90 THEN '90-100'
                    WHEN score >= 80 THEN '80-89'
                    WHEN score >= 70 THEN '70-79'
                    WHEN score >= 60 THEN '60-69'
                    ELSE '0-59'
                END as score_range,
                COUNT(*) as count
            FROM {TABLES['grades']}
            WHERE course_id = ? AND semester = ?
            GROUP BY score_range
            ORDER BY score_range DESC
            """
            self.db.execute(sql, (course_id, semester))
            distribution_rows = self.db.fetchall()
            
            # 转换为字典
            distribution = {row['score_range']: row['count'] for row in distribution_rows}
            
            # 计算及格率
            pass_rate = (stats['passed_count'] / stats['total_students']) * 100 if stats['total_students'] > 0 else 0
            
            return {
                'course_id': course_id,
                'semester': semester,
                'total_students': stats['total_students'],
                'max_score': stats['max_score'],
                'min_score': stats['min_score'],
                'avg_score': round(stats['avg_score'], 2),
                'pass_rate': round(pass_rate, 2),
                'score_distribution': distribution
            }
        except Exception as e:
            logger.error(f"获取课程统计信息失败: {e}")
            return {
                'course_id': course_id,
                'semester': semester,
                'error': str(e)
            }
    
    def _calculate_grade_point(self, score):
        """
        根据分数计算绩点
        
        参数:
            score (float): 分数
        
        返回:
            float: 绩点
        """
        if score >= 90:
            return 4.0
        elif score >= 85:
            return 3.7
        elif score >= 80:
            return 3.3
        elif score >= 75:
            return 3.0
        elif score >= 70:
            return 2.7
        elif score >= 65:
            return 2.3
        elif score >= 60:
            return 2.0
        else:
            return 0.0
    
    def count_grades(self, filters=None):
        """
        计算符合过滤条件的成绩记录数量
        
        参数:
            filters (dict, optional): 过滤条件
            
        返回:
            int: 记录数量
        """
        try:
            # 构建基本SQL
            sql = f"SELECT COUNT(*) as count FROM {TABLES['grades']} g"
            params = []
            
            # 添加JOIN
            sql += f" LEFT JOIN {TABLES['students']} s ON g.student_id = s.student_id"
            sql += f" LEFT JOIN {TABLES['courses']} c ON g.course_id = c.course_id"
            
            # 添加WHERE条件
            where_clauses = []
            if filters:
                if 'student_id' in filters and filters['student_id']:
                    where_clauses.append("g.student_id = ?")
                    params.append(filters['student_id'])
                
                if 'course_id' in filters and filters['course_id']:
                    where_clauses.append("g.course_id = ?")
                    params.append(filters['course_id'])
                
                if 'semester' in filters and filters['semester']:
                    where_clauses.append("g.semester = ?")
                    params.append(filters['semester'])
                    
                if 'class_name' in filters and filters['class_name']:
                    where_clauses.append("s.class_name = ?")
                    params.append(filters['class_name'])
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # 执行查询
            self.db.execute(sql, params)
            result = self.db.fetchone()
            
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"计算成绩记录数量失败: {e}")
            return 0
    
    def get_grades(self, filters=None, order_by='id', limit=20, offset=0):
        """
        获取符合过滤条件的成绩记录列表
        
        参数:
            filters (dict, optional): 过滤条件
            order_by (str): 排序字段
            limit (int): 限制返回的记录数
            offset (int): 偏移量
            
        返回:
            list: 成绩记录字典列表
        """
        try:
            # 构建基本SQL
            sql = f"""
            SELECT g.*,
                   s.name as student_name, s.class_name,
                   c.course_name, c.credit
            FROM {TABLES['grades']} g
            LEFT JOIN {TABLES['students']} s ON g.student_id = s.student_id
            LEFT JOIN {TABLES['courses']} c ON g.course_id = c.course_id
            """
            params = []
            
            # 添加WHERE条件
            where_clauses = []
            if filters:
                if 'student_id' in filters and filters['student_id']:
                    where_clauses.append("g.student_id = ?")
                    params.append(filters['student_id'])
                
                if 'course_id' in filters and filters['course_id']:
                    where_clauses.append("g.course_id = ?")
                    params.append(filters['course_id'])
                
                if 'semester' in filters and filters['semester']:
                    where_clauses.append("g.semester = ?")
                    params.append(filters['semester'])
                    
                if 'class_name' in filters and filters['class_name']:
                    where_clauses.append("s.class_name = ?")
                    params.append(filters['class_name'])
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # 添加排序
            if order_by:
                sql += f" ORDER BY g.{order_by}"
            
            # 添加分页
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            # 执行查询
            self.db.execute(sql, params)
            grades = self.db.fetchall()
            
            # 将Row对象列表转换为字典列表
            return [dict(grade) for grade in grades]
        except Exception as e:
            logger.error(f"获取成绩记录列表失败: {e}")
            return []
    
    def get_statistics(self, filters=None):
        """
        获取成绩统计数据
        
        参数:
            filters (dict, optional): 过滤条件
            
        返回:
            dict: 统计数据
        """
        try:
            # 基本统计信息
            stats = {
                'total_count': 0,
                'avg_score': 0,
                'pass_rate': 0,
                'score_distribution': {},
                'semester_stats': {},
                'course_stats': [],
                'class_stats': []
            }
            
            # 构建基本SQL - 总体统计
            sql = f"""
            SELECT
                COUNT(*) as total_count,
                COUNT(DISTINCT g.student_id) as total_students,
                AVG(score) as avg_score,
                COUNT(CASE WHEN score >= 60 THEN 1 END) as passed_count
            FROM {TABLES['grades']} g
            LEFT JOIN {TABLES['students']} s ON g.student_id = s.student_id
            """
            params = []
            
            # 添加WHERE条件
            where_clauses = []
            if filters:
                if 'student_id' in filters and filters['student_id']:
                    where_clauses.append("g.student_id = ?")
                    params.append(filters['student_id'])
                
                if 'course_id' in filters and filters['course_id']:
                    where_clauses.append("g.course_id = ?")
                    params.append(filters['course_id'])
                
                if 'semester' in filters and filters['semester']:
                    where_clauses.append("g.semester = ?")
                    params.append(filters['semester'])
                    
                if 'class_name' in filters and filters['class_name']:
                    where_clauses.append("s.class_name = ?")
                    params.append(filters['class_name'])
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # 执行查询 - 总体统计
            self.db.execute(sql, params)
            result = self.db.fetchone()
            
            if result and result['total_count'] > 0:
                stats['total_count'] = result['total_count']
                stats['total_students'] = result['total_students']  # 使用正确的学生计数
                stats['avg_score'] = round(result['avg_score'], 2)
                stats['average_score'] = round(result['avg_score'], 2)  # 添加前端使用的键名
                stats['pass_rate'] = round((result['passed_count'] / result['total_count']) * 100, 2)
                
                # 计算不及格率
                stats['fail_rate'] = round(100 - stats['pass_rate'], 2)
                
                # 查询最高分和最低分
                sql_minmax = f"""
                SELECT MAX(score) as highest_score, MIN(score) as lowest_score
                FROM {TABLES['grades']} g
                LEFT JOIN {TABLES['students']} s ON g.student_id = s.student_id
                """
                
                if where_clauses:
                    sql_minmax += " WHERE " + " AND ".join(where_clauses)
                    
                self.db.execute(sql_minmax, params)
                minmax_result = self.db.fetchone()
                
                if minmax_result:
                    stats['highest_score'] = minmax_result['highest_score']
                    stats['lowest_score'] = minmax_result['lowest_score']
                else:
                    stats['highest_score'] = 0
                    stats['lowest_score'] = 0
                
                # 计算平均GPA
                sql_gpa = f"""
                SELECT AVG(grade_point) as average_gpa
                FROM {TABLES['grades']} g
                LEFT JOIN {TABLES['students']} s ON g.student_id = s.student_id
                """
                
                if where_clauses:
                    sql_gpa += " WHERE " + " AND ".join(where_clauses)
                    
                self.db.execute(sql_gpa, params)
                gpa_result = self.db.fetchone()
                
                if gpa_result and gpa_result['average_gpa'] is not None:
                    stats['average_gpa'] = round(gpa_result['average_gpa'], 2)
                else:
                    stats['average_gpa'] = 0
            
            # 分数段分布
            sql = f"""
            SELECT
                CASE
                    WHEN score >= 90 THEN '90-100'
                    WHEN score >= 80 THEN '80-89'
                    WHEN score >= 70 THEN '70-79'
                    WHEN score >= 60 THEN '60-69'
                    ELSE '0-59'
                END as score_range,
                COUNT(*) as count
            FROM {TABLES['grades']} g
            LEFT JOIN {TABLES['students']} s ON g.student_id = s.student_id
            """
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            sql += " GROUP BY score_range ORDER BY score_range DESC"
            
            # 执行查询 - 分数段分布
            self.db.execute(sql, params)
            distribution_rows = self.db.fetchall()
            
            # 转换分数段分布到前端期望的格式
            score_ranges = {
                'excellent': 0,
                'good': 0,
                'medium': 0,
                'pass': 0,
                'fail': 0
            }
            
            for row in distribution_rows:
                if row['score_range'] == '90-100':
                    score_ranges['excellent'] = row['count']
                elif row['score_range'] == '80-89':
                    score_ranges['good'] = row['count']
                elif row['score_range'] == '70-79':
                    score_ranges['medium'] = row['count']
                elif row['score_range'] == '60-69':
                    score_ranges['pass'] = row['count']
                elif row['score_range'] == '0-59':
                    score_ranges['fail'] = row['count']
            
            stats['score_ranges'] = score_ranges
            stats['score_distribution'] = {row['score_range']: row['count'] for row in distribution_rows}
            
            # 计算优秀率
            total = stats['total_count'] if stats['total_count'] > 0 else 1
            stats['excellent_rate'] = round((score_ranges['excellent'] / total) * 100, 2)
            
            # 按学期统计
            sql = f"""
            SELECT
                g.semester,
                COUNT(*) as count,
                AVG(score) as avg_score,
                COUNT(CASE WHEN score >= 60 THEN 1 END) as passed_count
            FROM {TABLES['grades']} g
            LEFT JOIN {TABLES['students']} s ON g.student_id = s.student_id
            """
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            sql += " GROUP BY g.semester ORDER BY g.semester"
            
            # 执行查询 - 按学期统计
            self.db.execute(sql, params)
            semester_rows = self.db.fetchall()
            
            for row in semester_rows:
                pass_rate = (row['passed_count'] / row['count']) * 100 if row['count'] > 0 else 0
                stats['semester_stats'][row['semester']] = {
                    'count': row['count'],
                    'avg_score': round(row['avg_score'], 2),
                    'pass_rate': round(pass_rate, 2)
                }
            
            # 按课程统计
            sql = f"""
            SELECT
                g.course_id,
                c.course_name,
                COUNT(*) as count,
                AVG(score) as avg_score,
                COUNT(CASE WHEN score >= 60 THEN 1 END) as passed_count
            FROM {TABLES['grades']} g
            LEFT JOIN {TABLES['students']} s ON g.student_id = s.student_id
            LEFT JOIN {TABLES['courses']} c ON g.course_id = c.course_id
            """
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            sql += " GROUP BY g.course_id ORDER BY avg_score DESC"
            
            # 执行查询 - 按课程统计
            self.db.execute(sql, params)
            course_rows = self.db.fetchall()
            
            for row in course_rows:
                pass_rate = (row['passed_count'] / row['count']) * 100 if row['count'] > 0 else 0
                stats['course_stats'].append({
                    'course_id': row['course_id'],
                    'course_name': row['course_name'],
                    'count': row['count'],
                    'avg_score': round(row['avg_score'], 2),
                    'pass_rate': round(pass_rate, 2)
                })
            
            # 按班级统计
            sql = f"""
            SELECT
                s.class_name,
                COUNT(*) as count,
                AVG(score) as avg_score,
                COUNT(CASE WHEN score >= 60 THEN 1 END) as passed_count
            FROM {TABLES['grades']} g
            LEFT JOIN {TABLES['students']} s ON g.student_id = s.student_id
            """
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            sql += " GROUP BY s.class_name ORDER BY avg_score DESC"
            
            # 执行查询 - 按班级统计
            self.db.execute(sql, params)
            class_rows = self.db.fetchall()
            
            for row in class_rows:
                if row['class_name']:  # 确保班级名称不为空
                    pass_rate = (row['passed_count'] / row['count']) * 100 if row['count'] > 0 else 0
                    stats['class_stats'].append({
                        'class_name': row['class_name'],
                        'count': row['count'],
                        'avg_score': round(row['avg_score'], 2),
                        'pass_rate': round(pass_rate, 2)
                    })
            
            return stats
        except Exception as e:
            logger.error(f"获取成绩统计数据失败: {e}")
            return {
                'error': str(e),
                'total_count': 0,
                'total_students': 0,
                'avg_score': 0,
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0,
                'pass_rate': 0,
                'fail_rate': 0,
                'excellent_rate': 0,
                'average_gpa': 0,
                'score_distribution': {},
                'score_ranges': {'excellent': 0, 'good': 0, 'medium': 0, 'pass': 0, 'fail': 0},
                'semester_stats': {},
                'course_stats': [],
                'class_stats': []
            }