"""Tk desktop interface.

Tkinter and the Tk Matplotlib backend are imported only inside ``run_gui`` so
that importing WFM4Cities remains safe on headless systems.
"""

from __future__ import annotations


def run_gui() -> None:
    """Launch the WFM4Cities graphical interface."""

    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk

        import numpy as np
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure
    except ImportError as exc:
        raise ImportError(
            "the GUI requires Tkinter and Matplotlib's Tk backend; on Debian/Ubuntu "
            "install python3-tk"
        ) from exc

    from .core import SimulationConfig, build_surface, surface_from_grid
    from .io import read_surface_csv, write_scan_csv, write_surface_csv
    from .pts import progressive_threshold_scan

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        raise RuntimeError(
            "no graphical display is available; use 'wfm4cities demo' or "
            "'wfm4cities scan' for headless analysis"
        ) from exc

    class WFMApplication:
        def __init__(self, window: tk.Tk) -> None:
            self.root = window
            self.root.title("WFM4Cities 3.0 — Progressive Threshold Scanning")
            self.root.geometry("1240x800")
            self.root.minsize(980, 650)
            self.model = None
            self.result = None
            self.animation_job = None
            self.animation_levels = np.linspace(0.0, 0.95, 20)
            self.animation_index = 0

            self.variables = {
                "num_points": tk.IntVar(value=100),
                "noise_ratio": tk.DoubleVar(value=0.50),
                "num_clusters": tk.IntVar(value=3),
                "cluster_std": tk.DoubleVar(value=1.0),
                "min_distance": tk.DoubleVar(value=1.0),
                "grid_size": tk.IntVar(value=100),
                "seed": tk.IntVar(value=42),
                "threshold": tk.DoubleVar(value=0.40),
                "rule": tk.StringVar(value="inclusive"),
            }
            self.status = tk.StringVar(value="Ready / 就绪")
            self._build_layout(ttk, Figure, FigureCanvasTkAgg)
            self.generate()

        def _build_layout(self, ttk_module, figure_class, canvas_class) -> None:
            container = ttk_module.Frame(self.root, padding=8)
            container.pack(fill="both", expand=True)
            container.columnconfigure(1, weight=1)
            container.rowconfigure(0, weight=1)

            controls = ttk_module.LabelFrame(
                container, text="Parameters / 参数", padding=10
            )
            controls.grid(row=0, column=0, sticky="ns", padx=(0, 8))

            rows = (
                ("Points / 点数", "num_points"),
                ("Noise ratio / 噪声比", "noise_ratio"),
                ("Clusters / 聚类数", "num_clusters"),
                ("Cluster SD / 聚类标准差", "cluster_std"),
                ("Minimum distance / 最小距离", "min_distance"),
                ("Grid size / 网格边长", "grid_size"),
                ("Random seed / 随机种子", "seed"),
            )
            for row_index, (label, key) in enumerate(rows):
                ttk_module.Label(controls, text=label).grid(
                    row=row_index, column=0, sticky="w", pady=3
                )
                ttk_module.Entry(
                    controls, textvariable=self.variables[key], width=12
                ).grid(row=row_index, column=1, sticky="ew", pady=3)

            ttk_module.Separator(controls).grid(
                row=7, column=0, columnspan=2, sticky="ew", pady=8
            )
            ttk_module.Label(controls, text="Threshold h / 阈值").grid(
                row=8, column=0, sticky="w"
            )
            ttk_module.Label(
                controls, textvariable=self.variables["threshold"], width=6
            ).grid(row=8, column=1, sticky="e")
            threshold_scale = ttk_module.Scale(
                controls,
                from_=0.0,
                to=0.95,
                variable=self.variables["threshold"],
                command=lambda _value: self.draw(),
            )
            threshold_scale.grid(row=9, column=0, columnspan=2, sticky="ew", pady=4)

            ttk_module.Label(controls, text="Threshold rule / 判定").grid(
                row=10, column=0, sticky="w", pady=3
            )
            rule_box = ttk_module.Combobox(
                controls,
                textvariable=self.variables["rule"],
                values=("inclusive", "strict"),
                state="readonly",
                width=10,
            )
            rule_box.grid(row=10, column=1, sticky="ew", pady=3)
            rule_box.bind("<<ComboboxSelected>>", self._rule_changed)

            ttk_module.Button(
                controls, text="Generate / 生成", command=self.generate
            ).grid(row=11, column=0, columnspan=2, sticky="ew", pady=(10, 3))
            ttk_module.Button(
                controls, text="Load grid CSV / 导入网格", command=self.load_grid
            ).grid(row=12, column=0, columnspan=2, sticky="ew", pady=3)
            ttk_module.Button(
                controls, text="Animate / 动画", command=self.animate
            ).grid(row=13, column=0, columnspan=2, sticky="ew", pady=3)
            ttk_module.Button(
                controls, text="Export results / 导出", command=self.export
            ).grid(row=14, column=0, columnspan=2, sticky="ew", pady=3)
            ttk_module.Label(
                controls,
                text=(
                    "PTS is a threshold analysis,\nnot a hydrodynamic flood model.\n"
                    "PTS是阈值分析, 不是水动力模型。"
                ),
                foreground="#555555",
                wraplength=210,
                justify="left",
            ).grid(row=15, column=0, columnspan=2, sticky="w", pady=(14, 4))

            figure_frame = ttk_module.Frame(container)
            figure_frame.grid(row=0, column=1, sticky="nsew")
            self.figure = figure_class(figsize=(10, 7), constrained_layout=True)
            self.canvas = canvas_class(self.figure, master=figure_frame)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)

            status_bar = ttk_module.Label(
                container, textvariable=self.status, relief="sunken", anchor="w"
            )
            status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(7, 0))

        def _scan(self) -> None:
            self.result = progressive_threshold_scan(
                self.model.grid_z,
                threshold_count=51,
                threshold_min=0.0,
                threshold_max=0.95,
                rule=self.variables["rule"].get(),
                connectivity=8,
            )

        def _rule_changed(self, _event=None) -> None:
            if self.model is not None:
                self._scan()
                self.draw()

        def generate(self) -> None:
            try:
                settings = SimulationConfig(
                    num_points=self.variables["num_points"].get(),
                    noise_ratio=self.variables["noise_ratio"].get(),
                    num_clusters=self.variables["num_clusters"].get(),
                    cluster_std=self.variables["cluster_std"].get(),
                    min_distance=self.variables["min_distance"].get(),
                    grid_size=self.variables["grid_size"].get(),
                    seed=self.variables["seed"].get(),
                )
                self.status.set("Computing surface and PTS responses… / 正在计算…")
                self.root.update_idletasks()
                self.model = build_surface(settings)
                self._scan()
                self.draw()
                self.status.set("Synthetic analysis complete / 合成示例分析完成")
            except Exception as exc:
                messagebox.showerror("WFM4Cities", str(exc))
                self.status.set("Error / 错误")

        def load_grid(self) -> None:
            path = filedialog.askopenfilename(
                title="Select a headerless numeric grid CSV",
                filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
            )
            if not path:
                return
            try:
                self.model = surface_from_grid(read_surface_csv(path), normalize=True)
                self._scan()
                self.draw()
                self.status.set(f"Loaded {path}")
            except Exception as exc:
                messagebox.showerror("WFM4Cities", str(exc))

        def draw(self) -> None:
            if self.model is None or self.result is None:
                return
            threshold = float(self.variables["threshold"].get())
            self.figure.clear()

            map_ax = self.figure.add_subplot(221)
            if len(self.model.points):
                map_ax.scatter(
                    self.model.points[:, 0],
                    self.model.points[:, 1],
                    c=self.model.point_values,
                    cmap="viridis",
                    s=16,
                )
                map_ax.set_title("Point distribution / 点分布")
            else:
                map_ax.pcolormesh(
                    self.model.grid_x,
                    self.model.grid_y,
                    self.model.grid_z,
                    shading="auto",
                    cmap="viridis",
                )
                map_ax.set_title("Input grid / 输入网格")
            map_ax.set_aspect("equal", adjustable="box")
            map_ax.set_xlabel("x")
            map_ax.set_ylabel("y")

            surface_ax = self.figure.add_subplot(222, projection="3d")
            surface_ax.plot_surface(
                self.model.grid_x,
                self.model.grid_y,
                self.model.grid_z,
                cmap="viridis",
                linewidth=0,
                alpha=0.94,
            )
            surface_ax.plot_surface(
                self.model.grid_x,
                self.model.grid_y,
                np.full_like(self.model.grid_z, threshold),
                color="#77aadd",
                alpha=0.35,
                linewidth=0,
            )
            surface_ax.set_zlim(0, 1)
            surface_ax.set_title(f"3-D surface, h={threshold:.2f} / 三维表面")

            geometry_ax = self.figure.add_subplot(223)
            geometry_ax.plot(
                self.result.thresholds, self.result.area, label="A(h)", linewidth=2
            )
            geometry_ax.plot(
                self.result.thresholds,
                self.result.excess_volume,
                label="V(h)",
                linewidth=2,
            )
            geometry_ax.axvline(threshold, color="0.5", linestyle="--")
            geometry_ax.set_ylim(0, 1.02)
            geometry_ax.set_title("Geometric responses / 几何响应")
            geometry_ax.set_xlabel("Threshold h / 阈值")
            geometry_ax.legend(frameon=False)

            topology_ax = self.figure.add_subplot(224)
            topology_ax.plot(
                self.result.thresholds,
                self.result.component_count,
                color="#aa4466",
                label="N(h)",
                linewidth=2,
            )
            topology_ax.set_ylabel("N(h)", color="#aa4466")
            topology_ax.tick_params(axis="y", labelcolor="#aa4466")
            topology_ax.axvline(threshold, color="0.5", linestyle="--")
            dominance_ax = topology_ax.twinx()
            dominance_ax.plot(
                self.result.thresholds,
                self.result.largest_component_ratio,
                color="#4477aa",
                label="L(h)",
                linewidth=2,
            )
            dominance_ax.set_ylim(0, 1.02)
            dominance_ax.set_ylabel("L(h)", color="#4477aa")
            dominance_ax.tick_params(axis="y", labelcolor="#4477aa")
            topology_ax.set_title("Topological responses / 拓扑响应")
            topology_ax.set_xlabel("Threshold h / 阈值")
            self.canvas.draw_idle()

        def animate(self) -> None:
            if self.animation_job is not None:
                self.root.after_cancel(self.animation_job)
                self.animation_job = None
                self.status.set("Animation stopped / 动画已停止")
                return
            self.animation_index = 0
            self.status.set("Animating threshold scan… / 阈值扫描动画…")
            self._advance_animation()

        def _advance_animation(self) -> None:
            if self.animation_index >= len(self.animation_levels):
                self.animation_job = None
                self.status.set("Animation complete / 动画完成")
                return
            self.variables["threshold"].set(
                float(self.animation_levels[self.animation_index])
            )
            self.draw()
            self.animation_index += 1
            self.animation_job = self.root.after(180, self._advance_animation)

        def export(self) -> None:
            if self.model is None or self.result is None:
                return
            path = filedialog.asksaveasfilename(
                title="Save PTS response CSV",
                defaultextension=".csv",
                initialfile="pts_response.csv",
                filetypes=(("CSV files", "*.csv"),),
            )
            if not path:
                return
            try:
                write_scan_csv(path, self.result)
                surface_path = str(path).rsplit(".", 1)[0] + "_surface.csv"
                write_surface_csv(surface_path, self.model)
                self.status.set(f"Saved {path} and {surface_path}")
            except Exception as exc:
                messagebox.showerror("WFM4Cities", str(exc))

    WFMApplication(root)
    root.mainloop()
