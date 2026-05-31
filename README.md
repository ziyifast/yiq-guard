# yiQGuard

<p align="center">
  <img src="icon_preview.png" width="128" height="128" alt="yiQGuard Icon">
</p>

<p align="center">
  <strong>macOS 防误触 Command+Q 守护工具</strong><br>
  再也不怕手滑退出应用了
</p>

<p align="center">
  <a href="#安装">安装</a> |
  <a href="#使用说明">使用</a> |
  <a href="#从源码构建">构建</a> |
  <a href="#项目架构">架构</a> |
  <a href="TUTORIAL.md">开源教程</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%2012%2B-blue" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.9%20~%203.13-green" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange" alt="License">
  <img src="https://img.shields.io/badge/brand-ziyi-purple" alt="Brand">
</p>

---

## 为什么需要它？

`Command+Q`（退出应用）和 `Command+W`（关闭窗口）只差一个键。

手指稍微偏一下——正在写的文档、刚搭好的调试环境、还没保存的设计稿——全没了。

**yiQGuard** 常驻菜单栏，在系统层面拦截 `Cmd+Q`，给你一次"后悔"的机会。

---

## 功能特性

| 特性 | 说明 |
|------|------|
| 🛡 菜单栏常驻 | 无 Dock 图标，启动时 Toast 提醒 |
| 🔄 双击模式（默认） | 1.5 秒内连按两次 Cmd+Q 才退出，单次无效 |
| 💬 确认模式 | 按 Cmd+Q 弹出确认框，点"退出"才真正退出 |
| ⌨️ 快捷键可自定义 | 设置面板中自由修改 |
| 🔒 自我保护 | yiQGuard 不可被 Cmd+Q 退出 |
| 🌐 系统级保护 | 保护所有应用，无论何时打开 |

---

## 安装

### 方式一：直接下载（推荐，不需要 Python）

1. 前往 [Releases](https://github.com/ziyi/yiq-guard/releases) 页面
2. 下载最新版 `yiQGuard-vX.X.X-macOS.zip`
3. 解压，将 `yiQGuard.app` 拖入 `/Applications`
4. 双击运行

> ⚠️ 首次打开提示"无法验证开发者"？→ 右键点击 .app → 选择"打开"

### 方式二：Homebrew（即将支持）

```bash
# TODO: 待发布 tap 后可用
brew install --cask ziyi/tap/yiq-guard
```

### 首次授权

macOS 需要辅助功能权限：

1. 首次启动时系统弹出授权提示
2. 「系统设置 → 隐私与安全性 → 辅助功能」→ 勾选 yiQGuard
3. 重启程序 → 看到 Toast "🛡 yiQGuard 已启动" 即成功

### 开机自启

「系统设置 → 通用 → 登录项」→ 添加 yiQGuard

### 卸载

```bash
bash uninstall.sh
```

或手动：删除 .app → 删除 `~/.yiq-guard/` → 系统设置中移除辅助功能授权

---

## 使用说明

### 菜单栏

启动后菜单栏出现 `⌘Q🛡`。点击展开：

```
┌──────────────────────────────────────┐
│  🛡 yiQGuard 保护中                  │
├──────────────────────────────────────┤
│  打开设置…                            │
├──────────────────────────────────────┤
│  ✅ 保护已启用（点击关闭）            │
├──────────────────────────────────────┤
│  保护模式                             │
│    ⬜ 弹窗确认                        │
│    ✅ 双击 Cmd+Q（1.5s 内）          │
├──────────────────────────────────────┤
│  退出 yiQGuard（⌃⌥⇧Q）             │
└──────────────────────────────────────┘
```

### 保护模式

| 模式 | 行为 |
|------|------|
| **双击 Cmd+Q**（默认） | 第一次 Toast 提示，1.5s 内再按才退出 |
| **弹窗确认** | 弹对话框，取消后焦点自动回原应用 |

### 快捷键

| 快捷键 | 功能 | 可自定义 |
|--------|------|----------|
| `Ctrl+Option+Q` | 打开设置面板 | ✅ |
| `Ctrl+Option+Shift+Q` | 退出 yiQGuard | ✅ |

### 自我保护

- Cmd+Q **无法**退出 yiQGuard
- 退出需通过菜单或快捷键 + 二次确认

---

## 配置

`~/.yiq-guard/config.json`：

```json
{
  "enabled": true,
  "mode": "double_press",
  "settings_hotkey": { "ctrl": true, "option": true, "shift": false, "key": "q" },
  "quit_hotkey": { "ctrl": true, "option": true, "shift": true, "key": "q" }
}
```

也可在设置面板中可视化修改。

---

## 从源码构建

> 适合开发者、贡献者，或想自己编译的用户。

### 一键构建

```bash
git clone https://github.com/ziyi/yiq-guard.git
cd yiq-guard

bash build.sh --run       # 源码直接运行（测试）
bash build.sh --alias     # 别名模式打包（快速验证）
bash build.sh             # 正式打包 → dist/yiQGuard.app
```

`build.sh` 会自动处理：Python 版本检测、虚拟环境创建、依赖安装、打包。

### 手动步骤（如果 build.sh 不适用）

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install py2app

# 运行
python main.py

# 或打包
python setup.py py2app
```

### 环境要求

| 项目 | 版本 |
|------|------|
| macOS | 12.0+ |
| Python | 3.9 ~ 3.13 |

> `requirements.txt` 不锁版本，pip 会自动选择与你 Python 版本兼容的 PyObjC。

---

## 项目架构

```
yiq-guard/
├── main.py                    # 入口
├── build.sh                   # 一键打包
├── release.sh                 # 发布打包（生成 .zip）
├── uninstall.sh               # 一键卸载
├── setup.py                   # py2app 配置
├── requirements.txt           # 依赖（不锁版本）
│
├── yiqguard/                  # 核心包
│   ├── app_delegate.py        # 主控制器
│   ├── event_tap.py           # CGEventTap 拦截
│   ├── config.py              # 配置 + 快捷键工具
│   ├── permissions.py         # 权限检查
│   ├── modes/
│   │   ├── confirm_mode.py    # 弹窗模式
│   │   └── double_press_mode.py  # 双击模式 (1.5s)
│   └── ui/
│       ├── menu_bar.py        # 菜单栏
│       ├── settings_window.py # 设置面板
│       └── toast.py           # Toast
│
└── tests/                     # 46 项测试
```

### 事件流

```
Cmd+Q → CGEventTap(守护线程) → 吞掉 → Queue → 主线程:
  ├─ 目标是 yiQGuard → 提示+隐藏
  └─ 目标是其他应用 → 双击/确认模式
```

---

## 开发指南

```bash
# 运行测试（可在 Linux/CI 执行）
source venv/bin/activate
pip install pytest
python -m pytest tests/ -v   # 46 passed

# 开发运行
bash build.sh --run
```

### 添加新保护模式

1. `yiqguard/modes/` 新建模块 → 实现 `handle(on_quit, ...)`
2. `config.py` 注册 → `app_delegate.py` 路由 → UI 添加选项
3. 编写测试

---

## 发布新版本

```bash
# 1. 打包 + 生成 .zip
bash release.sh

# 2. 上传到 GitHub Release
gh release create v1.1.0 release/yiQGuard-v1.1.0-macOS.zip \
  --title "v1.1.0" \
  --notes "## 下载安装
1. 下载 yiQGuard-v1.1.0-macOS.zip
2. 解压 → 拖入 /Applications
3. 右键打开 → 授权辅助功能"
```

---

## 脚本一览

| 脚本 | 用途 | 用法 |
|------|------|------|
| `build.sh` | 打包/运行 | `bash build.sh [--run\|--alias]` |
| `release.sh` | 生成发布 .zip | `bash release.sh` |
| `uninstall.sh` | 卸载 | `bash uninstall.sh` |

---

## 常见问题

<details>
<summary><strong>下载的 .app 提示"无法验证开发者"</strong></summary>

右键点击 yiQGuard.app → 选择"打开" → 点击"打开"。仅首次需要。

或终端执行：
```bash
xattr -cr /Applications/yiQGuard.app
```
</details>

<details>
<summary><strong>安装依赖失败</strong></summary>

1. 升级 pip：`pip install --upgrade pip`
2. 删除 venv 重建：`rm -rf venv && bash build.sh`
3. 清华镜像：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
</details>

<details>
<summary><strong>打包后 Launch error</strong></summary>

1. 先试 `bash build.sh --alias`
2. 如果别名正常 → `brew install libffi` → `bash build.sh`
3. 查看日志：`dist/yiQGuard.app/Contents/MacOS/yiQGuard`
</details>

<details>
<summary><strong>看不到菜单栏图标</strong></summary>

- 启动有 Toast 提示 = 程序正常，图标被刘海遮挡
- `Ctrl+Option+Q` 直接打开设置
</details>

<details>
<summary><strong>如何退出</strong></summary>

菜单 → "退出 yiQGuard" 或快捷键 `Ctrl+Option+Shift+Q`（需确认）。Cmd+Q 无法退出。
</details>

---

## 贡献

[CONTRIBUTING.md](CONTRIBUTING.md)


## License

[MIT](LICENSE)

---

<p align="center">
  <strong>yiQGuard</strong> — <a href="https://github.com/ziyifast">ziyi</a> 出品<br>
</p>
