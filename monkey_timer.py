"""MonkeyTimer V0.2: a Windows floating presentation countdown timer."""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import ttk

from countdown import CountdownTimer


TRANSPARENT_COLOR = "#ff00ff"
DEFAULT_FONT_SIZE = 72
MIN_FONT_SIZE = 28
MAX_FONT_SIZE = 180


class MonkeyTimerApp:
    """Tkinter user interface around the tested countdown core."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.timer = CountdownTimer()
        self.presenter_mode = False
        self.drag_offset: tuple[int, int] | None = None
        self.toolbar_hide_job: str | None = None
        self.font_size = tk.IntVar(value=DEFAULT_FONT_SIZE)
        self.always_on_top = tk.BooleanVar(value=True)

        self.root.title("MonkeyTimer V0.2")
        self.root.resizable(False, False)
        self._build_widgets()
        self._bind_shortcuts()
        self._set_topmost()
        self._refresh_display()

    def _build_widgets(self) -> None:
        self.normal_frame = ttk.Frame(self.root, padding=20)
        self.normal_frame.grid()
        self.normal_display = ttk.Label(
            self.normal_frame, text="00:00", font=("Segoe UI", 36, "bold")
        )
        self.normal_display.grid(row=0, column=0, columnspan=4, pady=(0, 16))

        ttk.Label(self.normal_frame, text="分钟").grid(row=1, column=0, sticky="e")
        self.minutes = ttk.Entry(self.normal_frame, width=6, justify="center")
        self.minutes.insert(0, "5")
        self.minutes.grid(row=1, column=1, padx=(4, 12))
        ttk.Label(self.normal_frame, text="秒").grid(row=1, column=2, sticky="e")
        self.seconds = ttk.Entry(self.normal_frame, width=6, justify="center")
        self.seconds.insert(0, "0")
        self.seconds.grid(row=1, column=3, padx=(4, 0))

        buttons = ttk.Frame(self.normal_frame)
        buttons.grid(row=2, column=0, columnspan=4, pady=16)
        ttk.Button(buttons, text="开始", command=self.start).grid(row=0, column=0, padx=3)
        ttk.Button(buttons, text="暂停", command=self.pause).grid(row=0, column=1, padx=3)
        ttk.Button(buttons, text="继续", command=self.resume).grid(row=0, column=2, padx=3)
        ttk.Button(buttons, text="重置", command=self.reset).grid(row=0, column=3, padx=3)

        options = ttk.Frame(self.normal_frame)
        options.grid(row=3, column=0, columnspan=4, pady=(0, 10))
        ttk.Button(options, text="进入演讲模式", command=self.enter_presenter_mode).grid(
            row=0, column=0, padx=(0, 10)
        )
        ttk.Label(options, text="字体").grid(row=0, column=1)
        self.font_size_box = ttk.Spinbox(
            options, from_=MIN_FONT_SIZE, to=MAX_FONT_SIZE, increment=2,
            width=5, justify="center", textvariable=self.font_size,
            command=self._update_presenter_font,
        )
        self.font_size_box.grid(row=0, column=2, padx=(4, 10))
        ttk.Label(options, text="px").grid(row=0, column=3)
        ttk.Checkbutton(
            options, text="窗口置顶", variable=self.always_on_top,
            command=self._set_topmost,
        ).grid(row=0, column=4, padx=(12, 0))
        self.status = ttk.Label(self.normal_frame, text="请输入时间后点击开始。")
        self.status.grid(row=4, column=0, columnspan=4)

        self.presenter_frame = tk.Frame(self.root, bg=TRANSPARENT_COLOR)
        self.presenter_frame.bind("<Enter>", self._show_toolbar)
        self.presenter_frame.bind("<Leave>", self._schedule_toolbar_hide)
        self.presenter_display = tk.Frame(self.presenter_frame, bg=TRANSPARENT_COLOR)
        self.presenter_display.grid(row=0, column=0, padx=10, pady=8)
        self.shadow_display = tk.Label(
            self.presenter_display, text="00:00",
            font=("Segoe UI", DEFAULT_FONT_SIZE, "bold"), fg="#111111", bg=TRANSPARENT_COLOR,
        )
        self.shadow_display.place(x=3, y=3)
        self.presenter_number = tk.Label(
            self.presenter_display, text="00:00",
            font=("Segoe UI", DEFAULT_FONT_SIZE, "bold"), fg="white", bg=TRANSPARENT_COLOR,
        )
        self.presenter_number.place(x=0, y=0)
        for widget in (self.presenter_display, self.shadow_display, self.presenter_number):
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._drag_window)
            widget.bind("<ButtonRelease-1>", self._stop_drag)
            widget.bind("<Enter>", self._show_toolbar)

        self.presenter_toolbar = tk.Frame(self.presenter_frame, bg="#1f2937", padx=5, pady=4)
        tk.Button(self.presenter_toolbar, text="暂停/继续", command=self._toggle_pause, bd=0, padx=6).grid(row=0, column=0, padx=2)
        tk.Button(self.presenter_toolbar, text="重置", command=self.reset, bd=0, padx=6).grid(row=0, column=1, padx=2)
        tk.Button(self.presenter_toolbar, text="−", command=lambda: self._change_font_size(-2), bd=0).grid(row=0, column=2, padx=2)
        tk.Button(self.presenter_toolbar, text="+", command=lambda: self._change_font_size(2), bd=0).grid(row=0, column=3, padx=2)
        tk.Button(self.presenter_toolbar, text="退出", command=self.exit_presenter_mode, bd=0, padx=6).grid(row=0, column=4, padx=2)
        self.presenter_toolbar.bind("<Enter>", self._show_toolbar)
        self.presenter_toolbar.bind("<Leave>", self._schedule_toolbar_hide)

    def _bind_shortcuts(self) -> None:
        self.root.bind("<F11>", lambda _event: self._toggle_presenter_mode())
        self.root.bind("<space>", lambda _event: self._toggle_pause())
        self.root.bind("<r>", lambda _event: self.reset())
        self.root.bind("<plus>", lambda _event: self._change_font_size(2))
        self.root.bind("<minus>", lambda _event: self._change_font_size(-2))
        self.root.bind("<Escape>", lambda _event: self.exit_presenter_mode())

    def start(self) -> None:
        try:
            self.timer.start(self._read_duration())
        except ValueError as error:
            self.status.config(text=str(error))
            return
        self.status.config(text="倒计时进行中。")
        self._show_remaining()

    def pause(self) -> None:
        self.timer.pause()
        if self.timer.is_paused:
            self.status.config(text="已暂停。")

    def resume(self) -> None:
        self.timer.resume()
        if self.timer.is_running:
            self.status.config(text="倒计时进行中。")

    def reset(self) -> None:
        self.timer.reset()
        self.status.config(text="已重置。")
        self._show_remaining()

    def enter_presenter_mode(self) -> None:
        if self.presenter_mode:
            return
        self.presenter_mode = True
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.configure(bg=TRANSPARENT_COLOR)
        self.normal_frame.grid_remove()
        self.presenter_frame.grid()
        self._configure_windows_transparency()
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self._update_presenter_font()
        self._resize_presenter_window()

    def exit_presenter_mode(self) -> None:
        if not self.presenter_mode:
            return
        self.presenter_mode = False
        self._cancel_toolbar_hide()
        self.presenter_toolbar.grid_remove()
        self.root.withdraw()
        self._clear_windows_transparency()
        self.presenter_frame.grid_remove()
        self.root.overrideredirect(False)
        self.root.configure(bg="SystemButtonFace")
        self.normal_frame.grid()
        self.root.deiconify()
        self._set_topmost()

    def _toggle_presenter_mode(self) -> None:
        if self.presenter_mode:
            self.exit_presenter_mode()
        else:
            self.enter_presenter_mode()

    def _configure_windows_transparency(self) -> None:
        """Use Tk's Windows-only color key; other systems keep an opaque fallback."""
        if sys.platform == "win32":
            self.root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)

    def _clear_windows_transparency(self) -> None:
        if sys.platform == "win32":
            self.root.wm_attributes("-transparentcolor", "")

    def _set_topmost(self) -> None:
        self.root.attributes("-topmost", self.always_on_top.get())

    def _toggle_pause(self) -> None:
        if self.timer.is_running:
            self.pause()
        else:
            self.resume()

    def _change_font_size(self, difference: int) -> None:
        try:
            current = int(self.font_size.get())
        except tk.TclError:
            current = DEFAULT_FONT_SIZE
        self.font_size.set(max(MIN_FONT_SIZE, min(MAX_FONT_SIZE, current + difference)))
        self._update_presenter_font()

    def _update_presenter_font(self) -> None:
        try:
            size = int(self.font_size.get())
        except tk.TclError:
            size = DEFAULT_FONT_SIZE
        size = max(MIN_FONT_SIZE, min(MAX_FONT_SIZE, size))
        self.font_size.set(size)
        font = ("Segoe UI", size, "bold")
        self.presenter_number.config(font=font)
        self.shadow_display.config(font=font)
        if self.presenter_mode:
            self._resize_presenter_window()

    def _resize_presenter_window(self) -> None:
        self.presenter_frame.update_idletasks()
        # ``place`` does not contribute to its parent's requested geometry, so
        # size the borderless window from the number label itself.
        width = self.presenter_number.winfo_reqwidth() + 26
        height = self.presenter_number.winfo_reqheight() + 22
        if self.presenter_toolbar.winfo_ismapped():
            height += self.presenter_toolbar.winfo_reqheight() + 10
        self.root.geometry(f"{width}x{height}+{self.root.winfo_x()}+{self.root.winfo_y()}")

    def _show_toolbar(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        if not self.presenter_mode:
            return
        self._cancel_toolbar_hide()
        if not self.presenter_toolbar.winfo_ismapped():
            self.presenter_toolbar.grid(row=1, column=0, pady=(0, 6))
            self._resize_presenter_window()

    def _schedule_toolbar_hide(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        if self.presenter_mode:
            self._cancel_toolbar_hide()
            self.toolbar_hide_job = self.root.after(900, self._hide_toolbar)

    def _hide_toolbar(self) -> None:
        self.toolbar_hide_job = None
        if self.presenter_mode:
            self.presenter_toolbar.grid_remove()
            self._resize_presenter_window()

    def _cancel_toolbar_hide(self) -> None:
        if self.toolbar_hide_job is not None:
            self.root.after_cancel(self.toolbar_hide_job)
            self.toolbar_hide_job = None

    def _start_drag(self, event: tk.Event[tk.Misc]) -> None:
        self.drag_offset = (event.x_root - self.root.winfo_x(), event.y_root - self.root.winfo_y())

    def _drag_window(self, event: tk.Event[tk.Misc]) -> None:
        if self.drag_offset is not None:
            self.root.geometry(f"+{event.x_root - self.drag_offset[0]}+{event.y_root - self.drag_offset[1]}")

    def _stop_drag(self, _event: tk.Event[tk.Misc]) -> None:
        self.drag_offset = None

    def _read_duration(self) -> int:
        minutes_text = self.minutes.get().strip()
        seconds_text = self.seconds.get().strip()
        if not minutes_text.isdigit() or not seconds_text.isdigit():
            raise ValueError("分钟和秒必须是非负整数。")
        minutes, seconds = int(minutes_text), int(seconds_text)
        if seconds >= 60:
            raise ValueError("秒必须在 0 到 59 之间。")
        total = minutes * 60 + seconds
        if total == 0:
            raise ValueError("倒计时时间必须大于 0。")
        return total

    def _refresh_display(self) -> None:
        self._show_remaining()
        self.root.after(100, self._refresh_display)

    def _show_remaining(self) -> None:
        remaining = self.timer.display_seconds()
        minutes, seconds = divmod(remaining, 60)
        text = f"{minutes:02d}:{seconds:02d}"
        self.normal_display.config(text=text)
        self.presenter_number.config(text=text)
        self.shadow_display.config(text=text)
        if remaining == 0 and not self.timer.is_paused and self.timer.has_duration:
            self.status.config(text="时间到，倒计时已停止。")


def main() -> None:
    root = tk.Tk()
    MonkeyTimerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
