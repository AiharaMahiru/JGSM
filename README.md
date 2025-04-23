# 学生管理系统

这是一个功能完备的Python学生管理系统，旨在提供一个高效、稳定的教育管理平台。

## 主要功能

*   **学生信息管理:** 添加、编辑、查看、删除学生基本信息，支持导入导出。
*   **课程信息管理:** 添加、编辑、查看、删除课程信息。
*   **成绩管理:** 录入、修改、查看学生成绩，支持按学期、班级、课程筛选，支持导入导出。
*   **成绩统计分析:** 提供多维度（平均分、最高/低分、及格率、优秀率、分数段分布等）的统计分析，并以图表展示。
*   **用户管理:** (管理员) 添加、编辑、查看、删除用户信息（教师、学生等）。
*   **权限控制:** 基于角色的访问控制（管理员、教师、学生）。
*   **操作日志:** 记录关键操作，便于审计追踪。
*   **双操作模式:** 支持命令行界面 (CLI) 和 Web 用户界面。

## 技术栈

*   **后端:** Python 3
*   **Web 框架:** Flask
*   **数据库:** SQLite
*   **依赖管理:** uv
*   **前端:** Bootstrap 5, HTML, CSS, JavaScript (Chart.js 用于图表)
*   **模板引擎:** Jinja2

## 架构

系统采用经典的 **MVC (Model-View-Controller)** 设计模式：

*   **Model:** 负责数据持久化和业务逻辑核心 (`models/`, `controllers/`)。
*   **View:** 负责用户界面的展示 (CLI: `views/`, Web: `web/templates/`)。
*   **Controller:** 作为模型和视图之间的协调者 (CLI: `main.py`, `views/cli_view.py`, Web: `web/views/`)。

## 安装与设置

1.  **克隆仓库:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **创建并激活虚拟环境 (推荐):**
    ```bash
    # 使用 Python 自带的 venv
    python -m venv .venv
    # Windows
    .\.venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    
    # 或者如果你安装了 uv，可以直接使用 uv 创建
    # uv venv
    # source .venv/bin/activate (或 .\.venv\Scripts\activate)
    ```

3.  **安装依赖:**
    本项目使用 `uv` 进行依赖管理。
    ```bash
    uv sync
    ```

4.  **初始化数据库:**
    首次运行需要初始化数据库并创建表结构以及默认管理员账户。运行命令行主程序即可完成初始化：
    ```bash
    python main.py 
    ```
    (看到系统启动并显示主菜单后，可以按 `q` 退出 CLI)

## 使用说明

系统提供两种操作界面：

### 1. 命令行界面 (CLI)

直接运行主程序启动 CLI：

```bash
python main.py
```

根据菜单提示进行操作。

### 2. Web 界面

确保已至少运行过一次 `python main.py` 来初始化数据库。然后运行 Web 应用：

```bash
python web/app.py
```

系统将在 `http://0.0.0.0:5000` (或者 `http://127.0.0.1:5000`) 启动。在浏览器中打开此地址。

**默认管理员账户:**

*   用户名: `admin`
*   密码: `admin` (请首次登录后立即修改密码)

## 许可证

本学生管理系统基于 **GNU General Public License v3.0 (GPLv3)** 开源。

您可以自由地使用、修改和分发本软件的源代码，但必须遵守 GPLv3 协议的条款，包括保留原始版权声明和开源许可证信息，并以相同的许可证分发您的修改版本。

**商业使用授权:**

虽然本项目基于 GPLv3 开源，允许自由使用和修改，但**任何将本系统的源代码或其衍生版本用于商业目的（例如，销售包含此代码的产品或服务、提供基于此代码的付费支持等）的行为，必须事先获得原作者的书面授权。**

如需商业授权，请联系：**[张同学/2297488292@qq.com]**

## 贡献

欢迎对本项目进行贡献！如果您发现了 Bug 或有功能建议，请随时创建 Issue。如果您想贡献代码，请 Fork 本仓库并提交 Pull Request。