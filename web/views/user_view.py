"""
Web用户管理视图模块
"""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g

logger = logging.getLogger(__name__)

# 创建蓝图
user_bp = Blueprint('user', __name__)

@user_bp.route('/')
@user_bp.route('/list')
def list():
    """用户列表页面"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role != 'admin':
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('index'))
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role', '')
    keyword = request.args.get('keyword', '')
    
    # 构建过滤条件
    filters = {}
    if role:
        filters['role'] = role
    
    # 获取用户列表
    user_controller = g.controllers.get('user')
    
    if keyword:
        # 搜索用户
        result = user_controller.search_users(keyword)
    else:
        # 获取所有用户
        result = user_controller.get_all_users(filters, page, 10)
    
    if not result['success']:
        flash(result['message'], 'error')
        return render_template('users/list.html', users=[], pagination={})
    
    return render_template('users/list.html', 
                           users=result['data']['items'], 
                           pagination=result['data'],
                           filters={'role': role, 'keyword': keyword})

@user_bp.route('/view/<username>')
def view(username):
    """查看用户详情"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    current_username = session['user'].get('username')
    user_role = session['user'].get('role')
    
    if user_role != 'admin' and current_username != username:
        flash('您没有权限查看此用户信息', 'error')
        return redirect(url_for('index'))
    
    # 获取用户信息
    user_controller = g.controllers.get('user')
    result = user_controller.get_user(username)
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for('user.list') if user_role == 'admin' else url_for('index'))
    
    user = result['data']
    
    # 获取用户操作日志
    log_controller = g.controllers.get('log')
    log_result = log_controller.get_user_logs(username, 1, 10)
    logs = log_result['data']['items'] if log_result['success'] else []
    
    return render_template('users/view.html', user=user, logs=logs)

@user_bp.route('/add', methods=['GET', 'POST'])
def add():
    """添加用户"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role != 'admin':
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # 收集表单数据
        user_data = {
            'username': request.form.get('username'),
            'password': request.form.get('password'),
            'real_name': request.form.get('real_name'),
            'role': request.form.get('role'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone')
        }
        
        # 添加用户
        user_controller = g.controllers.get('user')
        result = user_controller.add_user(user_data)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('user.list'))
        else:
            flash(result['message'], 'error')
    
    return render_template('users/add.html')

@user_bp.route('/edit/<username>', methods=['GET', 'POST'])
def edit(username):
    """编辑用户信息"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    current_username = session['user'].get('username')
    user_role = session['user'].get('role')
    
    if user_role != 'admin' and current_username != username:
        flash('您没有权限修改此用户信息', 'error')
        return redirect(url_for('index'))
    
    # 获取用户控制器
    user_controller = g.controllers.get('user')
    
    if request.method == 'POST':
        # 收集表单数据
        update_data = {}
        
        # 只有管理员可以修改角色
        if user_role == 'admin':
            role = request.form.get('role')
            if role:
                update_data['role'] = role
        
        # 其他信息
        real_name = request.form.get('real_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        if real_name:
            update_data['real_name'] = real_name
        if email:
            update_data['email'] = email
        if phone:
            update_data['phone'] = phone
        
        # 更新用户信息
        result = user_controller.update_user(username, update_data)
        
        if result['success']:
            flash(result['message'], 'success')
            
            # 如果是当前用户，更新session中的用户信息
            if current_username == username:
                user_result = user_controller.get_user(username)
                if user_result['success']:
                    session['user'] = user_result['data']
            
            return redirect(url_for('user.view', username=username))
        else:
            flash(result['message'], 'error')
    
    # 获取用户信息
    result = user_controller.get_user(username)
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for('user.list') if user_role == 'admin' else url_for('index'))
    
    user = result['data']
    
    return render_template('users/edit.html', user=user)

@user_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """修改密码"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    username = session['user'].get('username')
    
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not old_password or not new_password or not confirm_password:
            flash('所有字段都必须填写', 'error')
            return render_template('users/change_password.html')
        
        if new_password != confirm_password:
            flash('新密码和确认密码不匹配', 'error')
            return render_template('users/change_password.html')
        
        # 修改密码
        user_controller = g.controllers.get('user')
        result = user_controller.change_password(username, old_password, new_password)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('user.view', username=username))
        else:
            flash(result['message'], 'error')
    
    return render_template('users/change_password.html')

@user_bp.route('/delete/<username>', methods=['POST'])
def delete(username):
    """删除用户"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 检查权限
    user_role = session['user'].get('role')
    current_username = session['user'].get('username')
    
    if user_role != 'admin':
        flash('您没有权限执行此操作', 'error')
        return redirect(url_for('index'))
    
    # 不能删除自己
    if current_username == username:
        flash('不能删除当前登录的用户', 'error')
        return redirect(url_for('user.list'))
    
    # 删除用户
    user_controller = g.controllers.get('user')
    result = user_controller.delete_user(username)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('user.list'))

@user_bp.route('/profile')
def profile():
    """查看个人资料"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    username = session['user'].get('username')
    return redirect(url_for('user.view', username=username))