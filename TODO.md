# 系统问题待办事项

## 1. 登录认证问题

### 问题描述
- 系统默认管理员账户的密码未在文档中明确说明
- 缺少默认密码的配置或文档说明
- 密码重置功能缺乏说明文档

### 相关文件
- `models/database.py`: 包含默认管理员账户创建代码
- `models/user.py`: 包含密码哈希处理逻辑
- `web/views/auth_view.py`: 包含登录验证逻辑

### 建议解决方案
1. 在README.md中添加默认管理员账户信息说明
2. 在首次启动系统时强制修改默认密码
3. 添加密码重置说明文档
4. 考虑添加环境变量配置默认密码的功能

### 技术细节
- 默认管理员用户名: `admin`
- 默认管理员密码: `admin123`
- 密码哈希算法: PBKDF2-SHA256
- 迭代次数: 150000
- 固定盐值: "xtR9ZGgI"

### 优先级
⚠️ 高优先级 - 影响系统初始化使用

## 2. 课程表功能问题

### 问题描述
- 课程表未完成，相关功能不可用或显示异常

### 相关文件
- `controllers/schedule_controller.py`
- `models/schedule.py`
- `web/views/schedule_view.py`
- `web/templates/schedules/index.html`

### 建议解决方案
1. 完成课程表功能开发
2. 确保课程表与课程数据正确关联
3. 添加课程表与学生选课的关联

### 优先级
⚠️ 高优先级 - 核心功能缺失

## 3. 成绩管理匹配问题

### 问题描述
- 成绩尚未和课程管理中的成绩匹配，导致数据不一致

### 相关文件
- `controllers/grade_controller.py`
- `models/grade.py`
- `web/views/grade_view.py`
- `web/templates/grades/list.html`
- `web/templates/grades/statistics.html`

### 建议解决方案
1. 修复成绩数据与课程数据的关联逻辑
2. 确保成绩统计计算正确
3. 添加数据验证，防止无效的成绩录入

### 优先级
⚠️ 高优先级 - 影响数据完整性和准确性