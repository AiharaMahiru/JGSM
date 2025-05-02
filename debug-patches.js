// 在loadSemesters函数中添加更详细的错误捕获
async function loadSemesters() {
    try {
        console.log("发送请求获取学期列表...");
        console.log("完整请求URL:", window.location.origin + '/api/schedules/semesters');
        
        const response = await fetch('/api/schedules/semesters');
        console.log("学期列表API响应状态:", response.status);
        console.log("学期列表API响应头:", Object.fromEntries([...response.headers]));
        
        if (!response.ok) {
            console.error(`HTTP错误! 状态: ${response.status} ${response.statusText}`);
            const errorText = await response.text();
            console.error("错误响应内容:", errorText);
            throw new Error(`HTTP错误! 状态: ${response.status} ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log("学期列表API响应数据:", result);
        
        // 其余逻辑保持不变...
    } catch (error) {
        console.error('获取学期列表异常:', error);
        console.error('错误堆栈:', error.stack);
        showMessage('获取学期列表异常: ' + error.message, 'danger');
        throw error;
    }
}

// 在loadScheduleData函数中添加更详细的错误捕获
async function loadScheduleData(semester, week = null) {
    try {
        console.log(`开始加载课程表数据, 学期: ${semester}, 周次: ${week || '全部'}`);
        
        // ... 保留原有代码 ...
        
        // 构建API URL
        let url = `/api/schedules?semester=${encodeURIComponent(semester)}`;
        if (week) {
            url += `&week=${week}`;
        }
        console.log("API请求URL:", url);
        console.log("完整请求URL:", window.location.origin + url);
        
        // 发送请求
        console.log("发送课程表数据请求...");
        const response = await fetch(url);
        console.log("课程表API响应状态:", response.status);
        console.log("课程表API响应头:", Object.fromEntries([...response.headers]));
        
        if (!response.ok) {
            console.error(`HTTP错误! 状态: ${response.status} ${response.statusText}`);
            const errorText = await response.text();
            console.error("错误响应内容:", errorText);
            throw new Error(`HTTP错误! 状态: ${response.status} ${response.statusText}`);
        }
        
        // ... 保留原有代码 ...
    } catch (error) {
        console.error('获取课程表异常:', error);
        console.error('错误堆栈:', error.stack);
        // ... 保留原有代码 ...
    }
}