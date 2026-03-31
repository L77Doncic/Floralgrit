# Shimeji Python Version

Python移植版本的Shimeji桌面宠物，基于PyQt6实现。

## 功能特性

- 透明无边框置顶窗口
- 完整的XML配置解析（支持原版`動作.xml`和`行動.xml`）
- 动作系统（静止、移动、固定、复合、选择）
- 行为树与条件判断
- 动画帧序列播放
- 环境感知（屏幕边缘、鼠标位置）
- 鼠标拖动交互
- 活跃窗口检测与互动（爬窗口、推窗口，跨平台支持）

## 安装依赖

```bash
pip install -r requirements.txt
```

### 系统依赖

#### Linux 桌面环境

**窗口检测功能依赖 X11 环境，Wayland 不完全支持**

如果在Linux桌面环境运行，需要安装以下依赖：

```bash
# Ubuntu/Debian
sudo apt-get install -y libxcb-cursor0 libxkbcommon-x11-0 libxcb-xinerama0

# 如果缺少显示依赖
sudo apt-get install -y libgl1 libfontconfig1

# 窗口互动功能需要以下工具（可选，用于爬窗口、推窗口等功能）
sudo apt-get install -y xdotool x11-utils xprop xwininfo
```

**注意**：窗口检测功能需要 X11 显示服务器，Wayland 环境可能无法正常工作。

#### Windows

Windows 系统通常无需额外安装系统依赖，PyQt6 的 pip 包已包含所需库。

系统要求：
- Windows 10 或更高版本（64位）
- 已安装 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)（通常系统已自带）

**窗口互动功能**：Windows 通过 Win32 API 原生支持窗口互动（爬窗口、推窗口等），无需额外配置。

#### macOS

macOS 系统通常无需额外安装系统依赖。

系统要求：
- macOS 10.15 (Catalina) 或更高版本
- 同时支持 Intel 和 Apple Silicon (M1/M2/M3) 架构

```bash
# 如果使用 Homebrew 安装的 Python
brew install python
```

**窗口互动功能**：macOS 通过 AppleScript 支持窗口互动功能。首次使用时可能需要在 **系统设置 > 隐私与安全 > 辅助功能** 中授予终端应用程序权限。

## 运行方式

### 快速启动（推荐）

#### Linux

```bash
# 自动检测环境并运行
./run.sh

# 或者指定多个实例
python main.py --count 3
```

#### Windows

```cmd
# 方法1：双击运行 run.bat
run.bat

# 方法2：使用 PowerShell（推荐，有彩色输出）
.\run.ps1

# 方法3：直接运行
python main.py
```

**注意**：PowerShell 执行策略可能阻止脚本运行，如遇问题可运行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### macOS

```bash
# 自动检测环境并运行
./run_mac.sh

# 或者直接运行
python3 main.py
```

### 桌面环境（笔记本/台式机）

在各桌面环境直接运行：

```bash
# Linux / macOS
python3 main.py

# Windows
python main.py
```

### 无头服务器（Headless Server）

**仅 Linux 支持无头模式**。

在无显示环境的服务器上，需要使用虚拟显示：

```bash
# 安装虚拟显示
sudo apt-get install -y xvfb

# 使用虚拟显示运行
xvfb-run python main.py

# 或者手动启动虚拟显示
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
python main.py
```

**注意**：虚拟显示下无法看到实际的mascot形象，但程序逻辑会正常运行。建议在有真实显示器的环境中使用。

**Windows/macOS 无头模式**：这两个系统不支持无头模式运行图形应用，必须在有图形界面的环境中运行。

### 命令行选项

```bash
python main.py --help
# 用法: main.py [-h] [--count N] [--xvfb]
#
# 可选参数:
#   -h, --help     显示帮助信息
#   --count N, -n N  mascot 实例数量 (默认: 1, 最大: 50)
#   --xvfb         强制使用虚拟显示
```

---

## 个性化定制

### 修改图片资源

如果你想用自己的图片替换默认的吉祥物形象，请按以下步骤操作：

#### 1. 准备图片素材

- **格式**：PNG（支持透明背景）
- **尺寸建议**：128x128 像素（也可自定义，程序会自动适应）
- **命名规范**：使用 `shime1.png` ~ `shime46.png` 的命名方式
- **透明背景**：建议使用透明背景，mascot 才能正确显示在桌面上

#### 2. 图片用途说明

| 文件名 | 用途说明 |
|--------|---------|
| `shime1.png` ~ `shime5.png` | 基础动作：站立、行走、跑步、猛冲 |
| `shime6.png` ~ `shime10.png` | 抵抗动作（被拖动时的挣扎） |
| `shime11.png` | 坐姿基础帧 |
| `shime12.png` ~ `shime14.png` | 爬墙动作序列 |
| `shime15.png` ~ `shime17.png` | 转头动作中间帧 |
| `shime18.png` ~ `shime22.png` | 跳跃、摔倒、天花板悬挂 |
| `shime23.png` ~ `shime25.png` | 天花板移动动作 |
| `shime26.png` ~ `shime29.png` | 坐下转头动作序列 |
| `shime30.png` ~ `shime33.png` | 放松坐姿、晃脚动作 |
| `shime34.png` ~ `shime37.png` | 携带窗口行走、投掷 |
| `shime38.png` ~ `shime46.png` | 分裂、拔出、特殊动作 |

> **提示**：动画是帧序列组成的，例如行走动作会循环播放 `shime1.png` → `shime2.png` → `shime1.png` → `shime3.png`

#### 3. 替换步骤

```bash
# 备份原图片（可选）
cp img/ img_backup/

# 将你的PNG图片放入 img/ 目录
# 确保文件名格式为 shime1.png, shime2.png, ...

# 运行查看效果
python main.py
```

#### 4. 验证替换成功

替换图片后，运行程序检查：

```bash
# 检查图片文件是否存在
ls img/shime1.png

# 运行程序查看效果
python main.py

# 如果 mascot 显示为空白或报错，检查：
# 1. 图片是否为有效的 PNG 格式
# 2. 文件名是否正确（区分大小写）
# 3. 图片是否在 img/ 目录下
```

#### 5. 高级：修改动作配置

如果需要调整动画帧序列或添加新动作，可以编辑 `conf/動作.xml`：

```xml
<動作 名前="立つ" 種類="静止" 枠="地面">
    <アニメーション>
        <ポーズ 画像="/shime1.png" 基準座標="64,128" 移動速度="0,0" 長さ="250" />
    </アニメーション>
</動作>
```

| 属性 | 说明 | 示例 |
|------|------|------|
| `画像` | 图片路径（相对于 img/ 目录） | `/shime1.png` |
| `基準座標` | 锚点位置（x,y），影响 mascot 在屏幕上的位置 | `64,128` 表示图片中心偏下 |
| `移動速度` | 播放该帧时的位移（vx, vy）像素/帧 | `0,0` 静止，`-2,0` 向左移动 |
| `長さ` | 该帧持续时间（tick数，约1/60秒） | `250` 约4秒，`6` 约0.1秒 |

### 修改行为模式

编辑 `conf/行動.xml` 可调整 mascot 的行为频率和条件：

```xml
<行動 名前="立ってボーっとする" 頻度="200" />
<!-- 頻度数值越大，该行为被选中的概率越高 -->
```

### 故障排除

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| mascot 显示为空白方块 | 图片路径错误或格式不支持 | 检查图片是否为 PNG 格式，文件名是否正确 |
| mascot 位置偏移 | 基準座標设置不当 | 调整 XML 中的基準座標值 |
| 动画闪烁或跳帧 | 图片尺寸不一致 | 确保所有帧图片尺寸相同 |
| 程序启动报错 | XML 格式错误 | 检查 XML 标签是否正确闭合，属性值是否加引号 |
| 行为不生效 | 条件表达式错误 | 查看终端输出，检查条件语法 |

## 项目结构

```
python-version/
├── main.py              # 入口文件
├── requirements.txt     # 依赖列表
├── README.md           # 本文件
├── run.sh              # Linux 自动环境检测启动脚本
├── run.bat             # Windows CMD 启动脚本
├── run.ps1             # Windows PowerShell 启动脚本（推荐）
├── run_mac.sh          # macOS 启动脚本
├── conf/               # 配置文件目录（独立）
│   ├── 動作.xml
│   ├── 行動.xml
│   ├── Mascot.xsd
│   └── logging.properties
├── img/                # 图片资源目录（独立，46张PNG）
└── shimeji/            # 核心包
    ├── __init__.py
    ├── config.py       # XML配置解析
    ├── mascot.py       # 主控制器
    ├── manager.py      # 多实例管理器
    ├── action.py       # 动作执行系统
    ├── behavior.py     # 行为树管理
    ├── animation.py    # 动画播放器
    ├── environment.py  # 环境感知（含窗口检测）
    ├── window.py       # 无边框窗口
    └── window_control.py # 跨平台窗口控制（Win/macOS/Linux）
```

## 与原版Java版本对比

| 特性 | Java原版 | Python版本 |
|------|----------|------------|
| 桌面宠物 | ✅ | ✅ |
| XML配置 | ✅ | ✅ |
| 多动作类型 | ✅ | ✅ |
| 行为树 | ✅ | ✅ |
| 条件判断 | ✅ | 基础支持 |
| 窗口互动 | ✅ | ✅ (跨平台：Linux xdotool、Windows Win32 API、macOS AppleScript) |
| IE/活跃窗口互动 | ✅ | ✅ (跨平台检测真实窗口) |
| 多实例管理 | ✅ | ✅ (最多50个) |
| 分裂/繁殖 | ✅ | ✅ |

## 安全注意事项

### 窗口控制功能（IE互动）

**默认禁用**。 mascot 与真实窗口的互动功能（抓取、移动、投掷窗口）默认处于关闭状态。

如需启用，请设置环境变量：
```bash
export SHIMEJI_ALLOW_WINDOW_CONTROL=1
python main.py
```

**风险提示**：
- 启用后 mascot 可以移动其他应用程序窗口
- 请确保只运行来自可信来源的 XML 配置文件
- 不要在生产服务器上启用此功能

### 条件表达式安全

本项目使用安全的表达式解析器（替代了原版的 `eval()`），只允许以下操作：
- 数学运算（+、-、*、/、%、**）
- 比较运算（==、!=、<、<=、>、>=）
- 逻辑运算（and、or、not）
- 白名单函数（abs、max、min、round 等）

## 注意事项

1. **Python版本拥有独立的资源目录**：`img/` 和 `conf/` 已复制到本目录下，不依赖外部文件
2. **Linux窗口检测**需要X11环境，Wayland可能不完全支持

## 常见问题

### Q: 程序启动后看不到mascot？
A: 检查是否在无头服务器上运行，需要虚拟显示或有真实桌面环境。

### Q: 鼠标拖动不工作？
A: 确保PyQt6正确安装，且系统支持X11。

### Q: 如何添加更多mascot实例？
A: 右键点击mascot，选择"Add Another"（功能待完善）。

---

## 致谢与版权

**作者**：w糖果w，叫我糖果就好

**图片素材**：截图自《RE：从零开始休息时间》，部分图片为作者自行拼接制作

**原桌宠**：东方栀子桌宠 —— 感谢原作者

### 使用注意事项

1. **二次转载**：可以二次转载，转载请注明作者【w糖果w】
2. **商用**：请联系作者，贴吧ID @晴空中的糖果雨，QQ 3466762660
3. **修改改良**：可以修改及改良，改造后请注明原作者【w糖果w】

以上，感谢使用！
