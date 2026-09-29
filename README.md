\# AI 电脑故障诊断助手



一个基于 Flask、SQLite 和规则诊断机制开发的电脑故障诊断 Web 应用。



用户可以输入电脑、Windows、软件或游戏相关的故障描述，系统会根据故障信息进行初步分析，并提供可能原因、排查步骤和解决建议。



项目同时预留了 AI 接口，可以在配置 API 后使用 AI 进行进一步分析；在 AI 接口不可用时，系统会自动切换到本地 Demo 模式，因此项目仍然可以在本地运行。



\---



\## 项目功能



\- 电脑故障描述输入

\- 故障初步分析

\- 可能原因分析

\- 故障排查步骤

\- 解决方案建议

\- AI 诊断模式

\- 本地 Demo 规则诊断模式

\- AI 调用失败自动切换 Demo 模式

\- SQLite 诊断历史记录

\- 历史诊断详情查看

\- 历史记录删除

\- Web 页面交互



\---



\## 技术栈



\### 后端



\- Python

\- Flask

\- SQLite



\### 前端



\- HTML

\- CSS

\- JavaScript



\### AI



\- OpenAI API

\- 本地规则诊断作为备用方案



\---



\## 项目结构



```text

AI-Fault-Diagnosis/

│

├── app.py

├── database.py

├── requirements.txt

├── README.md

├── .gitignore

│

├── templates/

│   └── index.html

│

└── static/

&#x20;   └── style.css

