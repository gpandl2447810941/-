#!/usr/bin/env python3
"""
UAECS SOP Installer
Creates desktop shortcut and installs web files.
"""

import os
import sys
import shutil
import platform
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

APP_NAME = "UAECS SOP"
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"


def get_default_install_dir():
    if IS_WINDOWS:
        return str(Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))) / "Programs" / APP_NAME)
    elif IS_MAC:
        return str(Path.home() / "Applications" / APP_NAME)
    else:
        return str(Path.home() / APP_NAME)


def create_shortcut(install_dir):
    """Create desktop shortcut that opens index.html"""
    index_path = Path(install_dir) / "index.html"
    desktop = Path.home() / "Desktop"

    if IS_WINDOWS:
        # Create .url file (Windows Internet Shortcut)
        url_path = desktop / f"{APP_NAME}.url"
        url_content = f"[InternetShortcut]\nURL=file:///{str(index_path).replace(chr(92), '/')}\nIconFile={index_path}\nIconIndex=0\n"
        with open(url_path, "w", encoding="utf-8") as f:
            f.write(url_content)
        return url_path

    elif IS_MAC:
        # Create .webloc file (macOS)
        webloc_path = desktop / f"{APP_NAME}.webloc"
        plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>URL</key>
    <string>file://{index_path}</string>
</dict>
</plist>'''
        with open(webloc_path, "w", encoding="utf-8") as f:
            f.write(plist)
        return webloc_path

    else:
        # Linux: create .desktop file
        desktop_path = desktop / f"{APP_NAME}.desktop"
        content = f"""[Desktop Entry]
Type=Application
Name={APP_NAME}
Exec=xdg-open {index_path}
Icon=text-html
Terminal=false
"""
        with open(desktop_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.chmod(desktop_path, 0o755)
        return desktop_path


def get_bundled_dir():
    """Get the directory where files are bundled (works with PyInstaller)"""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / "dist"
    else:
        return Path(__file__).parent / "dist"


def install(install_dir, progress_callback=None):
    """Copy files and create shortcut"""
    src_dir = get_bundled_dir()
    dest_dir = Path(install_dir)

    # Remove old installation if exists
    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    # Create install directory
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Get all files
    all_files = list(src_dir.rglob("*"))
    files_only = [f for f in all_files if f.is_file()]
    total = len(files_only)

    # Copy files
    for i, src_file in enumerate(files_only):
        rel_path = src_file.relative_to(src_dir)
        dest_file = dest_dir / rel_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)
        if progress_callback:
            progress_callback(i + 1, total)

    # Create shortcut
    shortcut_path = create_shortcut(install_dir)

    return shortcut_path


class InstallerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} - Installer")
        self.root.geometry("520x380")
        self.root.resizable(False, False)

        # Center window
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 11), padding=8)
        style.configure("TLabel", font=("Segoe UI", 11))
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))

        self.build_ui()

    def build_ui(self):
        # Title
        ttk.Label(self.root, text=APP_NAME, style="Title.TLabel").pack(pady=(30, 5))
        ttk.Label(self.root, text="Standard Operating Procedure", style="Subtitle.TLabel").pack()

        # Separator
        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=40, pady=20)

        # Install directory
        dir_frame = ttk.Frame(self.root)
        dir_frame.pack(fill="x", padx=40, pady=(0, 10))

        ttk.Label(dir_frame, text="Install to:").pack(anchor="w")

        dir_row = ttk.Frame(dir_frame)
        dir_row.pack(fill="x", pady=(5, 0))

        self.install_var = tk.StringVar(value=get_default_install_dir())
        self.dir_entry = ttk.Entry(dir_row, textvariable=self.install_var, font=("Segoe UI", 10))
        self.dir_entry.pack(side="left", fill="x", expand=True)

        ttk.Button(dir_row, text="Browse", command=self.browse_dir, width=8).pack(side="left", padx=(5, 0))

        # Info
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill="x", padx=40, pady=(10, 20))

        desktop_path = str(Path.home() / "Desktop" / f"{APP_NAME}")
        ttk.Label(info_frame, text=f"Desktop shortcut: {desktop_path}", foreground="gray").pack(anchor="w")

        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode="determinate", length=440)
        self.progress.pack(fill="x", padx=40, pady=(0, 5))

        self.status_var = tk.StringVar(value="Ready to install")
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, foreground="gray")
        self.status_label.pack()

        # Install button
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=20)

        self.install_btn = ttk.Button(btn_frame, text="Install", command=self.do_install, width=15)
        self.install_btn.pack()

        self.root.bind("<Return>", lambda e: self.do_install())

    def browse_dir(self):
        from tkinter import filedialog
        d = filedialog.askdirectory(title="Select Install Directory", initialdir=self.install_var.get())
        if d:
            self.install_var.set(d)

    def update_progress(self, current, total):
        self.progress["value"] = (current / total) * 100
        self.status_var.set(f"Installing... {current}/{total} files")
        self.root.update_idletasks()

    def do_install(self):
        install_dir = self.install_var.get().strip()
        if not install_dir:
            messagebox.showerror("Error", "Please select an install directory.")
            return

        self.install_btn.config(state="disabled")
        self.progress["value"] = 0
        self.status_var.set("Installing...")

        try:
            shortcut = install(install_dir, self.update_progress)
            self.progress["value"] = 100
            self.status_var.set("Installation complete!")
            self.root.update_idletasks()

            result = messagebox.askyesno(
                "Installation Complete",
                f"{APP_NAME} installed successfully!\n\n"
                f"Location: {install_dir}\n"
                f"Shortcut: {shortcut}\n\n"
                "Open now?"
            )

            if result:
                index_path = Path(install_dir) / "index.html"
                if IS_MAC:
                    subprocess.run(["open", str(index_path)])
                elif IS_WINDOWS:
                    os.startfile(str(index_path))
                else:
                    subprocess.run(["xdg-open", str(index_path)])

        except Exception as e:
            messagebox.showerror("Error", f"Installation failed:\n{e}")
            self.status_var.set("Installation failed")
        finally:
            self.install_btn.config(state="normal")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = InstallerApp()
    app.run()
