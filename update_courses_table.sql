-- 开始事务
BEGIN TRANSACTION;

-- 创建临时表，包含所有需要的列
CREATE TABLE IF NOT EXISTS courses_temp (
    course_id TEXT PRIMARY KEY,
    course_name TEXT NOT NULL,
    credit REAL NOT NULL,
    teacher TEXT,
    description TEXT,
    semester TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 将旧表中的数据复制到临时表
INSERT INTO courses_temp (course_id, course_name, credit, teacher, description, created_at, updated_at)
SELECT course_id, course_name, credit, teacher, description, created_at, updated_at FROM courses;

-- 删除旧表
DROP TABLE courses;

-- 将临时表重命名为原表名
ALTER TABLE courses_temp RENAME TO courses;

-- 提交事务
COMMIT;