"""
Web学生管理视图模块
"""
import logging
import os
import csv
from io import StringIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, jsonify, send_file

logger = logging.getLogger(__name__)

# 创建蓝图
student_bp = Blueprint('student', __name__)

@student_bp.route('/')
@student_bp.route('/list')
def list():
    """学生列表页面"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    class_name = request.args.get('class_name', '')
    status = request.args.get('status', '')
    keyword = request.args.get('keyword', '')
    
    # 构建过滤条件
    filters = {}
    if class_name:
        filters['class_name'] = class_name
    if status:
        filters['status'] = status
    
    # 获取学生列表
    student_controller = g.controllers.get('student')
    
    if keyword:
        # 搜索学生
        result = student_controller.search_students(keyword)
    else:
        # 获取所有学生
        result = student_controller.get_all_students(filters, page, 10)
    
    if not result['success']:
        flash(result['message'], 'error')
        return render_template('students/list.html',
                              students=[],
                              pagination={},
                              filters={'class_name': class_name, 'status': status, 'keyword': keyword},
                              class_list=[])
    
    # 获取班级列表（用于过滤）
    class_result = student_controller.get_class_list()
    class_list = class_result['data'] if class_result['success'] else []
    
    return render_template('students/list.html', 
                           students=result['data']['items'], 
                           pagination=result['data'],
                           filters={'class_name': class_name, 'status': status, 'keyword': keyword},
                           class_list=class_list)

@student_bp.route('/view/<student_id>')
def view(student_id):
    """查看学生详情"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 获取学生信息
    student_controller = g.controllers.get('student')
    result = student_controller.get_student(student_id)
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for('student.list'))
    
    student = result['data']
    
    # 获取学生成绩
    grade_controller = g.controllers.get('grade')
    grade_result = grade_controller.get_student_grades(student_id)
    grades = grade_result['data']['items'] if grade_result['success'] else []
    
    return render_template('students/view.html', student=student, grades=grades)

@student_bp.route('/add', methods=['GET', 'POST'])
def add():
    """添加学生"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role not in ['admin', 'teacher']:
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('student.list'))
    
    if request.method == 'POST':
        # 收集表单数据
        student_data = {
            'student_id': request.form.get('student_id'),
            'name': request.form.get('name'),
            'gender': request.form.get('gender'),
            'birth_date': request.form.get('birth_date'),
            'class_name': request.form.get('class_name'),
            'admission_date': request.form.get('admission_date'),
            'contact_phone': request.form.get('contact_phone'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'status': request.form.get('status', '在读')
        }
        
        # 添加学生
        student_controller = g.controllers.get('student')
        result = student_controller.add_student(student_data)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('student.list'))
        else:
            flash(result['message'], 'error')
    
    return render_template('students/add.html')

@student_bp.route('/edit/<student_id>', methods=['GET', 'POST'])
def edit(student_id):
    """编辑学生信息"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role not in ['admin', 'teacher']:
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('student.list'))
    
    # 获取学生控制器
    student_controller = g.controllers.get('student')
    
    if request.method == 'POST':
        # 收集表单数据
        update_data = {
            'name': request.form.get('name'),
            'gender': request.form.get('gender'),
            'birth_date': request.form.get('birth_date'),
            'class_name': request.form.get('class_name'),
            'admission_date': request.form.get('admission_date'),
            'contact_phone': request.form.get('contact_phone'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'status': request.form.get('status')
        }
        
        # 过滤空值
        update_data = {k: v for k, v in update_data.items() if v}
        
        # 更新学生信息
        result = student_controller.update_student(student_id, update_data)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('student.view', student_id=student_id))
        else:
            flash(result['message'], 'error')
    
    # 获取学生信息
    result = student_controller.get_student(student_id)
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for('student.list'))
    
    student = result['data']
    
    return render_template('students/edit.html', student=student)

@student_bp.route('/delete/<student_id>', methods=['POST'])
def delete(student_id):
    """删除学生"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role != 'admin':
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('student.list'))
    
    # 删除学生
    student_controller = g.controllers.get('student')
    result = student_controller.delete_student(student_id)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('student.list'))

@student_bp.route('/import', methods=['GET', 'POST'])
def import_students():
    """导入学生数据"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role not in ['admin', 'teacher']:
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('student.list'))
    
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
                students_data = [row for row in reader]
                
                if not students_data:
                    flash('CSV文件中没有数据', 'error')
                    return redirect(request.url)
                
                # 导入学生数据
                student_controller = g.controllers.get('student')
                result = student_controller.import_students(students_data)
                
                if result['success']:
                    data = result['data']
                    flash(f"成功导入 {data['success_count']} 条记录，失败 {data['failed_count']} 条记录", 'success')
                    
                    # 如果有失败记录，显示详情
                    if data['failed_count'] > 0:
                        for record in data['failed_records']:
                            flash(f"学号: {record['data'].get('student_id', '')}, 姓名: {record['data'].get('name', '')}, 原因: {record['reason']}", 'warning')
                else:
                    flash(result['message'], 'error')
            except Exception as e:
                flash(f'导入过程中出错: {str(e)}', 'error')
        else:
            flash('只支持CSV文件格式', 'error')
    
    return render_template('students/import.html')

@student_bp.route('/export')
def export_students():
    """导出学生数据"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 获取过滤条件
    class_name = request.args.get('class_name', '')
    status = request.args.get('status', '')
    
    filters = {}
    if class_name:
        filters['class_name'] = class_name
    if status:
        filters['status'] = status
    
    # 获取所有学生数据
    student_controller = g.controllers.get('student')
    result = student_controller.get_all_students(filters, 1, 1000)  # 获取最多1000条记录
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for('student.list'))
    
    students = result['data']['items']
    
    # 创建CSV文件
    output = StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow(['学号', '姓名', '性别', '出生日期', '班级', '入学日期', '联系电话', '电子邮箱', '地址', '状态'])
    
    # 写入数据
    for student in students:
        writer.writerow([
            student.get('student_id', ''),
            student.get('name', ''),
            student.get('gender', ''),
            student.get('birth_date', ''),
            student.get('class_name', ''),
            student.get('admission_date', ''),
            student.get('contact_phone', ''),
            student.get('email', ''),
            student.get('address', ''),
            student.get('status', '')
        ])
    
    # 设置响应
    output.seek(0)
    return send_file(
        StringIO(output.getvalue()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='students.csv'
    )