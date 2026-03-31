# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains a Java-based desktop mascot application, likely inspired by the Shimeji project. It features a configurable animated character that moves around the screen with various actions and behaviors based on system events and user interaction.

## Architecture

The application uses a configuration-driven approach with XML files defining:
- Action definitions (`conf/動作.xml`) - specifies all possible character animations and movements
- Behavior patterns (`conf/行動.xml`) - defines how the mascot responds to different environmental conditions
- Logging configuration (`conf/logging.properties`) 

The core application is a Java executable (shimeji.jar) that loads these configurations to control character behavior.

## Key Files and Directories

- `shimeji.jar` - Main executable Java application
- `conf/` - Configuration directory containing XML files:
  - `動作.xml` - Action definitions and animation sequences
  - `行動.xml` - Behavior patterns and conditional actions
  - `logging.properties` - Logging configuration
- `img/` - Image assets directory containing sprite sheets for character animations
- `lib/` - Library dependencies (JAR files like jna.jar, examples.jar)
- `README.md` - Basic project information and author credits

## Development Setup

To work with this codebase:

1. **Java Environment**: This is a Java application requiring JDK 8 or higher
2. **Build Process**: The application is packaged as a JAR file
3. **Configuration**: Modify XML files in the conf/ directory to customize behavior
4. **Assets**: Update PNG images in the img/ directory for new sprites

## Running and Testing

To run the application:
```bash
java -jar shimeji.jar
```

## Common Tasks

1. **Customizing Character Actions**: Modify `conf/動作.xml` to add or change animations
2. **Adjusting Behavior Patterns**: Edit `conf/行動.xml` to modify how the character responds to events
3. **Adding New Sprites**: Place new PNG images in the `img/` directory and reference them in the XML files
4. **Troubleshooting**: Check `hs_err_pid*.log` files for JVM crashes

## Known Issues

- The repository contains various log files (`hs_err_pid*.log`) and temporary files that may indicate stability issues
- Several Windows executables (`.exe`) are present, suggesting this may have been developed on Windows
- Some configuration appears to be Japanese-based (XML uses Japanese tags)

## Security Considerations

- The application loads external JAR libraries from the lib/ directory
- Be cautious when modifying XML configuration files that contain embedded expressions
- The application uses Java reflection for dynamic behavior execution

---

## 项目迁移任务 (Java → Python)

### 目标
将本项目从 Java 移植到 Python 版本，同时保留原始 Java 版本不变。

### 项目结构
```
Floralgrit/
├── java-original/        # 原 Java 版本（已归档）
│   ├── shimeji.jar
│   └── lib/
├── python-version/       # 新 Python 版本
│   ├── requirements.txt
│   ├── main.py           # 入口（支持多实例 --count N）
│   ├── run.sh            # 自动环境检测启动脚本
│   ├── README.md
│   └── shimeji/
│       ├── __init__.py
│       ├── config.py       # XML 配置解析
│       ├── mascot.py       # 主 mascot 类
│       ├── manager.py      # 多实例管理器（支持分裂/繁殖）
│       ├── action.py       # 动作系统（含 IE 窗口互动）
│       ├── behavior.py     # 行为树
│       ├── animation.py    # 动画播放
│       ├── environment.py  # 环境检测（真实活跃窗口检测）
│       └── window.py       # 无边框窗口
├── conf/                 # 配置文件（共用）
│   ├── 動作.xml
│   └── 行動.xml
├── img/                  # 图片资源（共用）
└── CLAUDE.md
```

### Python 技术栈
- **GUI 框架**: `PyQt6` (推荐，支持透明窗口和无边框)
- **配置解析**: `xml.etree.ElementTree` 解析 XML
- **图像处理**: `Pillow` (PIL)

### 核心功能模块

1. **配置解析** (`config.py`): 解析 `動作.xml` 和 `行動.xml`
2. **动作系统** (`action.py`): 实现基础动作类型（静止、移动、固定、复合、选择）
   - 内置动作：跳跃、掉落、拖动、转向、抵抗、分裂
   - **IE窗口互动**：抓取窗口、携带窗口移动、投掷窗口（通过 xdotool 实现真实窗口控制）
3. **行为树** (`behavior.py`): 根据条件选择行为，管理行为频率
4. **动画播放** (`animation.py`): 按帧率播放 PNG 序列
5. **窗口管理** (`window.py`): 无边框、透明、置顶、支持鼠标拖动
6. **环境检测** (`environment.py`): 
   - 屏幕边缘检测、鼠标位置追踪
   - **真实活跃窗口检测**：使用 xdotool/xwininfo 获取当前焦点窗口位置
7. **多实例管理** (`manager.py`): 支持最多50个 mascot 实例，处理分裂/繁殖事件