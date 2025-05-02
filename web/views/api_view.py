"""
API路由视图模块，处理所有API请求
"""
import logging
import json
from flask import Blueprint, request, jsonify, session, g

logger = logging.getLogger(__name__)

# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 通用错误响应
def error_response(message, code=400):
    """返回API错误响应"""
    return jsonify({
        'success': False,
        'message': message,
        'code': code
    }), code

# 检查用户是否登录
def check_login():
    """检查用户是否登录"""
    if 'user' not in session:
        return False
    return True

# 课程API路由
@api_bp.route('/courses', methods=['GET'])
def get_courses():
    """获取课程列表API"""
    if not check_login():
        return error_response('未登录', 401)
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 100, type=int)
    semester = request.args.get('semester', '')
    
    # 构建过滤条件
    filters = {}
    if semester:
        filters['semester'] = semester
    
    # 获取课程列表
    course_controller = g.controllers.get('course')
    result = course_controller.get_all_courses(filters, page, limit)
    
    if not result['success']:
        return jsonify({
            'success': False,
            'message': result['message']
        })
    
    return jsonify(result)

# 课程表API路由
@api_bp.route('/schedules', methods=['GET'])
def get_schedules():
    """获取课程表API"""
    if not check_login():
        return error_response('未登录', 401)
    
    # 获取查询参数
    semester = request.args.get('semester', '')
    week = request.args.get('week')
    day = request.args.get('day')
    course_id = request.args.get('course_id', '')
    
    if not semester:
        return error_response('semester参数为必填')
    
    # 转换week为整数（如果提供）
    if week is not None:
        try:
            week = int(week)
        except ValueError:
            return error_response('week参数必须为整数')
    
    # 获取课程表
    schedule_controller = g.controllers.get('schedule')
    result = schedule_controller.get_schedule(semester, week, day, course_id)
    
    return jsonify(result)

@api_bp.route('/schedules/<int:schedule_id>', methods=['GET'])
def get_schedule_item(schedule_id):
    """获取单个课程表项API"""
    if not check_login():
        return error_response('未登录', 401)
    
    # 获取课程表项
    schedule_controller = g.controllers.get('schedule')
    result = schedule_controller.get_schedule_item(schedule_id)
    
    return jsonify(result)

@api_bp.route('/schedules', methods=['POST'])
def add_schedule_item():
    """添加课程表项API"""
    if not check_login():
        return error_response('未登录', 401)
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role not in ['admin', 'teacher']:
        return error_response('权限不足', 403)
    
    # 获取请求数据
    try:
        schedule_data = request.json
    except Exception:
        return error_response('无效的JSON数据')
    
    # 添加课程表项
    schedule_controller = g.controllers.get('schedule')
    result = schedule_controller.add_schedule_item(schedule_data)
    
    return jsonify(result)

@api_bp.route('/schedules/<int:schedule_id>', methods=['PUT'])
def update_schedule_item(schedule_id):
    """更新课程表项API"""
    if not check_login():
        return error_response('未登录', 401)
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role not in ['admin', 'teacher']:
        return error_response('权限不足', 403)
    
    # 获取请求数据
    try:
        update_data = request.json
    except Exception:
        return error_response('无效的JSON数据')
    
    # 更新课程表项
    schedule_controller = g.controllers.get('schedule')
    result = schedule_controller.update_schedule_item(schedule_id, update_data)
    
    return jsonify(result)

@api_bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule_item(schedule_id):
    """删除课程表项API"""
    if not check_login():
        return error_response('未登录', 401)
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role not in ['admin', 'teacher']:
        return error_response('权限不足', 403)
    
    # 删除课程表项
    schedule_controller = g.controllers.get('schedule')
    result = schedule_controller.delete_schedule_item(schedule_id)
    
    return jsonify(result)

@api_bp.route('/schedules/semesters', methods=['GET'])
def get_semesters():
    """获取学期列表API"""
    if not check_login():
        return error_response('未登录', 401)
    
    # 获取学期列表
    schedule_controller = g.controllers.get('schedule')
    result = schedule_controller.get_semesters()
    
    return jsonify(result)

@api_bp.route('/schedules/batch', methods=['POST'])
def batch_import_schedule():
    """批量导入课程表API"""
    if not check_login():
        return error_response('未登录', 401)
    
    # 检查权限
    user_role = session['user'].get('role')
    if user_role != 'admin':
        return error_response('权限不足', 403)
    
    # 获取请求数据
    try:
        schedule_data_list = request.json
    except Exception:
        return error_response('无效的JSON数据')
    
    # 批量导入课程表
    schedule_controller = g.controllers.get('schedule')
    result = schedule_controller.batch_import_schedule(schedule_data_list)
    
    return jsonify(result)