"""
Web课程管理视图模块
"""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g

logger = logging.getLogger(__name__)

# 创建蓝图
course_bp = Blueprint('course', __name__)

@course_bp.route('/')
@course_bp.route('/list')
def list():
    """课程列表页面"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    semester = request.args.get('semester', '')
    keyword = request.args.get('keyword', '')
    
    # 构建过滤条件
    filters = {}
    if semester:
        filters['semester'] = semester
    
    # 获取课程列表
    course_controller = g.controllers.get('course')
    
    if keyword:
        # 搜索课程
        result = course_controller.search_courses(keyword)
    else:
        # 获取所有课程
        result = course_controller.get_all_courses(filters, page, 10)
    
    if not result['success']:
        flash(result['message'], 'error')
        return render_template('courses/list.html', courses=[], pagination={})
    
    # 获取学期列表（用于过滤）
    semester_result = course_controller.get_semester_list()
    semester_list = semester_result['data'] if semester_result['success'] else []
    
    return render_template('courses/list.html', 
                           courses=result['data']['items'], 
                           pagination=result['data'],
                           filters={'semester': semester, 'keyword': keyword},
                           semester_list=semester_list)

@course_bp.route('/view/<course_id>')
def view(course_id):
    """查看课程详情"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 获取课程信息
    course_controller = g.controllers.get('course')
    result = course_controller.get_course(course_id)
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for('course.list'))
    
    course = result['data']
    
    # 获取选修该课程的学生列表
    grade_controller = g.controllers.get('grade')
    
    # 获取当前学期（从请求参数获取，或使用默认值）
    semester = request.args.get('semester', '当前学期')
    
    # 使用get_course_grades方法替代不存在的get_course_students方法
    student_result = grade_controller.get_course_grades(course_id, semester)
    students = student_result['data']['items'] if student_result['success'] else []
    
    return render_template('courses/view.html', course=course, students=students)

@course_bp.route('/add', methods=['GET', 'POST'])
def add():
    """添加课程"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role not in ['admin', 'teacher']:
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('course.list'))
    
    if request.method == 'POST':
        # 收集表单数据
        course_data = {
            'course_id': request.form.get('course_id'),
            'course_name': request.form.get('name'),  # 将name映射为course_name
            'semester': request.form.get('semester'),
            'credit': request.form.get('credit'),
            'teacher': request.form.get('teacher_name'),  # 将teacher_name映射为teacher
            'description': request.form.get('description')
        }
        
        # 添加课程
        course_controller = g.controllers.get('course')
        result = course_controller.add_course(course_data)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('course.list'))
        else:
            flash(result['message'], 'error')
    
    return render_template('courses/add.html')

@course_bp.route('/edit/<course_id>', methods=['GET', 'POST'])
def edit(course_id):
    """编辑课程信息"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role not in ['admin', 'teacher']:
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('course.list'))
    
    # 获取课程控制器
    course_controller = g.controllers.get('course')
    
    if request.method == 'POST':
        # 收集表单数据
        update_data = {
            'course_name': request.form.get('name'),  # 将name映射为course_name
            'semester': request.form.get('semester'),
            'credit': request.form.get('credit'),
            'teacher': request.form.get('teacher_name'),  # 将teacher_name映射为teacher
            'description': request.form.get('description')
        }
        
        # 过滤空值
        update_data = {k: v for k, v in update_data.items() if v}
        
        # 更新课程信息
        result = course_controller.update_course(course_id, update_data)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('course.view', course_id=course_id))
        else:
            flash(result['message'], 'error')
    
    # 获取课程信息
    result = course_controller.get_course(course_id)
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for('course.list'))
    
    course = result['data']
    
    return render_template('courses/edit.html', course=course)

@course_bp.route('/delete/<course_id>', methods=['POST'])
def delete(course_id):
    """删除课程"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role != 'admin':
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('course.list'))
    
    # 删除课程
    course_controller = g.controllers.get('course')
    result = course_controller.delete_course(course_id)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('course.list'))