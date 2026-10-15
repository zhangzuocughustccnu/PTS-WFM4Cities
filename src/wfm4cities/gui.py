"""Tk desktop interface for PTS-WFM4Cities.

Progressive threshold scanning (PTS) on DEM-inspired urban scalar surfaces.

Tkinter and the Tk Matplotlib backend are imported only inside :func:`run_gui`
so that importing the package stays safe on headless systems.  The interface
language defaults to English and can be switched to Chinese from the *Language*
button; every label, panel title and status message follows it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    import tkinter as tk

#: Structure buttons, in the order of the two dimensions of the design.
STRUCTURE_KEYS = ("M1", "M2", "M3", "M4")

#: Width of the moving average used to smooth the topological curves *for
#: display only*.  Exported values are never smoothed.
SMOOTH_WINDOW = 5


def smooth_for_display(values, window: int = SMOOTH_WINDOW):
    """Return a moving average of ``values`` for plotting, edges preserved."""

    import numpy as np

    array = np.asarray(values, dtype=float)
    if window < 3 or array.size < window:
        return array
    pad = window // 2
    padded = np.pad(array, pad, mode="edge")
    kernel = np.ones(window, dtype=float) / window
    smoothed = np.convolve(padded, kernel, mode="valid")
    # Keep the two anchors exact so the displayed curve starts and ends on the
    # measured values even though the interior is smoothed.
    smoothed[0] = array[0]
    smoothed[-1] = array[-1]
    return smoothed


def ripley_envelope(points, radii, *, repeats: int = 20, seed: int = 20261014):
    """Return the CSR mean and 95% pointwise envelope of Ripley's K.

    The envelope comes from complete-spatial-randomness simulations over the
    same bounding box, which is the reference band drawn in the manuscript.
    """

    import numpy as np

    from .core import ripley_k

    coords = np.asarray(points, dtype=float)
    if coords.shape[0] < 4:
        raise ValueError("at least four observations are required")
    low = coords.min(axis=0)
    high = coords.max(axis=0)
    area = float((high[0] - low[0]) * (high[1] - low[1]))
    if area <= 0.0:
        raise ValueError("the observations must span a non-degenerate extent")
    generator = np.random.default_rng(seed)
    curves = []
    for _ in range(repeats):
        sample = np.column_stack(
            (
                generator.uniform(low[0], high[0], coords.shape[0]),
                generator.uniform(low[1], high[1], coords.shape[0]),
            )
        )
        curves.append(ripley_k(sample, radii, area=area))
    stack = np.asarray(curves, dtype=float)
    return (
        np.asarray(ripley_k(coords, radii, area=area), dtype=float),
        stack.mean(axis=0),
        np.percentile(stack, 2.5, axis=0),
        np.percentile(stack, 97.5, axis=0),
    )


def run_gui() -> None:
    """Launch the PTS-WFM4Cities graphical interface."""

    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk

        import numpy as np
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.colors import LightSource
        from matplotlib.figure import Figure
    except ImportError as exc:
        raise ImportError(
            "the GUI requires Tkinter and Matplotlib's Tk backend; on Debian/Ubuntu "
            "install python3-tk"
        ) from exc

    from . import fonts, i18n, palette
    from .core import (
        MODEL_LABELS,
        SimulationConfig,
        build_surface,
        interpolate_surface,
        model_config,
        standardize_points,
        surface_from_grid,
    )
    from .io import (
        list_csv_columns,
        read_point_table,
        read_surface_csv,
        write_scan_csv,
        write_surface_csv,
    )
    from .pts import progressive_threshold_scan

    fonts.apply()

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        raise RuntimeError(
            "no graphical display is available; use 'wfm4cities demo' or "
            "'wfm4cities scan' for headless analysis"
        ) from exc

    class PTSApplication:
        """Single-window console for the four canonical structures and PTS."""

        def __init__(self, window: tk.Tk) -> None:
            self.root = window
            self.language = i18n.DEFAULT_LANGUAGE
            self.model = None
            self.result = None
            self.imported_points = None
            self.animation_job = None
            self.animation_levels = np.linspace(0.0, 0.95, 20)
            self.animation_index = 0
            self._text_widgets: list[tuple[object, str]] = []
            self._frames: list[tuple[object, str]] = []
            self._status: tuple[str, dict] = ("status_ready", {})
            self._curves: tuple | None = None
            self._curves_key: tuple | None = None

            self.variables = {
                "num_points": tk.IntVar(value=150),
                "noise_ratio": tk.DoubleVar(value=0.15),
                "num_clusters": tk.IntVar(value=1),
                "cluster_std": tk.DoubleVar(value=0.55),
                "min_distance": tk.DoubleVar(value=0.0),
                "grid_size": tk.IntVar(value=100),
                "seed": tk.IntVar(value=42),
                "slice_x": tk.DoubleVar(value=50.0),
                "slice_y": tk.DoubleVar(value=50.0),
                "view": tk.StringVar(value="ISO"),
                "threshold": tk.DoubleVar(value=0.40),
                "rule": tk.StringVar(value="inclusive"),
            }
            self.status = tk.StringVar(value="")
            self._build_layout(ttk, Figure, FigureCanvasTkAgg)
            self.retranslate()
            self.generate()

        # ------------------------------------------------------------------
        # language handling
        # ------------------------------------------------------------------
        def t(self, key: str, **fields: object) -> str:
            return i18n.translate(key, self.language, **fields)

        def toggle_language(self) -> None:
            self.language = "zh" if self.language == "en" else "en"
            self.retranslate()

        def retranslate(self) -> None:
            """Apply the current language to every widget and panel title."""

            self.root.title(self.t("window_title"))
            for widget, key in self._text_widgets:
                widget.configure(text=self.t(key))
            for frame, key in self._frames:
                frame.configure(text=self.t(key))
            self.language_button.configure(
                text="Language: English"
                if self.language == "en"
                else "\u8bed\u8a00: \u4e2d\u6587"
            )
            key, fields = self._status
            self.status.set(self.t(key, **fields))
            if self.model is not None:
                self.draw()

        def set_status(self, key: str, **fields: object) -> None:
            self._status = (key, fields)
            self.status.set(self.t(key, **fields))

        # ------------------------------------------------------------------
        # layout helpers
        # ------------------------------------------------------------------
        def _label(self, parent, key: str, **kwargs):
            widget = self._ttk.Label(parent, **kwargs)
            self._text_widgets.append((widget, key))
            return widget

        def _button(self, parent, key: str, command, **kwargs):
            widget = self._ttk.Button(parent, command=command, **kwargs)
            self._text_widgets.append((widget, key))
            return widget

        def _frame(self, parent, key: str, **kwargs):
            widget = self._ttk.LabelFrame(parent, **kwargs)
            self._frames.append((widget, key))
            return widget

        def _build_layout(self, ttk_module, figure_class, canvas_class) -> None:
            self._ttk = ttk_module
            self._tk = tk
            self._messagebox = messagebox
            self._filedialog = filedialog
            self._palette = palette

            container = ttk_module.Frame(self.root, padding=8)
            container.pack(fill="both", expand=True)
            container.columnconfigure(1, weight=1)
            container.rowconfigure(0, weight=1)

            side = ttk_module.Frame(container)
            side.grid(row=0, column=0, sticky="ns", padx=(0, 8))

            self.language_button = ttk_module.Button(
                side, command=self.toggle_language, width=22
            )
            self.language_button.pack(fill="x", pady=(0, 6))

            structures = self._frame(side, "panel_structures", padding=8)
            structures.pack(fill="x")
            self.structure_buttons = {}
            for index, key in enumerate(STRUCTURE_KEYS):
                button = self._button(
                    structures,
                    f"structure_{key}",
                    lambda k=key: self.apply_structure(k),
                    width=17,
                )
                button.grid(
                    row=index // 2, column=index % 2, padx=3, pady=3, sticky="ew"
                )
                self.structure_buttons[key] = button
            structures.columnconfigure(0, weight=1)
            structures.columnconfigure(1, weight=1)

            controls = self._frame(side, "panel_parameters", padding=8)
            controls.pack(fill="x", pady=(8, 0))
            rows = (
                ("label_points", "num_points"),
                ("label_noise", "noise_ratio"),
                ("label_clusters", "num_clusters"),
                ("label_cluster_sd", "cluster_std"),
                ("label_min_distance", "min_distance"),
                ("label_grid_size", "grid_size"),
                ("label_seed", "seed"),
            )
            for row_index, (key, variable) in enumerate(rows):
                self._label(controls, key).grid(
                    row=row_index, column=0, sticky="w", pady=2
                )
                ttk_module.Entry(
                    controls, textvariable=self.variables[variable], width=10
                ).grid(row=row_index, column=1, sticky="ew", pady=2)
            controls.columnconfigure(1, weight=1)

            base = len(rows)
            ttk_module.Separator(controls).grid(
                row=base, column=0, columnspan=2, sticky="ew", pady=7
            )
            self._label(controls, "label_threshold").grid(
                row=base + 1, column=0, sticky="w"
            )
            ttk_module.Label(
                controls, textvariable=self.variables["threshold"], width=6
            ).grid(row=base + 1, column=1, sticky="e")
            ttk_module.Scale(
                controls,
                from_=0.0,
                to=0.95,
                variable=self.variables["threshold"],
                command=lambda _value: self.draw(),
            ).grid(row=base + 2, column=0, columnspan=2, sticky="ew", pady=3)

            for offset, (key, variable) in enumerate(
                (("label_slice_x", "slice_x"), ("label_slice_y", "slice_y"))
            ):
                self._label(controls, key).grid(
                    row=base + 17 + offset * 2, column=0, columnspan=2, sticky="w"
                )
                self._tk.Scale(
                    controls,
                    from_=0.0,
                    to=100.0,
                    orient="horizontal",
                    variable=self.variables[variable],
                    command=lambda _value: self.draw(),
                ).grid(
                    row=base + 18 + offset * 2,
                    column=0,
                    columnspan=2,
                    sticky="ew",
                    pady=1,
                )
            self._label(controls, "label_view").grid(
                row=base + 21, column=0, sticky="w", pady=2
            )
            view_box = self._ttk.Combobox(
                controls,
                textvariable=self.variables["view"],
                values=("ISO", "Top", "Side"),
                state="readonly",
                width=10,
            )
            view_box.grid(row=base + 21, column=1, sticky="ew", pady=2)
            view_box.bind("<<ComboboxSelected>>", lambda _event: self.draw())

            self._label(controls, "label_rule").grid(
                row=base + 3, column=0, sticky="w", pady=2
            )
            rule_box = ttk_module.Combobox(
                controls,
                textvariable=self.variables["rule"],
                values=("inclusive", "strict"),
                state="readonly",
                width=10,
            )
            rule_box.grid(row=base + 3, column=1, sticky="ew", pady=2)
            rule_box.bind("<<ComboboxSelected>>", self._rule_changed)

            actions = (
                ("button_generate", self.generate),
                ("button_import", self.import_points),
                ("button_grid", self.load_grid),
                ("button_animate", self.animate),
                ("button_export", self.export),
            )
            for offset, (key, command) in enumerate(actions):
                self._button(controls, key, command).grid(
                    row=base + 4 + offset, column=0, columnspan=2, sticky="ew", pady=2
                )

            self._label(
                controls,
                "disclaimer",
                foreground="#555555",
                wraplength=230,
                justify="left",
            ).grid(row=base + 9, column=0, columnspan=2, sticky="w", pady=(10, 2))

            figure_frame = ttk_module.Frame(container)
            figure_frame.grid(row=0, column=1, sticky="nsew")
            self.figure = figure_class(
                figsize=(11.6, 7.9),
                constrained_layout={
                    "w_pad": 0.14,
                    "h_pad": 0.10,
                    "wspace": 0.015,
                    "hspace": 0.025,
                },
            )
            self.canvas = canvas_class(self.figure, master=figure_frame)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)

            status_bar = ttk_module.Label(
                container, textvariable=self.status, relief="sunken", anchor="w"
            )
            status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(7, 0))

        # ------------------------------------------------------------------
        # actions
        # ------------------------------------------------------------------
        def structure_curves(self):
            """Mean N(h) and L(h) of the four structures with 10--90% bands.

            Mirrors panel c1/c2 of Figure 3 of the accompanying study: the four
            canonical structures are generated as their stochastic presets, each
            repeated with different seeds, and the bands summarise the spread.
            """

            key_now = (
                int(self.variables["grid_size"].get()),
                str(self.variables["rule"].get()),
            )
            if self._curves is not None and self._curves_key == key_now:
                return self._curves
            self.set_status("status_structures")
            self.root.update_idletasks()
            thresholds = np.linspace(0.0, 0.90, 41)
            curves: dict[str, dict[str, tuple]] = {"N": {}, "L": {}}
            for name in STRUCTURE_KEYS:
                counts: list = []
                shares: list = []
                for repeat in range(8):
                    settings = model_config(
                        name, seed=1000 + 37 * repeat, grid_size=key_now[0]
                    )
                    model = build_surface(settings)
                    result = progressive_threshold_scan(
                        model.grid_z, thresholds, rule=key_now[1]
                    )
                    counts.append(np.asarray(result.component_count, dtype=float))
                    shares.append(
                        np.asarray(result.largest_component_ratio, dtype=float)
                    )
                for label, stack in (("N", counts), ("L", shares)):
                    values = np.asarray(stack)
                    curves[label][name] = (
                        values.mean(axis=0),
                        np.percentile(values, 5, axis=0),
                        np.percentile(values, 95, axis=0),
                    )
            self._curves = (thresholds, curves)
            self._curves_key = key_now
            return self._curves

        def apply_structure(self, key: str) -> None:
            """Load the preset of a canonical structure and redraw."""

            settings = model_config(key)
            self.variables["num_points"].set(settings.num_points)
            self.variables["num_clusters"].set(settings.num_clusters)
            self.variables["grid_size"].set(settings.grid_size)
            self.variables["seed"].set(settings.seed)
            self.variables["noise_ratio"].set(float(settings.noise_ratio))
            self.variables["cluster_std"].set(float(settings.cluster_std))
            self.variables["min_distance"].set(float(settings.min_distance))
            self.imported_points = None
            self._curves = None
            self.generate()
            self.set_status("status_preset", label=MODEL_LABELS[key])

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
                self.set_status("status_computing")
                self.root.update_idletasks()
                self.model = build_surface(settings)
                self.imported_points = None
                self._curves = None
                self._scan()
                self.draw()
                self.set_status("status_done")
            except Exception as exc:
                self._messagebox.showerror(self.t("window_title"), str(exc))
                self.set_status("status_error")

        def _choose_columns(self, columns: list[str]):
            dialog = self._ttk.Toplevel(self.root)
            dialog.title(self.t("dialog_columns_title"))
            dialog.transient(self.root)
            dialog.grab_set()
            ttk = self._ttk
            choices = {}
            for row, (key, role, default) in enumerate(
                (
                    ("dialog_col_x", "x", columns[0]),
                    (
                        "dialog_col_y",
                        "y",
                        columns[1] if len(columns) > 1 else columns[0],
                    ),
                    ("dialog_col_value", "value", ""),
                )
            ):
                ttk.Label(dialog, text=self.t(key)).grid(
                    row=row, column=0, sticky="w", padx=8, pady=5
                )
                var = tk.StringVar(value=default)
                ttk.Combobox(
                    dialog,
                    textvariable=var,
                    values=["", *columns],
                    state="readonly",
                    width=22,
                ).grid(row=row, column=1, padx=8, pady=5)
                choices[role] = var
            result: dict[str, str] = {}

            def confirm() -> None:
                result.update({role: var.get() for role, var in choices.items()})
                dialog.destroy()

            ttk.Button(dialog, text="OK", command=confirm).grid(
                row=3, column=0, columnspan=2, pady=8
            )
            self.root.wait_window(dialog)
            if not result.get("x") or not result.get("y"):
                return None
            return result["x"], result["y"], (result.get("value") or None)

        def import_points(self) -> None:
            path = self._filedialog.askopenfilename(
                title=self.t("dialog_import_title"),
                filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
            )
            if not path:
                return
            try:
                columns = list_csv_columns(path)
            except Exception as exc:
                self._messagebox.showerror(self.t("window_title"), str(exc))
                return
            if len(columns) < 2:
                self._messagebox.showerror(
                    self.t("window_title"), self.t("error_too_few_columns")
                )
                return
            chosen = self._choose_columns(columns)
            if chosen is None:
                return
            x_col, y_col, value_col = chosen
            if value_col is None:
                self._messagebox.showerror(
                    self.t("window_title"), self.t("error_need_value_column")
                )
                return
            try:
                points, values = read_point_table(path, x_col, y_col, value_col)
                assert values is not None
                mapped, normalised, report = standardize_points(points, values)
                _x, _y, grid_z = interpolate_surface(
                    mapped,
                    normalised,
                    grid_size=int(self.variables["grid_size"].get()),
                    domain_min=0.0,
                    domain_max=100.0,
                    method="cubic",
                    fill_boundaries=True,
                    normalize=True,
                )
                self.model = surface_from_grid(
                    grid_z, domain_min=0.0, domain_max=100.0, normalize=False
                )
                self.imported_points = mapped
                self._scan()
                self.draw()
                self.set_status(
                    "status_imported",
                    n=len(mapped),
                    extent=tuple(round(v, 3) for v in report.source_extent),
                )
                if report.scale_x != report.scale_y:
                    self.status.set(
                        self.status.get()
                        + self.t(
                            "status_aspect",
                            scale_x=report.scale_x,
                            scale_y=report.scale_y,
                        )
                    )
            except Exception as exc:
                self._messagebox.showerror(self.t("window_title"), str(exc))
                self.set_status("status_import_failed")

        def load_grid(self) -> None:
            path = self._filedialog.askopenfilename(
                title=self.t("dialog_grid_title"),
                filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
            )
            if not path:
                return
            try:
                self.model = surface_from_grid(read_surface_csv(path), normalize=True)
                self.imported_points = None
                self._scan()
                self.draw()
                self.set_status("status_loaded", path=path)
            except Exception as exc:
                self._messagebox.showerror(self.t("window_title"), str(exc))

        # ------------------------------------------------------------------
        # drawing
        # ------------------------------------------------------------------
        def _style(self, axis) -> None:
            axis.set_facecolor(palette.PANEL_FACE)
            axis.grid(True, color=palette.GRID_GRAY, linewidth=0.5, alpha=0.9)
            axis.tick_params(pad=1.5, length=2.0)
            for spine in axis.spines.values():
                spine.set_color(palette.SPINE_GRAY)

        def draw(self) -> None:
            if self.model is None or self.result is None:
                return
            threshold = float(self.variables["threshold"].get())
            self.figure.clear()
            # Layout: the three-dimensional surface and the geometric
            # responses are the main panels (two columns each); the point
            # pattern, Ripley's K, the topological responses and the histograms
            # are the smaller statistics panels beside them.
            # Layout after the author's sketch: two rows of three columns.
            # Row 1: point pattern | three-dimensional surface | Ripley's K.
            # Row 2: the two vertical sections stacked | geometric responses |
            # topological responses.  Columns are equal so the panels align.
            grid = self.figure.add_gridspec(
                2,
                3,
                width_ratios=(1.0, 1.5, 1.0),
                height_ratios=(1.0, 1.0),
                wspace=0.02,
                hspace=0.03,
            )

            # ---- point pattern (or the imported surface) --------------------
            map_ax = self.figure.add_subplot(grid[0, 0])
            if len(self.model.points):
                map_ax.set_facecolor(palette.DOMAIN_FILL)
                map_ax.scatter(
                    self.model.points[:, 0],
                    self.model.points[:, 1],
                    s=17,
                    color=palette.POINT_COLOR,
                    edgecolors="white",
                    linewidths=0.3,
                )
                if len(self.model.centers):
                    map_ax.scatter(
                        self.model.centers[:, 0],
                        self.model.centers[:, 1],
                        s=85,
                        marker="*",
                        color=palette.CENTER_COLOR,
                        edgecolors="white",
                        linewidths=0.7,
                        zorder=3,
                    )
                map_ax.set_title(self.t("plot_points"))
            else:
                map_ax.pcolormesh(
                    self.model.grid_x,
                    self.model.grid_y,
                    self.model.grid_z,
                    shading="auto",
                    cmap=palette.surface_cmap(),
                )
                map_ax.set_title(self.t("plot_imported"))
            if self.imported_points is not None:
                map_ax.scatter(
                    self.imported_points[:, 0],
                    self.imported_points[:, 1],
                    s=7,
                    color=palette.POINT_COLOR,
                    alpha=0.8,
                    linewidths=0,
                )
            map_ax.set_aspect("equal", adjustable="box")
            map_ax.set_xlabel("x")
            map_ax.set_ylabel("y")
            self._style(map_ax)

            # ---- three-dimensional surface ---------------------------------
            surface_ax = self.figure.add_subplot(grid[0, 1], projection="3d")
            light = LightSource(azdeg=315, altdeg=42)
            relief = light.shade(
                self.model.grid_z,
                cmap=palette.surface_cmap(),
                vert_exag=1.8,
                blend_mode="soft",
            )
            surface_ax.plot_surface(
                self.model.grid_x,
                self.model.grid_y,
                self.model.grid_z,
                facecolors=relief,
                rstride=1,
                cstride=1,
                linewidth=0,
                antialiased=True,
                shade=False,
            )
            surface_ax.plot_surface(
                self.model.grid_x,
                self.model.grid_y,
                np.full_like(self.model.grid_z, threshold),
                color=palette.WATER_COLOR,
                alpha=0.32,
                linewidth=0,
            )
            surface_ax.set_zlim(0, 1)
            view = str(self.variables["view"].get())
            if view == "Top":
                surface_ax.view_init(elev=78, azim=-90)
            elif view == "Side":
                surface_ax.view_init(elev=4, azim=-90)
            else:
                surface_ax.view_init(elev=34, azim=-60)
            surface_ax.set_box_aspect((1.0, 1.0, 0.62), zoom=1.22)
            x0, x1 = float(self.model.grid_x.min()), float(self.model.grid_x.max())
            y0, y1 = float(self.model.grid_y.min()), float(self.model.grid_y.max())
            surface_ax.set_xticks(np.linspace(x0, x1, 11))
            surface_ax.set_yticks(np.linspace(y0, y1, 11))
            surface_ax.set_zticks(np.linspace(0.0, 1.0, 6))
            for axis in (surface_ax.xaxis, surface_ax.yaxis, surface_ax.zaxis):
                axis.set_pane_color((0.975, 0.975, 0.975, 1.0))
                axis._axinfo["grid"].update(
                    {
                        "linewidth": 0.35,
                        "color": (0.86, 0.86, 0.86, 1.0),
                        "linestyle": "-",
                    }
                )
            surface_ax.tick_params(labelsize=7, colors=palette.SPINE_GRAY)
            surface_ax.set_title(self.t("plot_surface", h=threshold))

            # ---- N(h) of the four structures (Figure 3c1) ------------------
            thresholds, curves = self.structure_curves()
            count_ax = self.figure.add_subplot(grid[0, 2])
            for index, name in enumerate(STRUCTURE_KEYS):
                mean, low, high = curves["N"][name]
                colour = palette.series_color(index)
                count_ax.fill_between(
                    thresholds, low, high, color=colour, alpha=0.15, linewidth=0
                )
                count_ax.plot(
                    thresholds,
                    mean,
                    color=colour,
                    linewidth=1.5,
                    marker=palette.series_marker(index),
                    markersize=2.6,
                    markevery=4,
                    label=name,
                )
            count_ax.set_title(self.t("plot_ripley"))
            count_ax.set_xlabel(self.t("axis_threshold"))
            count_ax.set_ylabel("N(h)")
            count_ax.legend(frameon=False, fontsize=6.5, ncols=2)
            self._style(count_ax)

            # ---- geometric responses ---------------------------------------
            geometry_ax = self.figure.add_subplot(grid[1, 1])
            geometry_ax.plot(
                self.result.thresholds,
                self.result.area,
                color=palette.GEOMETRY_A_COLOR,
                marker="o",
                markersize=3.5,
                markerfacecolor="white",
                markeredgewidth=0.6,
                markevery=8,
                linewidth=1.9,
                label="A(h)",
            )
            geometry_ax.plot(
                self.result.thresholds,
                self.result.excess_volume,
                color=palette.GEOMETRY_V_COLOR,
                marker="s",
                markersize=3.3,
                markerfacecolor="white",
                markeredgewidth=0.6,
                markevery=8,
                linewidth=1.9,
                label="V(h)",
            )
            geometry_ax.axvline(
                threshold, color=palette.SPINE_GRAY, linestyle="--", linewidth=0.9
            )
            geometry_ax.set_ylim(0, 1.02)
            geometry_ax.set_title(self.t("plot_geometry"))
            geometry_ax.set_xlabel(self.t("axis_threshold"))
            geometry_ax.legend(frameon=False, fontsize=8)
            self._style(geometry_ax)

            # ---- L(h) of the four structures (Figure 3c2) ------------------
            share_ax = self.figure.add_subplot(grid[1, 2])
            for index, name in enumerate(STRUCTURE_KEYS):
                mean, low, high = curves["L"][name]
                colour = palette.series_color(index)
                share_ax.fill_between(
                    thresholds, low, high, color=colour, alpha=0.15, linewidth=0
                )
                share_ax.plot(
                    thresholds,
                    mean,
                    color=colour,
                    linewidth=1.5,
                    marker=palette.series_marker(index),
                    markersize=2.6,
                    markevery=4,
                    label=name,
                )
            share_ax.set_ylim(0.0, 1.02)
            share_ax.set_title(self.t("plot_topology"))
            share_ax.set_xlabel(self.t("axis_threshold"))
            share_ax.set_ylabel("L(h)")
            share_ax.legend(frameon=False, fontsize=6.5, ncols=2, loc="lower right")
            self._style(share_ax)

            # ---- vertical sections, coloured by height ---------------------
            from matplotlib.collections import LineCollection

            section_grid = grid[1, 0].subgridspec(2, 1, hspace=0.06)
            axis_z = np.asarray(self.model.grid_z)
            xs = np.asarray(self.model.grid_x[0, :])
            ys = np.asarray(self.model.grid_y[:, 0])
            column = int(
                np.clip(
                    round(
                        float(self.variables["slice_x"].get())
                        / 100.0
                        * (axis_z.shape[1] - 1)
                    ),
                    0,
                    axis_z.shape[1] - 1,
                )
            )
            row = int(
                np.clip(
                    round(
                        float(self.variables["slice_y"].get())
                        / 100.0
                        * (axis_z.shape[0] - 1)
                    ),
                    0,
                    axis_z.shape[0] - 1,
                )
            )
            cmap = palette.surface_cmap()

            def draw_section(ax, horizontal, profile, title):
                points = np.column_stack((horizontal, profile))
                segments = np.stack((points[:-1], points[1:]), axis=1)
                colours = cmap(0.5 * (profile[:-1] + profile[1:]))
                ax.add_collection(
                    LineCollection(segments, colors=colours, linewidths=2.0)
                )
                ax.fill_between(
                    horizontal,
                    profile,
                    threshold,
                    where=profile > threshold,
                    color=palette.WATER_COLOR,
                    alpha=0.30,
                    linewidth=0,
                )
                ax.axhline(
                    threshold, color=palette.SPINE_GRAY, linestyle="--", linewidth=0.9
                )
                ax.set_xlim(float(horizontal.min()), float(horizontal.max()))
                ax.set_ylim(-0.02, 1.02)
                ax.set_title(title, fontsize=7)
                ax.tick_params(labelsize=6)
                self._style(ax)

            section_x = self.figure.add_subplot(section_grid[0])
            draw_section(
                section_x,
                ys,
                axis_z[:, column],
                f"{self.t('plot_section_x')} = {xs[column]:.2f}",
            )
            section_x.set_ylabel("z", fontsize=7)
            section_y = self.figure.add_subplot(section_grid[1])
            draw_section(
                section_y,
                xs,
                axis_z[row, :],
                f"{self.t('plot_section_y')} = {ys[row]:.2f}",
            )
            section_y.set_xlabel("x", fontsize=7)
            section_y.set_ylabel("z", fontsize=7)

            self.canvas.draw_idle()

        def animate(self) -> None:
            if self.animation_job is not None:
                self.root.after_cancel(self.animation_job)
                self.animation_job = None
                self.set_status("status_anim_stop")
                return
            self.animation_index = 0
            self.set_status("status_animating")
            self._advance_animation()

        def _advance_animation(self) -> None:
            if self.animation_index >= len(self.animation_levels):
                self.animation_job = None
                self.set_status("status_anim_done")
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
            path = self._filedialog.asksaveasfilename(
                title=self.t("dialog_save_title"),
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
                self.set_status("status_saved", path=path)
            except Exception as exc:
                self._messagebox.showerror(self.t("window_title"), str(exc))

    PTSApplication(root)
    root.mainloop()
