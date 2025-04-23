"""
学生管理系统Web应用入口
"""
import os
import sys
import logging
from flask import Flask, session, g, redirect, url_for
from flask_session import Session

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置
from config.settings import LOGGING_CONFIG, DATABASE_CONFIG

# 导入控制器
from controllers.student_controller import StudentController
from controllers.course_controller import CourseController
from controllers.grade_controller import GradeController
from controllers.user_controller import UserController
from controllers.log_controller import LogController

# 导入数据库
from models.database import Database

# 导入Web视图
from web.views.auth_view import auth_bp
from web.views.student_view import student_bp
from web.views.course_view import course_bp
from web.views.grade_view import grade_bp
from web.views.user_view import user_bp

def create_app():
    """创建Flask应用实例"""
    # 创建应用实例
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # 配置应用
    app.config.update(
        SECRET_KEY=os.urandom(24),
        SESSION_TYPE='filesystem',
        SESSION_FILE_DIR=os.path.join(os.path.dirname(__file__), 'flask_session'),
        SESSION_PERMANENT=False,
        SESSION_USE_SIGNER=True,
        PERMANENT_SESSION_LIFETIME=1800  # 30分钟
    )
    
    # 初始化Session
    Session(app)
    
    # 添加上下文处理器，注入当前日期时间
    @app.context_processor
    def inject_now():
        """注入当前日期时间到所有模板"""
        from datetime import datetime
        return {'now': datetime.now()}
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix='/students')
    app.register_blueprint(course_bp, url_prefix='/courses')
    app.register_blueprint(grade_bp, url_prefix='/grades')
    app.register_blueprint(user_bp, url_prefix='/users')
    
    # 请求前处理
    @app.before_request
    def before_request():
        """每个请求前执行的操作"""
        # 为每个请求创建新的数据库连接
        g.db = Database(DATABASE_CONFIG)
        g.db.connect()
        
        # 初始化控制器
        g.controllers = {
            'student': StudentController(g.db, session.get('user')),
            'course': CourseController(g.db, session.get('user')),
            'grade': GradeController(g.db, session.get('user')),
            'user': UserController(g.db, session.get('user')),
            'log': LogController(g.db, session.get('user'))
        }
    
    # 请求后处理
    @app.teardown_request
    def teardown_request(exception=None):
        """每个请求结束后执行的操作"""
        # 关闭数据库连接
        db = g.pop('db', None)
        if db is not None:
            db.close()
    
    # 主页路由
    @app.route('/')
    def index():
        """主页"""
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return redirect(url_for('student.list'))
    
    # 创建session目录
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    return app

if __name__ == '__main__':
    # 创建应用
    app = create_app()
    
    # 运行应用
    app.run(debug=True, host='0.0.0.0', port=5000)