"""
学生管理系统主程序入口
"""
import os
import sys
import logging
import logging.config
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入配置
from config.settings import LOGGING_CONFIG, DATABASE_CONFIG

# 导入控制器
from controllers.student_controller import StudentController
from controllers.course_controller import CourseController
from controllers.grade_controller import GradeController
from controllers.user_controller import UserController
from controllers.log_controller import LogController

# 导入视图
from views.cli_view import CommandLineView
from views.cli_student_view import CLIStudentView
from views.cli_course_view import CLICourseView
from views.cli_grade_view import CLIGradeView
from views.cli_user_view import CLIUserView
from views.cli_log_view import CLILogView

def setup_logging():
    """配置日志系统"""
    os.makedirs('logs', exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info("日志系统初始化完成")
    return logger

def init_database():
    """初始化数据库"""
    from models.database import Database
    db = Database(DATABASE_CONFIG)
    db.init_database()
    return db

def init_controllers(db):
    """
    初始化控制器
    
    参数:
        db: 数据库实例
    
    返回:
        dict: 控制器字典
    """
    controllers = {
        'student': StudentController(db),
        'course': CourseController(db),
        'grade': GradeController(db),
        'user': UserController(db),
        'log': LogController(db)
    }
    return controllers

def init_views(controllers, db):
    """
    初始化视图
    
    参数:
        controllers: 控制器字典
        db: 数据库实例
    
    返回:
        CommandLineView: 命令行界面视图实例
    """
    # 创建主视图
    cli_view = CommandLineView(controllers, db)
    
    # 创建子视图并关联到主视图
    student_view = CLIStudentView(cli_view, controllers['student'], controllers['grade'])
    course_view = CLICourseView(cli_view, controllers['course'], controllers['grade'])
    grade_view = CLIGradeView(cli_view, controllers['grade'], controllers['student'], controllers['course'])
    user_view = CLIUserView(cli_view, controllers['user'])
    log_view = CLILogView(cli_view, controllers['log'])
    
    # 将子视图方法绑定到主视图
    cli_view.show_student_management = student_view.show_student_management
    cli_view.show_course_management = course_view.show_course_management
    cli_view.show_grade_management = grade_view.show_grade_management
    cli_view.show_user_management = user_view.show_user_management
    cli_view.show_system_logs = log_view.show_system_logs
    cli_view.show_personal_info = user_view.show_personal_info
    cli_view.show_change_password = user_view.show_change_password
    
    return cli_view

def main():
    """主程序入口"""
    print("正在启动学生管理系统...")
    
    # 设置日志
    logger = setup_logging()
    logger.info("学生管理系统启动")
    
    try:
        # 初始化数据库
        db = init_database()
        logger.info("数据库初始化完成")
        
        # 初始化控制器
        controllers = init_controllers(db)
        logger.info("控制器初始化完成")
        
        # 初始化视图
        view = init_views(controllers, db)
        logger.info("视图初始化完成")
        
        # 运行视图
        view.run()
        
        logger.info("学生管理系统正常退出")
    except Exception as e:
        logger.error(f"系统运行出错: {str(e)}", exc_info=True)
        print(f"系统出现错误: {str(e)}")
        print("请查看日志文件获取详细信息。")
    finally:
        print("学生管理系统已退出。")

if __name__ == "__main__":
    main()