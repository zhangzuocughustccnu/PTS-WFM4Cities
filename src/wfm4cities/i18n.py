"""Bilingual interface strings.

English is the default language, matching the historical desktop console.
Only interface text lives here; parameter values such as ``inclusive`` and
``strict`` are data and are never translated.
"""

from __future__ import annotations

LANGUAGES: tuple[str, ...] = ("en", "zh")
DEFAULT_LANGUAGE = "en"

STRINGS: dict[str, dict[str, str]] = {
    "window_title": {
        "en": "PTS-WFM4Cities 3.1 — Progressive Threshold Scanning (PTS)",
        "zh": "PTS-WFM4Cities 3.1 — 渐进式阈值扫描 (PTS)",
    },
    "language": {"en": "Language / 语言", "zh": "Language / 语言"},
    "panel_structures": {
        "en": "Canonical structures",
        "zh": "典型结构",
    },
    "panel_parameters": {"en": "Parameters", "zh": "参数"},
    "structure_M1": {"en": "M1\nmono·concentrated", "zh": "M1\n单中心·集中"},
    "structure_M2": {"en": "M2\npoly·concentrated", "zh": "M2\n多中心·集中"},
    "structure_M3": {"en": "M3\nmono·dispersed", "zh": "M3\n单中心·分散"},
    "structure_M4": {"en": "M4\npoly·dispersed", "zh": "M4\n多中心·分散"},
    "label_points": {"en": "Points", "zh": "点数"},
    "label_noise": {"en": "Noise ratio", "zh": "噪声比"},
    "label_clusters": {"en": "Clusters", "zh": "聚类数"},
    "label_cluster_sd": {"en": "Cluster SD", "zh": "聚类标准差"},
    "label_min_distance": {"en": "Minimum distance", "zh": "最小距离"},
    "label_grid_size": {"en": "Grid size", "zh": "网格边长"},
    "label_seed": {"en": "Random seed", "zh": "随机种子"},
    "label_threshold": {"en": "Threshold h", "zh": "阈值 h"},
    "label_rule": {"en": "Threshold rule", "zh": "判定规则"},
    "button_generate": {"en": "Generate", "zh": "生成"},
    "button_import": {"en": "Import points", "zh": "导入点数据"},
    "button_grid": {"en": "Load grid CSV", "zh": "导入网格"},
    "button_animate": {"en": "Animate", "zh": "动画"},
    "button_export": {"en": "Export results", "zh": "导出结果"},
    "disclaimer": {
        "en": "PTS is a threshold analysis,\nnot a hydrodynamic flood model.",
        "zh": "PTS 是阈值分析,\n不是水动力模型。",
    },
    "plot_points": {"en": "Point distribution", "zh": "点分布"},
    "plot_imported": {"en": "Imported surface", "zh": "导入表面"},
    "plot_surface": {"en": "3-D surface, h={h:.2f}", "zh": "三维表面, h={h:.2f}"},
    "plot_geometry": {"en": "Geometric responses", "zh": "几何响应"},
    "plot_ripley": {
        "en": "Ripley's K(r) and the CSR band",
        "zh": "Ripley K(r) 与 CSR 置信带",
    },
    "plot_histograms": {
        "en": "Coordinate histograms",
        "zh": "坐标直方图",
    },
    "plot_topology": {"en": "Topological responses", "zh": "拓扑响应"},
    "axis_threshold": {"en": "Threshold h", "zh": "阈值 h"},
    "status_ready": {"en": "Ready", "zh": "就绪"},
    "status_computing": {
        "en": "Computing surface and PTS responses…",
        "zh": "正在计算表面与 PTS 响应…",
    },
    "status_done": {
        "en": "Synthetic analysis complete",
        "zh": "合成示例分析完成",
    },
    "status_preset": {
        "en": "{label} preset generated",
        "zh": "已按 {label} 预设生成",
    },
    "status_imported": {
        "en": "Imported {n} points; extent {extent} → 0-100",
        "zh": "已导入 {n} 个点; 范围 {extent} → 0-100",
    },
    "status_aspect": {
        "en": " (aspect not kept: x{scale_x:.3g}, y{scale_y:.3g})",
        "zh": " (未保留长宽比: x{scale_x:.3g}, y{scale_y:.3g})",
    },
    "status_animating": {
        "en": "Animating threshold scan…",
        "zh": "阈值扫描动画…",
    },
    "status_anim_stop": {
        "en": "Animation stopped",
        "zh": "动画已停止",
    },
    "status_anim_done": {"en": "Animation complete", "zh": "动画完成"},
    "status_error": {"en": "Error", "zh": "错误"},
    "status_loaded": {"en": "Loaded {path}", "zh": "已读入 {path}"},
    "status_saved": {"en": "Saved {path}", "zh": "已保存 {path}"},
    "status_import_failed": {"en": "Import failed", "zh": "导入失败"},
    "dialog_import_title": {
        "en": "Select a point table (CSV)",
        "zh": "选择点数据 CSV",
    },
    "dialog_grid_title": {
        "en": "Select a headerless numeric grid CSV",
        "zh": "选择无表头的数值网格 CSV",
    },
    "dialog_columns_title": {
        "en": "Select columns",
        "zh": "选择列",
    },
    "dialog_col_x": {"en": "x (horizontal)", "zh": "x (横坐标)"},
    "dialog_col_y": {"en": "y (vertical)", "zh": "y (纵坐标)"},
    "dialog_col_value": {"en": "Z attribute", "zh": "Z 属性列"},
    "error_need_value_column": {
        "en": "Select the column that holds the vertical attribute.",
        "zh": "请选择存放垂向属性的列。",
    },
    "error_too_few_columns": {
        "en": "The file needs at least an x and a y column.",
        "zh": "文件至少需要 x 和 y 两列。",
    },
    "dialog_save_title": {
        "en": "Save PTS response CSV",
        "zh": "保存 PTS 响应 CSV",
    },
}


def normalise(language: str | None) -> str:
    """Return a supported language code, falling back to the default."""

    code = (language or "").strip().lower()[:2]
    return code if code in LANGUAGES else DEFAULT_LANGUAGE


def translate(key: str, language: str = DEFAULT_LANGUAGE, **fields: object) -> str:
    """Return the string for ``key`` in ``language``, formatted if needed."""

    entry = STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(normalise(language), entry[DEFAULT_LANGUAGE])
    return text.format(**fields) if fields else text
