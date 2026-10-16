"""MonkeyTimer: a simple Windows presentation countdown timer."""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import ttk

from countdown import CountdownTimer


class MonkeyTimerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.timer = CountdownTimer()
        self.root.title("MonkeyTimer V0.1")
        self.root.resizable(False, False)
        self.presentation_window: tk.Toplevel | None = None
        self.presentation_display: tk.Label | None = None
        self._build_widgets()
        self._refresh_display()

    def _build_widgets(self) -> None:
        frame = ttk.Frame(self.root, padding=20)
        frame.grid()

        self.display = ttk.Label(frame, text="00:00", font=("Segoe UI", 36, "bold"))
        self.display.grid(row=0, column=0, columnspan=4, pady=(0, 16))

        ttk.Label(frame, text="分钟").grid(row=1, column=0, sticky="e")
        self.minutes = ttk.Entry(frame, width=6, justify="center")
        self.minutes.insert(0, "5")
        self.minutes.grid(row=1, column=1, padx=(4, 12))
        ttk.Label(frame, text="秒").grid(row=1, column=2, sticky="e")
        self.seconds = ttk.Entry(frame, width=6, justify="center")
        self.seconds.insert(0, "0")
        self.seconds.grid(row=1, column=3, padx=(4, 0))

        buttons = ttk.Frame(frame)
        buttons.grid(row=2, column=0, columnspan=4, pady=16)
        ttk.Button(buttons, text="开始", command=self.start).grid(row=0, column=0, padx=3)
        ttk.Button(buttons, text="暂停", command=self.pause).grid(row=0, column=1, padx=3)
        ttk.Button(buttons, text="继续", command=self.resume).grid(row=0, column=2, padx=3)
        ttk.Button(buttons, text="重置", command=self.reset).grid(row=0, column=3, padx=3)

        ttk.Button(frame, text="演讲模式", command=self.open_presentation_mode).grid(
            row=3, column=0, columnspan=4
        )

        self.status = ttk.Label(frame, text="请输入时间后点击开始。")
        self.status.grid(row=4, column=0, columnspan=4, pady=(8, 0))

    def open_presentation_mode(self) -> None:
        """Open the smallest reliable presentation view before adding transparency."""
        if self.presentation_window is not None and self.presentation_window.winfo_exists():
            self.presentation_window.deiconify()
            self.presentation_window.lift()
            return

        window = tk.Toplevel(self.root)
        window.title("MonkeyTimer 演讲模式")
        window.geometry("600x260+120+120")
        window.minsize(600, 260)
        window.overrideredirect(True)
        window.configure(background="black")
        window.protocol("WM_DELETE_WINDOW", self.close_presentation_mode)
        window.bind("<Escape>", lambda _event: self.close_presentation_mode())

        display = tk.Label(
            window,
            background="black",
            foreground="white",
            font=("Segoe UI", 120, "bold"),
            text=self._formatted_remaining(),
        )
        display.pack(expand=True, fill="both", padx=20, pady=20)

        self.presentation_window = window
        self.presentation_display = display
        window.update_idletasks()
        self._enable_presentation_transparency(window)
        window.deiconify()
        window.attributes("-topmost", True)
        window.lift()

    @staticmethod
    def _enable_presentation_transparency(window: tk.Toplevel) -> None:
        """Make only the black presentation background transparent on Windows."""
        if sys.platform != "win32":
            return
        try:
            window.attributes("-transparentcolor", "black")
        except tk.TclError:
            # Keep the proven black-background presentation window as a fallback.
            pass

    def close_presentation_mode(self) -> None:
        if self.presentation_window is not None and self.presentation_window.winfo_exists():
            self.presentation_window.destroy()
        self.presentation_window = None
        self.presentation_display = None

    def start(self) -> None:
        try:
            total_seconds = self._read_duration()
            self.timer.start(total_seconds)
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

    def _read_duration(self) -> int:
        minutes_text = self.minutes.get().strip()
        seconds_text = self.seconds.get().strip()
        if not minutes_text.isdigit() or not seconds_text.isdigit():
            raise ValueError("分钟和秒必须是非负整数。")
        minutes = int(minutes_text)
        seconds = int(seconds_text)
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
        formatted_remaining = self._format_seconds(remaining)
        self.display.config(text=formatted_remaining)
        if self.presentation_display is not None and self.presentation_display.winfo_exists():
            self.presentation_display.config(text=formatted_remaining)
        if remaining == 0 and not self.timer.is_paused and self.timer.has_duration:
            self.status.config(text="时间到，倒计时已停止。")

    def _formatted_remaining(self) -> str:
        remaining = self.timer.display_seconds()
        return self._format_seconds(remaining)

    @staticmethod
    def _format_seconds(remaining: int) -> str:
        minutes, seconds = divmod(remaining, 60)
        return f"{minutes:02d}:{seconds:02d}"


def main() -> None:
    root = tk.Tk()
    MonkeyTimerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
