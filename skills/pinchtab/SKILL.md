---
name: pinchtab
description: 控制浏览器使用 PinchTab（HTTP API + CLI 方式）。
---

# pinchtab

控制浏览器使用 PinchTab（HTTP API + CLI 方式）。

## 触发条件

用户提及：
- "浏览器自动化"
- "控制浏览器"
- "打开网页"
- "截图"
- "点击元素"
- "填表单"
- "滚动页面"
- "浏览器操作"

## 前置条件

1. 安装 PinchTab：`curl -fsSL https://pinchtab.com/install.sh | bash` 或 `npm install -g pinchtab`
2. 启动 PinchTab 服务器：`pinchtab`（默认端口 9867）
3. 确认 Chrome 已安装

## 常用操作

### 启动服务器

```bash
pinchtab  # 启动服务器在 localhost:9867
```

### 导航

```bash
pinchtab nav <url>           # 导航到 URL
pinchtab quick <url>         # 快速导航 + 分析页面
```

### 快照与分析

```bash
pinchtab snap                # 获取完整 accessibility 树
pinchtab snap -i             # 仅交互元素（按钮、链接、输入框）
pinchtab snap -c             # 紧凑格式（最省 token）
pinchtab snap -d             # 自上次快照以来的变化
pinchtab snap -s "selector"  # 限定 CSS 选择器范围
pinchtab text                # 提取可读文本
pinchtab text --raw          # 原始文本
```

### 交互操作

```bash
pinchtab click <ref>         # 点击元素（使用 snapshot 中的 ref）
pinchtab type <ref> <text>   # 输入文本
pinchtab fill <ref> <text>   # 直接填充输入框
pinchtab press <key>         # 按键（Enter, Tab, Escape, ArrowDown 等）
pinchtab hover <ref>         # 悬停元素
pinchtab scroll <ref>       # 滚动到元素
pinchtab scroll 500         # 向下滚动 500 像素
pinchtab focus <ref>        # 聚焦元素
pinchtab select <ref> <value>  # 选择下拉选项
```

### 标签页管理

```bash
pinchtab tabs                # 列出所有标签页
pinchtab tabs new <url>      # 新建标签页
pinchtab tabs close <id>    # 关闭标签页
```

### 截图与 PDF

```bash
pinchtab ss                  # 截图
pinchtab ss -o file.png      # 保存截图到文件
pinchtab ss -q 80            # 压缩质量 80%
pinchtab pdf -o output.pdf   # 导出 PDF
```

### JavaScript 执行

```bash
pinchtab eval "document.title"     # 获取页面标题
pinchtab eval "document.querySelectorAll('a').length"  # 计算链接数
```

### 实例管理

```bash
pinchtab instances              # 列出运行中的实例
pinchtab profiles                # 列出可用配置文件
pinchtab health                  # 检查服务器状态
```

## 环境变量

- `PINCHTAB_URL` - 服务器地址（默认 http://127.0.0.1:9867）
- `PINCHTAB_TOKEN` - 认证令牌
- `BRIDGE_HEADLESS` - 无头模式（默认 true，设为 false 可看到浏览器）

## 工作流程

1. 启动 PinchTab：`pinchtab &`（后台运行）
2. 导航：`pinchtab nav https://example.com`
3. 获取快照分析页面：`pinchtab snap -i -c`
4. 根据 ref 进行交互：`pinchtab click e5`
5. 验证结果：`pinchtab snap` 或 `pinchtab ss`

## 注意事项

- 元素 ref 是稳定引用，不同页面会话中可能变化
- 使用 `snap -c` 可以大幅减少 token 消耗
- 复杂操作建议逐 step 验证，避免串行失败
- 遇到问题先检查 `pinchtab health`
