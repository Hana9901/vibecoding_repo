# Tetris（俄罗斯方块）

一个用 **Python + pygame** 编写的俄罗斯方块小程序。

## 运行环境

- Python 3.10+（推荐 3.12）
- Windows / macOS / Linux

## 本地运行（推荐使用 venv）

在项目根目录（有 `main.py` 的目录）执行：

```bash
python -m venv venv
```

Windows PowerShell 激活：

```powershell
.\venv\Scripts\Activate.ps1
```

安装依赖：

```bash
pip install -r requirements.txt
```

启动游戏：

```bash
python main.py
```

## 操作

- ← / →：左右移动
- ↑：旋转
- ↓：加速下落（soft drop）
- 空格：一键直落（hard drop）
- R：重新开始
- ESC：退出
