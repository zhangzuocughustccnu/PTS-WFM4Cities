# PTS-WFM4Cities

PTS-WFM4Cities是一款面向科研的Python软件包，用于构建受数字高程模型（DEM）
思想启发的城市标量表面，并实施渐进式阈值扫描（Progressive Threshold
Scanning，PTS）。新版同时提供可复用的Python API、命令行批处理方式和中英
双语桌面界面。

[English README](README.md)

## 设计理念与功能总览

### 设计原则

1. **一个标量表面、一根阈值轴。** 任何由二维空间承载的城市属性——夜间灯光
   强度、人口密度、建筑体量——都先构造成连续表面，结果一律表达为随阈值 \(h\)
   变化的曲线，而不是一个没有上下文的数字。
2. **可复现是构造性的。** 点格局、表面、阈值序列与图件都由显式的随机种子和
   配置重新生成，任何一次运行都可以被精确重复。
3. **界面与API共用同一套实现。** 桌面窗口、命令行与库调用的是同一批函数，
   手工出图可以一键用脚本复现。
4. **外观只有一个来源。** 颜色集中在 `wfm4cities.palette`，文字集中在
   `wfm4cities.i18n`，字体集中在 `wfm4cities.fonts`；界面、导出图件与论文
   因此始终一致。

### 功能总览

| 方面 | 3.1版的提供方式 |
| --- | --- |
| 典型结构 | 论文中的四个模型 `M1`–`M4` 一键预设 |
| 自有数据 | 导入任意"二维坐标 + 一个属性"的数据表 |
| 构面 | 三次插值、凸包外最近邻填充、最小—最大值归一化至 \([0,1]\) |
| 扫描 | 有序阈值序列，判定规则可显式选择 `inclusive` 或 `strict` |
| 曲线 | 投影面积 \(A(h)\)、归一化超额体积 \(V(h)\)、连通组件数 \(N(h)\)、最大组件比率 \(L(h)\) |
| 观察 | 阈值滑块、\(x\)/\(y\) 切面、ISO/俯视/侧视视角、动画播放 |
| 图件 | 点格局、三维表面、按高度渐变填充的剖面、几何响应、\(N(h)\) 与 \(L(h)\) 面板 |
| 界面 | 中英双语（默认英文，一键切换），Times New Roman 与 SimSun/STSong 排版 |
| 自动化 | 无界面API、命令行接口、CSV与JSON导出 |

窗口按论文的六个面板排布：点格局、三维表面、连通组件数、两个剖面、几何响应
以及最大组件占比。

## 主要功能

- 检查和显示点格局；
- 一键生成四个典型结构 `M1`–`M4` 的随机点格局；
- 采用 `scipy.interpolate.griddata(method="cubic")` 完成三次插值建面；
- 以最近邻结果填充三次插值凸包以外的边界单元；
- 将分析表面按最小—最大值归一化至 \([0,1]\)；
- 在有序阈值序列上实施PTS；
- 计算投影面积 \(A(h)\)、归一化超额体积 \(V(h)\)、连通组件数 \(N(h)\)
  和最大组件比率 \(L(h)\)；
- 导出网格、完整响应轨迹、十项汇总特征和综合分析图；
- 导入任意"二维坐标 + 一个属性"的数据表，并映射到标准方形域；
- 按需安装GeoPandas/PySAL空间诊断功能。

垂向数值必须由使用者赋予明确含义，例如人口密度、活动强度或建筑体量。
软件不会自动推断变量的理论或现实含义。

## 方法边界

“漫水”只是帮助理解水平阈值逐级移动的过程类比。WFM4Cities不是水动力
洪水模型，不是通用DEM生产软件，也不是业务化规划系统；阈值顺序不表示
时间演化。实际洪涝研究还需要真实地形、降雨、排水、流路、水深和暴露度
等信息。

## 安装

支持Python 3.10—3.13，推荐使用Python 3.11。

从GitHub安装当前版本：

    git clone https://github.com/zhangzuocughustccnu/WFM4Cities.git
    cd WFM4Cities
    python -m venv .venv

激活环境：

    # Windows PowerShell
    .venv\Scripts\Activate.ps1

    # macOS/Linux
    source .venv/bin/activate

安装软件：

    python -m pip install --upgrade pip
    python -m pip install -e .

3.1版已发布，可直接安装：

    python -m pip install PTS-WFM4Cities

PyPI上的发行名为 `PTS-WFM4Cities`。历史版本2.6仍以较短的 `WFM4Cities`
为名发布，且属于另一个PyPI账号，因此 `pip install WFM4Cities` 装到的是旧的
2.6版；请始终使用 `PTS-WFM4Cities` 安装3.1版。

如需GeoPandas/PySAL空间诊断：

    python -m pip install "PTS-WFM4Cities[spatial]"

使用Conda：

    conda env create -f environment.yml
    conda activate pts-wfm4cities

Windows和macOS的标准Python通常已含Tkinter。部分Linux系统需要另行安装，
例如Debian/Ubuntu可使用 `sudo apt install python3-tk`。

## 快速使用

启动图形界面：

    wfm4cities gui

不加子命令直接运行 `wfm4cities` 也会打开界面。为兼容旧版，
安装后仍可使用 `WFM4Cities` 命令；在源码目录中也可继续使用
`python WFM4Cities.py`。

运行可重复的合成示例：

    wfm4cities demo --output-dir demo_results --seed 42

扫描已有规则网格：

    wfm4cities scan my_surface.csv --output-dir scan_results

输入文件应为不带表头的纯数值CSV矩阵。如需在 \(h=0\) 时排除零值背景，
使用严格判定：

    wfm4cities scan my_surface.csv --rule strict --output-dir scan_results

从散点数据建面：

    wfm4cities points observations.csv --grid-size 100 --method cubic

散点CSV必须含 `x` 和 `y` 两列；可选的 `value`、`density` 或
`z` 列用于提供垂向值。如果没有这些列，软件会计算指定半径内的邻点数。

## Python调用示例

    from wfm4cities import (
        SimulationConfig,
        build_surface,
        extract_features,
        progressive_threshold_scan,
    )

    config = SimulationConfig(
        num_points=150,
        noise_ratio=0.30,
        num_clusters=4,
        grid_size=100,
        seed=2026,
    )
    model = build_surface(config)
    result = progressive_threshold_scan(
        model.grid_z,
        threshold_count=51,
        threshold_min=0.0,
        threshold_max=0.95,
        rule="inclusive",
        connectivity=8,
    )
    print(extract_features(result))

四条响应轨迹可直接通过 `result.A`、`result.V`、`result.N` 和
`result.L` 读取。

## 两种阈值判定

- `inclusive`：保留 \(z \ge h\) 的单元，用于受控典型结构分析，也是默认值；
- `strict`：保留 \(z > h\) 的单元，适合在 \(h=0\) 时排除零值背景。

\(A(h)\)始终以固定分析域为分母，而不是以当前正值单元数为分母。连通组件
默认采用八邻域；也可选择四邻域。\(V(h)\)以 \(h=0\) 时总强度为分母。
精确定义见[方法约定](docs/METHOD.md)。

## 输出文件

标准批处理会生成：

- `surface_normalized.csv`：归一化规则网格；
- `pts_response.csv`：阈值及A、V、N、L完整轨迹；
- `pts_features.json`：固定十项PTS汇总特征和计算约定；
- `wfm4cities_overview.png`：点—面—阈值响应综合图；
- `source_points.csv`：在散点或合成示例中保存的源点。

## 复现与测试

    python -m pip install -e ".[dev]"
    ruff check .
    pytest
    python -m build
    python -m twine check dist/*

`pyproject.toml` 是依赖和发布元数据的唯一权威来源；
`requirements-tested.txt` 记录3.0.0候选版实际验证时的精确数值环境。

## 版本兼容

新版将原来的单文件脚本拆分为建面、PTS、输入输出、绘图、GUI和可选空间
诊断模块。导入软件包时不再自动创建窗口，也不再强制选择TkAgg后端。旧脚本
原样保存在 `legacy/` 中，仅用于版本追溯，不作为维护入口。

## 开发者

本工具包的早期单文件版本 **WFM4Cities** 由**张祚（Zuo Zhang）、江驭鲲
（Yukun Jiang）和王哲（Zhe Wang）**三人共同开发。

当前版本 **PTS-WFM4Cities**（3.0及以后）由**张祚（Zuo Zhang）**独立开发。
详见 [AUTHORS.md](AUTHORS.md)。


## 四个典型结构（M1–M4）

论文中的四种典型结构已做成一键预设。聚类数为1表示单中心，多于1表示多中心；
聚类标准差小表示集中，大表示分散。

| 预设 | 结构 |
| --- | --- |
| `M1` | 单中心–集中 |
| `M2` | 多中心–集中 |
| `M3` | 单中心–分散 |
| `M4` | 多中心–分散 |

    from wfm4cities import build_model_surface

    surface = build_model_surface("M3")      # 也可用 M1、M2、M4

这些预设是论文确定性基准面的**随机对应版本**：生成的是具备该结构特征的随机点
格局，而不是存档的基准网格本身。桌面界面中对应 *Canonical structures* 面板的
四个按钮。

## 导入自己的观测数据

任意"二维坐标 + 一个属性"的数据表都可以导入。软件会去掉外部空白边界、把范围
仿射映射到标准方形域（默认 0–100），并把所选属性归一化到 0–1——与论文中夜间
灯光数据的处理方式一致。除非显式设置 `preserve_aspect=True`，否则不保留长宽比，
且实际使用的缩放比会随结果一起报告。

在桌面界面点 *Import points*，选择 x、y 与属性列即可，状态栏会报告所用的映射。

## 界面语言与字体

桌面界面**默认英文**，点 *Language* 按钮可切换中文，所有标签、图标题与状态栏
随之切换（字符串集中在 `wfm4cities.i18n`）。

`wfm4cities.fonts` 会优先使用系统中已安装的 Times New Roman 与 SimSun/STSong；
若系统缺失（多见于 Linux），可用环境变量 `PTS_FONT_DIR` 指向字体文件所在目录。
**包内不附带任何专有字体文件。**

## 配色方案

所有颜色集中在 `wfm4cities.palette`，界面、命令行与导出图件始终一致。

## 演示、引用与许可

用于解释阈值类比的实体浸没演示见
[YouTube](https://youtu.be/tMdRVbR-JpQ)。请使用GitHub的“Cite this
repository”功能或 [CITATION.cff](CITATION.cff) 引用软件；论文发表后再将
正式DOI补入引用文件。

本项目采用[MIT许可证](LICENSE)。贡献、问题报告与安全说明分别见
[CONTRIBUTING.md](CONTRIBUTING.md)和[SECURITY.md](SECURITY.md)。
