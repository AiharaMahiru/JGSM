"""
Web课程表管理视图模块
"""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g

logger = logging.getLogger(__name__)

# 创建蓝图
schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('/')
@schedule_bp.route('/index')
def index():
    """课程表页面"""
    # 检查用户是否登录
    if 'user' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login'))
    
    # 课程表页面不需要直接获取数据，数据将通过AJAX API请求加载
    return render_template('schedules/index.html')