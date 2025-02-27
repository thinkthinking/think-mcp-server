# -*- coding: utf-8 -*-
"""模板文件管理模块，用于存放模板文件内容。"""

# .env 文件模板 - Unix 系统 (macOS/Linux)
ENV_TEMPLATE_UNIX = """# MCP Server 配置文件

# 基础路径配置
prompts_path=~/.think-mcp-server/prompts
resources_path=~/.think-mcp-server/resources

# 文章分析工具配置
article_base_path=~/src_code/nas/knowledge/Articles
max_tokens_limit=89600

# 内容分析工具配置
content_analyzer_prompt_path=~/.think-mcp-server/resources/tool_content_analyzer_prompt.md
"""

# .env 文件模板 - Windows 系统
ENV_TEMPLATE_WINDOWS = """# MCP Server 配置文件

# 基础路径配置
prompts_path={home_dir}/.think-mcp-server/prompts
resources_path={home_dir}/.think-mcp-server/resources

# 文章分析工具配置
article_base_path={home_dir}/src_code/nas/knowledge/Articles
max_tokens_limit=89600

# 内容分析工具配置
content_analyzer_prompt_path={home_dir}/.think-mcp-server/resources/tool_content_analyzer_prompt.md
"""

# 内容分析工具提示词模板
CONTENT_ANALYZER_PROMPT_TEMPLATE = """---
name: "content-analyzer"
description: "分析内容，提取关键信息"
arguments:
  - name: "content"
    description: "需要分析的内容"
    required: true
---

你是一个专业的内容分析专家。请分析以下内容，提取关键信息，并按照要求进行输出。

内容：
{{content}}

请提取以下信息：
1. 主题
2. 关键点
3. 情感倾向
4. 建议或行动项

输出格式：
```json
{
  "topic": "主题",
  "key_points": ["关键点1", "关键点2", ...],
  "sentiment": "正面/负面/中性",
  "suggestions": ["建议1", "建议2", ...]
}
```
"""

# 提示词模板
PROMPTS_TEMPLATE = """---
name: "example-prompt"
description: "示例提示词模板"
arguments:
  - name: "query"
    description: "用户查询"
    required: true
  - name: "context"
    description: "上下文信息"
    required: false
---

# 示例提示词

你是一个专业的助手，请根据以下信息回答用户的问题。

## 用户查询
{{query}}

## 上下文信息
{{context}}

请提供简洁、准确的回答，并在必要时引用上下文信息。
"""

# 资源模板
RESOURCES_TEMPLATE = """---
name: "example-resource"
description: "示例资源文件"
---

# 示例资源文件

这是一个示例资源文件，可以包含各种信息，如参考资料、指南、模板等。

## 使用方法

1. 将此文件放在资源目录中
2. 在代码中引用此资源
3. 根据需要修改内容

## 示例内容

这里可以放置任何需要在应用中使用的文本内容。
"""

# 智能体介绍模板
AGENT_INTRODUCTION_TEMPLATE = """---
name: "agent-introduction"
description: "根据智能体名称和主要功能，生成富有个性的智能体介绍"
arguments:
  - name: "agent_name"
    description: "智能体名称"
    required: true
  - name: "agent_function"
    description: "智能体主要功能"
    required: true
---

# 智能体介绍生成器

## 智能体名称
{{agent_name}}

## 主要功能
{{agent_function}}

## 生成要求
1. 创建一个简短但吸引人的介绍
2. 突出智能体的主要功能和优势
3. 使用友好、专业的语气
4. 添加一个号召性用语，鼓励用户尝试
5. 总字数控制在100-150字之间

## 示例格式
你好，我是[智能体名称]，你的[功能描述]助手。我能帮你[具体功能1]、[具体功能2]和[具体功能3]，让你的[相关任务]变得更加轻松高效。无论你是需要[使用场景1]还是[使用场景2]，我都能提供专业的支持。有[相关问题]？请随时向我咨询！
"""

# 简历时间线模板
CV_TIMELINE_TEMPLATE = """---
description: 【技术工具文档】解决个人简历可视化生成问题。通过Lisp脚本自动获取职业信息并设计SVG图表，快速创建包含工作经历和项目经验的优化简历。
name: cv-timeline
---

;; 个人简历时间线生成工具
;; 使用Lisp语言编写的SVG时间线生成脚本

(defun 生成简历时间线 (主题)
  "生成主题的简历时间线SVG"
  (let ((工作经历 (获取工作经历 主题))
        (项目经验 (获取项目经验 主题)))
    (生成SVG工作经历 工作经历)
    (生成SVG项目经验 项目经验)))

(defun 获取工作经历 (主题)
  "获取主题的工作经历"
  (case 主题
    (我的简历 '(("AgentOS首席产品架构师" "土豆数据科技集团有限公司" "2023年7月 - 至今")
                ("AI技术产品经理" "百度在线网络技术（北京）有限公司" "2022年9月 - 2023年7月")
                ("高级软件工程师" "北京字节跳动科技有限公司" "2020年3月 - 2022年8月")
                ("算法工程师" "阿里巴巴（中国）有限公司" "2018年7月 - 2020年2月")))
    (t nil)))

(defun 获取项目经验 (主题)
  "获取主题的项目经验"
  (case 主题
    (我的简历 '(("AgentOS·智能体操作系统" "设计并实现了AgentOS智能体操作系统的核心架构，包括智能体管理、工具调用、记忆系统等核心模块。")
                ("文心一言·对话能力" "负责文心一言对话能力的产品设计与优化，提升了模型的对话连贯性和信息准确性。")
                ("抖音电商·推荐算法" "开发抖音电商的个性化推荐算法，提高了用户购买转化率和平台GMV。")
                ("淘宝搜索·排序优化" "优化淘宝搜索的排序算法，提升了搜索结果的相关性和用户体验。")))
    (其他简历 '(("自动驾驶·感知算法" "负责自动驾驶感知算法的研发，包括目标检测、跟踪和场景理解等模块。")
                ("CTC滑动底盘项目·自动驾驶视觉感知算法开发" "基于ROS开发自动驾驶系统的视觉感知算法，包括2D/3D目标物检测、跟踪算法及车道线识别算法。")
                ("无线BMS项目·无线BMS跳频通信算法开发" "完成无线BMS项目的跳频通信整体架构设计及跳频通信算法开发。")
                ("V2X产品·车路协同产品设计" "负责V2X产品的规划设计，包括V2X-Box、V2X-RSU等产品。")))
    (t nil)))
"""
