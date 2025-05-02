// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 激活工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 激活弹出框
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // 表单验证
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // 数据表格增强
    var tables = document.querySelectorAll('.table-sortable');
    if (tables.length > 0) {
        Array.from(tables).forEach(function(table) {
            enhanceTable(table);
        });
    }
    
    // 图表初始化
    initCharts();
});

// 增强表格功能
function enhanceTable(table) {
    // 添加排序功能
    var headers = table.querySelectorAll('th[data-sort]');
    headers.forEach(function(header) {
        header.addEventListener('click', function() {
            var column = this.cellIndex;
            var sortDir = this.getAttribute('data-sort-direction') || 'asc';
            var rows = Array.from(table.querySelectorAll('tbody tr'));
            
            rows.sort(function(a, b) {
                var aValue = a.cells[column].textContent.trim();
                var bValue = b.cells[column].textContent.trim();
                
                // 检查是否为数字
                if (!isNaN(aValue) && !isNaN(bValue)) {
                    return sortDir === 'asc' ? aValue - bValue : bValue - aValue;
                }
                
                // 字符串比较
                return sortDir === 'asc' ? 
                    aValue.localeCompare(bValue, 'zh-CN') : 
                    bValue.localeCompare(aValue, 'zh-CN');
            });
            
            // 更新排序方向
            this.setAttribute('data-sort-direction', sortDir === 'asc' ? 'desc' : 'asc');
            
            // 更新表格内容
            var tbody = table.querySelector('tbody');
            rows.forEach(function(row) {
                tbody.appendChild(row);
            });
        });
    });
}

// 初始化图表
function initCharts() {
    // 为确保DOM已完全加载，使用延迟执行
    setTimeout(function() {
        // 检查当前页面是否为统计页面
        var scoreChart = document.getElementById('scoreDistributionChart');
        var gradeChart = document.getElementById('gradeDistributionChart');
        
        if (scoreChart || gradeChart) {
            console.log("检测到统计页面，跳过通用图表初始化");
            return;
        }
        
        // 处理其他页面上的通用图表
        var charts = document.querySelectorAll('[data-chart]');
        if (charts.length > 0) {
            charts.forEach(function(chartElement) {
                try {
                    var ctx = chartElement.getContext('2d');
                    var chartData = JSON.parse(chartElement.getAttribute('data-chart'));
                    var chartType = chartElement.getAttribute('data-chart-type') || 'bar';
                    
                    new Chart(ctx, {
                        type: chartType,
                        data: {
                            labels: chartData.labels,
                            datasets: [{
                                label: chartData.label || '数据',
                                data: chartData.data,
                                backgroundColor: [
                                    'rgba(255, 99, 132, 0.5)',
                                    'rgba(255, 159, 64, 0.5)',
                                    'rgba(255, 205, 86, 0.5)',
                                    'rgba(75, 192, 192, 0.5)',
                                    'rgba(54, 162, 235, 0.5)'
                                ],
                                borderColor: [
                                    'rgb(255, 99, 132)',
                                    'rgb(255, 159, 64)',
                                    'rgb(255, 205, 86)',
                                    'rgb(75, 192, 192)',
                                    'rgb(54, 162, 235)'
                                ],
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: chartType === 'bar' || chartType === 'line' ? {
                                y: {
                                    beginAtZero: true,
                                    ticks: {
                                        precision: 0
                                    }
                                }
                            } : undefined
                        }
                    });
                } catch (e) {
                    console.error("初始化图表失败:", e);
                }
            });
        }
    }, 100); // 添加100ms延迟，确保DOM完全加载
}

// 确认删除
function confirmDelete(message, formId) {
    if (confirm(message)) {
        document.getElementById(formId).submit();
    }
}

// 动态添加表单行
function addFormRow(containerId, template) {
    var container = document.getElementById(containerId);
    var newRow = document.createElement('div');
    newRow.className = 'row mb-3';
    newRow.innerHTML = template;
    container.appendChild(newRow);
}

// 删除表单行
function removeFormRow(btn) {
    var row = btn.closest('.row');
    row.remove();
}