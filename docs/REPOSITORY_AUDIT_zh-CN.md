# 现有仓库与2.6发布包快速审计

*Chinese-language working note, kept for provenance: a dated snapshot of the
repository as it stood before version 3.0. The maintained documentation is in
English.*

审计日期：2026-08-08。

## 已核实的现状

- 用户上传的 `WFM4Cities.py` 与GitHub仓库同名文件SHA-256完全一致；
- GitHub `main` 分支当前仅有 `WFM4Cities.py` 和
  `water-flooding model.py` 两个脚本；
- PyPI已有 `WFM4Cities 2.6`，发布日期为2025-01-22；
- 2.6发布包采用MIT许可证，作者列为张祚、江驭鲲、王哲；
- 2.6元数据中的项目主页仍是中文占位地址；
- 2.6分发版本号为2.6，但包内 `__version__` 为2.0；
- 原脚本在模块导入阶段创建多个Tk根窗口、强制TkAgg后端，并启动主循环；
- GUI、计算、绘图、随机生成和全局状态位于同一文件，难以无界面复现和测试；
- 原始运行依赖被逐一精确锁定，且PySAL以大型聚合包作为必装依赖。

## 3.0.0中的处理

- 项目主页、仓库、问题跟踪和更新日志地址改为真实URL；
- 版本号统一为3.0.0；
- 采用现代 `pyproject.toml` 和 `src/` 布局；
- 数值模块不再依赖GUI全局变量；
- GUI和Tk后端按需加载；
- GeoPandas、Shapely、libpysal和esda移入可选 `spatial` 依赖；
- 原始脚本以相同SHA-256保存在 `legacy/`；
- 新增README、许可证、引用文件、环境文件、测试、CI和PyPI发布流程；
- 构建wheel和source distribution并进行独立安装验证。

该审计用于说明软件工程迁移，不代替论文的方法验证或真实城市数据复核。
