"""
Web成绩管理视图模块
"""
import logging
import csv
from io import StringIO, BytesIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, send_file

logger = logging.getLogger(__name__)

# 创建蓝图
grade_bp = Blueprint('grade', __name__)

@grade_bp.route('/')
@grade_bp.route('/list')
def list():
    """成绩列表页面"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    student_id = request.args.get('student_id', '')
    course_id = request.args.get('course_id', '')
    semester = request.args.get('semester', '')
    
    # 构建过滤条件
    filters = {}
    if student_id:
        filters['student_id'] = student_id
    if course_id:
        filters['course_id'] = course_id
    if semester:
        filters['semester'] = semester
    
    # 获取成绩列表
    grade_controller = g.controllers.get('grade')
    result = grade_controller.get_all_grades(filters, page, 10)
    
    if not result['success']:
        flash(result['message'], 'error')
        return render_template('grades/list.html',
                              grades=[],
                              pagination={},
                              filters={'student_id': student_id, 'course_id': course_id, 'semester': semester},
                              semester_list=[])
    
    # 获取学期列表（用于过滤）
    course_controller = g.controllers.get('course')
    semester_result = course_controller.get_semester_list()
    semester_list = semester_result['data'] if semester_result['success'] else []
    
    return render_template('grades/list.html', 
                           grades=result['data']['items'], 
                           pagination=result['data'],
                           filters={'student_id': student_id, 'course_id': course_id, 'semester': semester},
                           semester_list=semester_list)

@grade_bp.route('/add', methods=['GET', 'POST'])
def add():
    """添加成绩"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role not in ['admin', 'teacher']:
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('grade.list'))
    
    # 获取学生和课程列表（用于选择）
    student_controller = g.controllers.get('student')
    course_controller = g.controllers.get('course')
    
    student_result = student_controller.get_all_students({}, 1, 1000)
    course_result = course_controller.get_all_courses({}, 1, 1000)
    
    students = student_result['data']['items'] if student_result['success'] else []
    courses = course_result['data']['items'] if course_result['success'] else []
    
    if request.method == 'POST':
        # 收集表单数据
        grade_data = {
            'student_id': request.form.get('student_id'),
            'course_id': request.form.get('course_id'),
            'score': request.form.get('score'),
            'semester': request.form.get('semester')
        }
        
        # 添加成绩
        grade_controller = g.controllers.get('grade')
        result = grade_controller.add_grade(grade_data)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('grade.list'))
        else:
            flash(result['message'], 'error')
    
    return render_template('grades/add.html', students=students, courses=courses)

@grade_bp.route('/edit/<int:grade_id>', methods=['GET', 'POST'])
def edit(grade_id):
    """编辑成绩"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role not in ['admin', 'teacher']:
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('grade.list'))
    
    # 获取成绩控制器
    grade_controller = g.controllers.get('grade')
    
    if request.method == 'POST':
        # 收集表单数据
        update_data = {
            'score': request.form.get('score')
        }
        
        # 更新成绩
        result = grade_controller.update_grade(grade_id, update_data)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('grade.list'))
        else:
            flash(result['message'], 'error')
    
    # 获取成绩信息
    result = grade_controller.get_grade(grade_id)
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for('grade.list'))
    
    grade = result['data']
    
    return render_template('grades/edit.html', grade=grade)

@grade_bp.route('/delete/<int:grade_id>', methods=['POST'])
def delete(grade_id):
    """删除成绩"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role not in ['admin', 'teacher']:
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('grade.list'))
    
    # 删除成绩
    grade_controller = g.controllers.get('grade')
    result = grade_controller.delete_grade(grade_id)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('grade.list'))

@grade_bp.route('/import', methods=['GET', 'POST'])
def import_grades():
    """导入成绩数据"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role not in ['admin', 'teacher']:
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('grade.list'))
    
    if request.method == 'POST':
        # 检查是否有文件上传
        if 'file' not in request.files:
            flash('没有选择文件', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('没有选择文件', 'error')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            try:
                # 读取CSV文件
                content = file.read().decode('utf-8')
                csv_file = StringIO(content)
                reader = csv.DictReader(csv_file)
                grades_data = [row for row in reader]
                
                if not grades_data:
                    flash('CSV文件中没有数据', 'error')
                    return redirect(request.url)
                
                # 导入成绩数据
                grade_controller = g.controllers.get('grade')
                result = grade_controller.import_grades(grades_data)
                
                if result['success']:
                    data = result['data']
                    flash(f"成功导入 {data['success_count']} 条记录，失败 {data['failed_count']} 条记录", 'success')
                    
                    # 如果有失败记录，显示详情
                    if data['failed_count'] > 0:
                        for record in data['failed_records']:
                            flash(f"学号: {record['data'].get('student_id', '')}, 课程: {record['data'].get('course_id', '')}, 原因: {record['reason']}", 'warning')
                else:
                    flash(result['message'], 'error')
            except Exception as e:
                flash(f'导入过程中出错: {str(e)}', 'error')
        else:
            flash('只支持CSV文件格式', 'error')
    
    return render_template('grades/import.html')

@grade_bp.route('/export')
def export_grades():
    """导出成绩数据"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 获取过滤条件
    student_id = request.args.get('student_id', '')
    course_id = request.args.get('course_id', '')
    semester = request.args.get('semester', '')
    
    filters = {}
    if student_id:
        filters['student_id'] = student_id
    if course_id:
        filters['course_id'] = course_id
    if semester:
        filters['semester'] = semester
    
    # 获取所有成绩数据
    grade_controller = g.controllers.get('grade')
    result = grade_controller.get_all_grades(filters, 1, 1000)  # 获取最多1000条记录
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for('grade.list'))
    
    grades = result['data']['items']
    
    # 创建CSV文件
    output = StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow(['学号', '学生姓名', '课程编号', '课程名称', '学期', '成绩', '绩点'])
    
    # 写入数据
    for grade in grades:
        writer.writerow([
            grade.get('student_id', ''),
            grade.get('student_name', ''),
            grade.get('course_id', ''),
            grade.get('course_name', ''),
            grade.get('semester', ''),
            grade.get('score', ''),
            grade.get('grade_point', '')
        ])
    
    # 设置响应
    output.seek(0)
    # 将StringIO转换为BytesIO
    binary_output = BytesIO(output.getvalue().encode('utf-8'))
    binary_output.seek(0)
    return send_file(
        binary_output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='grades.csv'
    )

@grade_bp.route('/statistics')
def statistics():
    """成绩统计分析"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 获取查询参数
    semester = request.args.get('semester', '')
    class_name = request.args.get('class_name', '')
    course_id = request.args.get('course_id', '')
    
    # 构建过滤条件
    filters = {}
    if semester:
        filters['semester'] = semester
    if class_name:
        filters['class_name'] = class_name
    if course_id:
        filters['course_id'] = course_id
    
    # 获取成绩统计数据
    grade_controller = g.controllers.get('grade')
    result = grade_controller.get_grade_statistics(filters)
    
    if not result['success']:
        flash(result['message'], 'error')
        return render_template('grades/statistics.html', statistics={}, filters={})
    
    # 获取学期和班级列表（用于过滤）
    course_controller = g.controllers.get('course')
    student_controller = g.controllers.get('student')
    
    semester_result = course_controller.get_semester_list()
    class_result = student_controller.get_class_list()
    course_result = course_controller.get_all_courses({}, 1, 1000)
    
    semester_list = semester_result['data'] if semester_result['success'] else []
    class_list = class_result['data'] if class_result['success'] else []
    courses = course_result['data']['items'] if course_result['success'] else []
    
    return render_template('grades/statistics.html', 
                           statistics=result['data'], 
                           filters={'semester': semester, 'class_name': class_name, 'course_id': course_id},
                           semester_list=semester_list,
                           class_list=class_list,
                           courses=courses)