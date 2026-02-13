# 🚀 EasyBot v0.2: 你的全能 AI 智能体桌面助手 (基于 Nanobot)

> **零代码 · 极致稳定 · 原生中文支持 · 多模型精细切换 · 你的私人 AI 专家**

![EasyBot 截图](images/figures/图1.png)

## 📖 简介 | Introduction

**EasyBot** 是为普通用户量身打造的 **[Nanobot](https://github.com/HKUDS/nanobot)** 桌面封装版。它不仅仅是一个聊天工具，更是一个能帮你处理复杂任务的 **AI 智能体 (AI Agent)**。

我们深知，虽然现在的 AI 模型（如 DeepSeek-V3、Qwen-Max）非常强大，但繁琐的 Python 环境配置、依赖缺失报错以及编码问题，将许多非技术用户拒之门外。

**EasyBot v0.2 的使命是“稳定与易用”：** 让最顶尖的 AI 触手可及。你**不需要写一行代码**，也不用懂什么是 Python，只需填入 API Key，就能瞬间拥有一个强大的本地智能助手。



## 💡 我能用它做什么？ | Use Cases

EasyBot 就像是一个住在你电脑里的全能专家，随时待命：

*   🎓 **学术科研**：帮你阅读几百页的论文 PDF，提取关键数据，帮你润色英文摘要。
*   💻 **代码编写**：我是程序员的好帮手，能帮你写脚本、查 Bug、解释复杂的代码逻辑。
*   📝 **文案创作**：无论是写周报、写小说还是写小红书文案，都能信手拈来。
*   🌍 **多语言翻译**：精准的英中互译，比机翻更懂语境。



## 🧠 支持的模型列表 | Supported Models

我们内置了目前最强大的中文 AI 模型配置，并在本地进行了适配优化：

| 厂商 | 支持模型 (部分) | 特点 |
| :--- | :--- | :--- |
| **DeepSeek (深度求索)** | `deepseek-chat` (V3), `deepseek-coder` | 目前最火的开源模型，逻辑与代码能力超强 |
| **Tongyi Qwen (通义千问)** | `qwen-max`, `qwen-plus`, `qwen-long` | 阿里出品，知识储备丰富，懂中文更懂中国文化 |
| **Moonshot Kimi (月之暗面)** | `moonshot-v1-8k/32k/128k` | 长文本处理专家，能一口气读完长篇小说或财报 |
| **Zhipu GLM (智谱清言)** | `glm-4`, `glm-4-flash` | 全能型选手，综合能力均衡，指令遵循度高 |


## 🚀 快速开始 | Quick Start

1.  下载本仓库 Release 中的 **`EasyBot_v0.2.zip`** 压缩包。
2.  解压文件到任意位置（建议不要包含中文路径）。
3.  双击运行 **`EasyBot.exe`**。
4.  在左侧选择你喜欢的**AI 厂商**（如 DeepSeek），然后在下拉框中选择**具体模型**（如 `deepseek-chat`）。
5.  **填入 API Key**（点击界面蓝色链接可直达申请页面）。
6.  点击 **“保存并应用”**，然后点击 **“启动助手”**，即可开始丝滑对话！



## ⚠️ 常见问题 (FAQ)

*   **Q: 启动后点击“启动助手”没有反应？**
    *   A: 请检查 API Key 是否正确复制。如果 Key 错误，软件会自动拦截并提示。
*   **Q: 为什么生成的体积比以前小了？**
    *   A: v0.2 采用了智能依赖收集技术，剔除了无关的测试代码和文档，核心功能不受影响。



## 🙏 致谢 | Credits

本项目核心功能基于 **Nanobot** 构建。感谢原作者团队的杰出工作！
This project is built upon the amazing work of [Nanobot](https://github.com/HKUDS/nanobot).