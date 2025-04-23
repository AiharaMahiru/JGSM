"""
Web身份验证视图模块
"""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g

logger = logging.getLogger(__name__)

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('用户名和密码不能为空', 'error')
            return render_template('login.html')
        
        # 验证用户凭据
        user_controller = g.controllers.get('user')
        result = user_controller.login(username, password)
        
        if result['success']:
            # 登录成功，保存用户信息到session
            session['user'] = result['data']
            logger.info(f"用户 {username} 登录成功")
            flash(f"欢迎回来，{result['data'].get('real_name') or username}！", 'success')
            return redirect(url_for('index'))
        else:
            # 登录失败
            logger.warning(f"用户 {username} 登录失败: {result['message']}")
            flash(result['message'], 'error')
            return render_template('login.html')
    
    # GET请求，显示登录页面
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """用户注销"""
    if 'user' in session:
        username = session['user'].get('username')
        logger.info(f"用户 {username} 注销")
        session.pop('user', None)
        flash('您已成功注销', 'success')
    
    return redirect(url_for('auth.login'))