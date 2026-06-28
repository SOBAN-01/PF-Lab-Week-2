"""
ShieldAI - Phishing Link Detector (Desktop Edition)
=====================================================
Light theme: white background, pure blue (#0000FF) brand, semantic
warning colors. Pure tkinter GUI, no Flask, no HTTP - talks directly
to the functions in app.py, which read/write local JSON files.

Run:        python3 main.py
Package:    pyinstaller --onefile --windowed main.py
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog

import app


# ─── Color Palette ───────────────────────────────────────────────────────────
BG_ROOT    = "#FFFFFF"
BG_SIDEBAR = "#F0F4FF"
BG_CARD    = "#FFFFFF"
BG_INPUT   = "#F5F8FF"
BG_PANEL   = "#F8FAFF"
BG_HOVER   = "#E8EFFE"

BLUE       = "#0000FF"
BLUE_LIGHT = "#3333FF"
BLUE_PALE  = "#D6DCFF"
BLUE_MID   = "#6674E5"

BORDER     = "#D1D9F0"
BORDER_DIM = "#E8EDF8"

DANGER_FG  = "#CC0000"
DANGER_BG  = "#FFF0F0"
DANGER_BDR = "#FFAAAA"

WARN_FG    = "#B85C00"
WARN_BG    = "#FFF8EE"
WARN_BDR   = "#FFCC88"

SAFE_FG    = "#006600"
SAFE_BG    = "#F0FFF2"
SAFE_BDR   = "#88DD99"

INFO_FG    = "#0000CC"
INFO_BG    = "#F0F4FF"
INFO_BDR   = "#AABBFF"

TEXT_H1    = "#0A0A1A"
TEXT_H2    = "#1A1A3A"
TEXT_BODY  = "#2A2A4A"
TEXT_SEC   = "#5A607A"
TEXT_DIM   = "#9099B8"
TEXT_MONO  = "#3A3A5A"


# ─── Semantic helpers ─────────────────────────────────────────────────────────
def score_color(score):
    if score >= 60: return DANGER_FG
    if score >= 25: return WARN_FG
    return SAFE_FG


def tag_palette(tag):
    t = str(tag).upper()
    if t == "DANGER":
        return DANGER_FG, DANGER_BG, DANGER_BDR
    if t == "SUSPICIOUS":
        return WARN_FG, WARN_BG, WARN_BDR
    if t == "SAFE":
        return SAFE_FG, SAFE_BG, SAFE_BDR
    return INFO_FG, INFO_BG, INFO_BDR


def Separator(parent, padx=0, pady=(8, 8)):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=padx, pady=pady)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class ShieldAI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ShieldAI — Phishing Detector")
        self.geometry("1200x800")
        self.minsize(900, 640)
        self.configure(bg=BG_ROOT)
        self._style_ttk()

        app.ensure_directories()

        self._current_user = None
        self._show_login()

    def _style_ttk(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Vertical.TScrollbar",
                    background=BG_SIDEBAR, troughcolor=BG_ROOT,
                    arrowcolor=BLUE, bordercolor=BORDER, relief="flat")

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _show_login(self):
        self._current_user = None
        self._clear()
        LoginScreen(self)

    def _show_main(self, username):
        self._current_user = username
        self._clear()
        MainApp(self)


# ══════════════════════════════════════════════════════════════════════════════
#  TOAST  (lightweight inline message banner)
# ══════════════════════════════════════════════════════════════════════════════
class Toast(tk.Frame):
    """kind: "info" | "success" | "warning" | "error" """
    PALETTES = {
        "info":    (INFO_FG,    INFO_BG,    INFO_BDR,    "ℹ"),
        "success": (SAFE_FG,    SAFE_BG,    SAFE_BDR,    "✓"),
        "warning": (WARN_FG,    WARN_BG,    WARN_BDR,    "⚠"),
        "error":   (DANGER_FG,  DANGER_BG,  DANGER_BDR,  "✕"),
    }

    def __init__(self, parent, message, kind="info", auto_hide_ms=4000):
        fg, bg, bdr, icon = self.PALETTES.get(kind, self.PALETTES["info"])
        super().__init__(parent, bg=bg, highlightthickness=1,
                         highlightbackground=bdr)
        tk.Label(self, text=f" {icon} ", bg=bg, fg=fg,
                 font=("Segoe UI", 11, "bold")).pack(side="left", padx=(8, 0), pady=8)
        tk.Label(self, text=message, bg=bg, fg=fg,
                 font=("Segoe UI", 9), wraplength=600, justify="left").pack(
                 side="left", padx=8, pady=8)
        if auto_hide_ms:
            self.after(auto_hide_ms, self.destroy)


# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN / SIGNUP SCREEN
# ══════════════════════════════════════════════════════════════════════════════
class LoginScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_ROOT)
        self.master = master
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        tk.Frame(self, bg=BLUE, width=6).place(relheight=1, x=0, y=0)

        card = tk.Frame(self, bg=BG_CARD, highlightthickness=1,
                        highlightbackground=BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=520)

        icon_bg = tk.Frame(card, bg=BLUE_PALE, width=72, height=72)
        icon_bg.pack(pady=(44, 0))
        icon_bg.pack_propagate(False)
        tk.Label(icon_bg, text="⬡", bg=BLUE_PALE, fg=BLUE,
                 font=("Courier New", 28)).pack(expand=True)

        bf = tk.Frame(card, bg=BG_CARD)
        bf.pack(pady=(10, 0))
        tk.Label(bf, text="SHIELD", bg=BG_CARD, fg=TEXT_H1,
                 font=("Courier New", 22, "bold")).pack(side="left")
        tk.Label(bf, text="AI", bg=BG_CARD, fg=BLUE,
                 font=("Courier New", 22, "bold")).pack(side="left")

        tk.Label(card, text="Phishing Link Detector  //  Access Portal",
                 bg=BG_CARD, fg=TEXT_DIM, font=("Segoe UI", 8)).pack(pady=(2, 0))

        Separator(card, padx=36, pady=(18, 8))
        tk.Label(card, text="LOCAL ACCESS LAYER", bg=BG_CARD,
                 fg=TEXT_DIM, font=("Courier New", 7)).pack()

        self._username = self._field(card, "Enter account username", show="")
        self._password = self._field(card, "Enter secure password",  show="•")

        self._toast_slot = tk.Frame(card, bg=BG_CARD)
        self._toast_slot.pack(fill="x", padx=32, pady=(6, 0))

        tk.Button(card, text="SIGN IN", bg=BLUE, fg="white",
                  font=("Courier New", 10, "bold"), bd=0, cursor="hand2",
                  activebackground=BLUE_LIGHT, activeforeground="white",
                  command=self._sign_in).pack(
                  fill="x", padx=32, pady=(10, 0), ipady=11)

        tk.Button(card, text="CREATE NEW ACCOUNT", bg=BG_INPUT, fg=BLUE,
                  font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground=BLUE_PALE,
                  activebackground=BLUE_PALE, activeforeground=BLUE_LIGHT,
                  command=self._create_account).pack(
                  fill="x", padx=32, pady=(10, 0), ipady=9)

        tk.Label(card, text="ShieldAI Desktop  ·  Local JSON Storage",
                 bg=BG_CARD, fg=TEXT_DIM, font=("Segoe UI", 7)).pack(pady=(16, 0))

        self._username.bind("<Return>", lambda e: self._password.focus())
        self._password.bind("<Return>", lambda e: self._sign_in())

    def _field(self, parent, placeholder, show):
        frame = tk.Frame(parent, bg=BG_INPUT, highlightthickness=1,
                         highlightbackground=BORDER)
        frame.pack(fill="x", padx=32, pady=(12, 0), ipady=2)

        entry = tk.Entry(frame, bg=BG_INPUT, fg=TEXT_DIM, bd=0,
                         insertbackground=BLUE,
                         font=("Segoe UI", 10), show=show)
        entry.pack(fill="x", padx=12, pady=8)
        entry.insert(0, placeholder)

        def on_in(e):
            if entry.get() == placeholder:
                entry.delete(0, "end")
                entry.config(fg=TEXT_H1)
                if show:
                    entry.config(show=show)

        def on_out(e):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=TEXT_DIM, show="")

        entry.bind("<FocusIn>",  on_in)
        entry.bind("<FocusOut>", on_out)

        frame.bind("<Enter>", lambda e: frame.config(highlightbackground=BLUE))
        frame.bind("<Leave>", lambda e: frame.config(highlightbackground=BORDER))
        return entry

    def _show_toast(self, message, kind):
        for w in self._toast_slot.winfo_children():
            w.destroy()
        Toast(self._toast_slot, message, kind).pack(fill="x")

    def _get_inputs(self):
        u = self._username.get().strip()
        p = self._password.get().strip()
        if not u or u == "Enter account username":
            return None, "Username is required."
        if not p or p == "Enter secure password":
            return None, "Password is required."
        return (u, p), None

    def _sign_in(self):
        creds, err = self._get_inputs()
        if err:
            return self._show_toast(err, "warning")

        result = app.login(creds[0], creds[1])
        if result["success"]:
            self.master._show_main(result["username"])
        else:
            self._show_toast(result.get("error", "Login failed."), "error")

    def _create_account(self):
        creds, err = self._get_inputs()
        if err:
            return self._show_toast(err, "warning")

        result = app.signup(creds[0], creds[1])
        if result["success"]:
            self._show_toast("Account created. You can now sign in.", "success")
        else:
            self._show_toast(result.get("error", "Registration failed."), "error")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP SHELL  (sidebar + content)
# ══════════════════════════════════════════════════════════════════════════════
class MainApp(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_ROOT)
        self.master = master
        self.pack(fill="both", expand=True)
        self._build()
        self._nav_to("scanner")

    def _build(self):
        self._sidebar = tk.Frame(self, bg=BG_SIDEBAR, width=224)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        tk.Frame(self._sidebar, bg=BLUE, height=4).pack(fill="x")

        bf = tk.Frame(self._sidebar, bg=BG_SIDEBAR)
        bf.pack(fill="x", padx=16, pady=(18, 0))
        icon_bg = tk.Frame(bf, bg=BLUE_PALE, width=34, height=34)
        icon_bg.pack(side="left")
        icon_bg.pack_propagate(False)
        tk.Label(icon_bg, text="⬡", bg=BLUE_PALE, fg=BLUE,
                 font=("Courier New", 14)).pack(expand=True)
        nb = tk.Frame(bf, bg=BG_SIDEBAR)
        nb.pack(side="left", padx=8)
        nr = tk.Frame(nb, bg=BG_SIDEBAR)
        nr.pack(anchor="w")
        tk.Label(nr, text="SHIELD", bg=BG_SIDEBAR, fg=TEXT_H1,
                 font=("Courier New", 12, "bold")).pack(side="left")
        tk.Label(nr, text="AI", bg=BG_SIDEBAR, fg=BLUE,
                 font=("Courier New", 12, "bold")).pack(side="left")
        tk.Label(nb, text="Phishing Detector", bg=BG_SIDEBAR,
                 fg=TEXT_DIM, font=("Segoe UI", 7)).pack(anchor="w")

        Separator(self._sidebar, padx=14, pady=(16, 6))

        self._nav_btns = {}
        for key, icon, label in [
            ("scanner", "🔍", "URL Scanner"),
            ("history", "📊", "Scan History"),
            ("profile", "👤", "My Profile"),
        ]:
            btn = tk.Button(
                self._sidebar, text=f"  {icon}  {label}", anchor="w",
                bg=BG_SIDEBAR, fg=TEXT_BODY, bd=0, cursor="hand2",
                font=("Segoe UI", 10), padx=12, pady=10,
                activebackground=BLUE_PALE, activeforeground=BLUE,
                command=lambda k=key: self._nav_to(k))
            btn.pack(fill="x", padx=8, pady=1)
            self._nav_btns[key] = btn

        Separator(self._sidebar, padx=14, pady=(8, 8))

        status = tk.Frame(self._sidebar, bg=SAFE_BG,
                          highlightthickness=1, highlightbackground=SAFE_BDR)
        status.pack(fill="x", padx=12, pady=(4, 0))
        sr = tk.Frame(status, bg=SAFE_BG)
        sr.pack(padx=10, pady=8, anchor="w")
        tk.Label(sr, text="● ", bg=SAFE_BG, fg=SAFE_FG,
                 font=("Segoe UI", 8)).pack(side="left")
        tk.Label(sr, text="Engine Online · Local Analysis Mode",
                 bg=SAFE_BG, fg=SAFE_FG, font=("Segoe UI", 8)).pack(side="left")

        tk.Button(self._sidebar, text="  ⇥  Logout", anchor="w",
                  bg=BG_SIDEBAR, fg=DANGER_FG, bd=0, cursor="hand2",
                  font=("Segoe UI", 9), padx=12, pady=10,
                  activebackground=DANGER_BG, activeforeground=DANGER_FG,
                  command=self.master._show_login).pack(
                  fill="x", padx=8, pady=(0, 12), side="bottom")

        self._content = tk.Frame(self, bg=BG_ROOT)
        self._content.pack(side="left", fill="both", expand=True)

    def _nav_to(self, key):
        for k, btn in self._nav_btns.items():
            if k == key:
                btn.config(bg=BLUE_PALE, fg=BLUE, font=("Segoe UI", 10, "bold"))
            else:
                btn.config(bg=BG_SIDEBAR, fg=TEXT_BODY, font=("Segoe UI", 10))
        for w in self._content.winfo_children():
            w.destroy()
        if key == "scanner": ScannerPage(self._content, self)
        elif key == "history": HistoryPage(self._content, self)
        elif key == "profile": ProfilePage(self._content, self)

    @property
    def current_user(self):
        return self.master._current_user


# ══════════════════════════════════════════════════════════════════════════════
#  URL SCANNER PAGE (Dashboard)
# ══════════════════════════════════════════════════════════════════════════════
class ScannerPage(tk.Frame):
    def __init__(self, parent, main_app):
        super().__init__(parent, bg=BG_ROOT)
        self.main_app = main_app
        self.pack(fill="both", expand=True)
        self._scanning = False
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=BG_ROOT)
        hdr.pack(fill="x", padx=28, pady=(24, 0))
        tk.Label(hdr, text="URL Scanner", bg=BG_ROOT, fg=TEXT_H1,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(hdr, text="Paste a suspicious URL and run a phishing analysis.",
                 bg=BG_ROOT, fg=TEXT_SEC, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

        self._engine_badge = tk.Label(
            hdr, text=" ⚡  SCAN ENGINE READY ",
            bg=INFO_BG, fg=INFO_FG, font=("Courier New", 8, "bold"),
            highlightthickness=1, highlightbackground=INFO_BDR)
        self._engine_badge.pack(side="right", anchor="ne", padx=(0, 4))

        Separator(self, padx=28, pady=(16, 0))

        inp_row = tk.Frame(self, bg=BG_ROOT)
        inp_row.pack(fill="x", padx=28, pady=(14, 0))

        inp_wrap = tk.Frame(inp_row, bg=BG_INPUT, highlightthickness=1,
                            highlightbackground=BORDER)
        inp_wrap.pack(side="left", fill="x", expand=True, ipady=2)
        inp_wrap.bind("<Enter>", lambda e: inp_wrap.config(highlightbackground=BLUE))
        inp_wrap.bind("<Leave>", lambda e: inp_wrap.config(highlightbackground=BORDER))

        tk.Label(inp_wrap, text="🌐", bg=BG_INPUT, fg=TEXT_DIM,
                 font=("Segoe UI", 11)).pack(side="left", padx=(10, 0))
        self._url_var = tk.StringVar()
        self._url_entry = tk.Entry(
            inp_wrap, textvariable=self._url_var,
            bg=BG_INPUT, fg=TEXT_H1, bd=0, insertbackground=BLUE,
            font=("Segoe UI", 10))
        self._url_entry.pack(side="left", fill="x", expand=True, padx=8, pady=10)
        self._url_entry.bind("<Return>", lambda e: self._start_scan())

        self._scan_btn = tk.Button(
            inp_row, text="⚡  Analyze Target",
            bg=BLUE, fg="white", bd=0, cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            activebackground=BLUE_LIGHT, activeforeground="white",
            command=self._start_scan, padx=18, pady=11)
        self._scan_btn.pack(side="left", padx=(10, 0))

        self._toast_slot = tk.Frame(self, bg=BG_ROOT)
        self._toast_slot.pack(fill="x", padx=28, pady=(10, 0))

        self._result_frame = tk.Frame(self, bg=BG_ROOT)
        self._result_frame.pack(fill="both", expand=True, padx=28, pady=(12, 0))
        self._show_idle()

    def _show_toast(self, message, kind):
        for w in self._toast_slot.winfo_children():
            w.destroy()
        Toast(self._toast_slot, message, kind).pack(fill="x")

    def _show_idle(self):
        for w in self._result_frame.winfo_children():
            w.destroy()
        idle = tk.Frame(self._result_frame, bg=BG_ROOT)
        idle.pack(expand=True)
        tk.Label(idle, text="🔍", bg=BG_ROOT, fg=TEXT_DIM,
                 font=("Segoe UI", 32)).pack(pady=(50, 8))
        tk.Label(idle, text="Awaiting target URL", bg=BG_ROOT, fg=TEXT_DIM,
                 font=("Segoe UI", 12, "bold")).pack()
        tk.Label(idle, text="Paste any URL above and press Analyze Target",
                 bg=BG_ROOT, fg=TEXT_DIM, font=("Segoe UI", 9)).pack(pady=(4, 0))

    def _start_scan(self):
        url = self._url_var.get().strip()
        if not url:
            self._show_toast("Enter a URL before scanning.", "warning")
            return
        if self._scanning:
            return

        self._scanning = True
        self._scan_btn.config(state="disabled", text="⏳  Scanning…", bg=BLUE_MID)
        self._engine_badge.config(text=" ⏳  PROCESSING ", bg=WARN_BG, fg=WARN_FG,
                                  highlightbackground=WARN_BDR)
        self._show_toast("Running phishing analysis…", "info")

        # Scanning involves a real TLS handshake attempt, which can briefly
        # block - run it off the main thread so the GUI never freezes.
        def run():
            username = self.main_app.current_user
            result = app.scan_url(username, url)
            self.after(0, lambda: self._on_done(result))

        threading.Thread(target=run, daemon=True).start()

    def _on_done(self, result):
        self._scanning = False
        self._scan_btn.config(state="normal", text="⚡  Analyze Target", bg=BLUE)
        self._engine_badge.config(text=" ⚡  SCAN ENGINE READY ", bg=INFO_BG, fg=INFO_FG,
                                  highlightbackground=INFO_BDR)

        if not result.get("success"):
            self._show_toast(result.get("error", "Scan failed."), "error")
            return

        for w in self._toast_slot.winfo_children():
            w.destroy()
        self._display_result(result)

    def _display_result(self, r):
        for w in self._result_frame.winfo_children():
            w.destroy()

        tag   = str(r.get("danger_level", "SAFE")).upper()
        score = r.get("risk_score", 0)
        fg, bg_card, bdr = tag_palette(tag)
        sc    = score_color(score)

        canvas = tk.Canvas(self._result_frame, bg=BG_ROOT, highlightthickness=0)
        sb = ttk.Scrollbar(self._result_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=BG_ROOT)
        cw = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _cfg(e): canvas.configure(scrollregion=canvas.bbox("all"))
        def _rsz(e): canvas.itemconfig(cw, width=e.width)
        inner.bind("<Configure>", _cfg)
        canvas.bind("<Configure>", _rsz)
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        card = tk.Frame(inner, bg=bg_card, highlightthickness=1, highlightbackground=bdr)
        card.pack(fill="x", pady=(0, 10))

        left = tk.Frame(card, bg=bg_card, width=110)
        left.pack(side="left", padx=20, pady=20)
        left.pack_propagate(False)
        circ = tk.Canvas(left, width=90, height=90, bg=bg_card, highlightthickness=0)
        circ.pack()
        circ.create_oval(5, 5, 85, 85, outline=BORDER, width=7)
        extent = int(score / 100 * 359)
        circ.create_arc(5, 5, 85, 85, start=90, extent=-extent, outline=sc, width=7, style="arc")
        circ.create_text(45, 42, text=str(score), fill=sc, font=("Courier New", 22, "bold"))
        circ.create_text(45, 62, text="RISK", fill=TEXT_DIM, font=("Courier New", 7))

        right = tk.Frame(card, bg=bg_card)
        right.pack(side="left", fill="both", expand=True, pady=16)

        tag_badge = tk.Label(right, text=f"  {tag}  ", bg=bg_card, fg=fg,
                             font=("Courier New", 9, "bold"),
                             highlightthickness=1, highlightbackground=bdr)
        tag_badge.pack(anchor="w", pady=(0, 6))

        tk.Label(right, text=r.get("url", ""), bg=bg_card, fg=TEXT_MONO,
                 font=("Courier New", 9)).pack(anchor="w")

        reasons = r.get("reasons", [])
        if reasons:
            Separator(right, pady=(10, 6))
            tk.Label(right, text="Flagged reasons:", bg=bg_card,
                     fg=TEXT_SEC, font=("Segoe UI", 8, "bold")).pack(anchor="w")
            for reason in reasons:
                rf = tk.Frame(right, bg=bg_card)
                rf.pack(fill="x", anchor="w", pady=1)
                tk.Label(rf, text="›", bg=bg_card, fg=sc,
                         font=("Segoe UI", 9, "bold")).pack(side="left")
                tk.Label(rf, text="  " + reason, bg=bg_card, fg=TEXT_BODY,
                         font=("Segoe UI", 9), wraplength=700,
                         justify="left").pack(side="left")

        tk.Label(card, text=f"  {score}/100  ", bg=bg_card, fg=sc,
                 font=("Courier New", 11, "bold"),
                 highlightthickness=1, highlightbackground=bdr).pack(
                 side="right", anchor="ne", padx=16, pady=16)

        if tag == "DANGER":
            kind, msg = "error", "Critical threat indicators found. Do not submit any credentials or personal data on this site."
        elif tag == "SUSPICIOUS":
            kind, msg = "warning", "Suspicious indicators detected. Proceed with caution and verify this domain independently."
        else:
            kind, msg = "success", "No threats detected based on the heuristics checked."

        Toast(inner, msg, kind, auto_hide_ms=0).pack(fill="x", pady=(0, 6))


# ══════════════════════════════════════════════════════════════════════════════
#  SCAN HISTORY PAGE
# ══════════════════════════════════════════════════════════════════════════════
class HistoryPage(tk.Frame):
    SORT_LABELS = {
        "Newest first": "newest",
        "Oldest first": "oldest",
        "Highest risk score": "highest",
        "Lowest risk score": "lowest",
    }

    def __init__(self, parent, main_app):
        super().__init__(parent, bg=BG_ROOT)
        self.main_app = main_app
        self.pack(fill="both", expand=True)
        self._records = []
        self._build()
        self._refresh()

    def _build(self):
        hdr = tk.Frame(self, bg=BG_ROOT)
        hdr.pack(fill="x", padx=28, pady=(24, 0))
        tk.Label(hdr, text="Scan History", bg=BG_ROOT, fg=TEXT_H1,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(hdr, text="All recorded scan events for this account.",
                 bg=BG_ROOT, fg=TEXT_SEC, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

        Separator(self, padx=28, pady=(16, 0))

        # Search + sort controls
        controls = tk.Frame(self, bg=BG_ROOT)
        controls.pack(fill="x", padx=28, pady=(14, 0))

        search_wrap = tk.Frame(controls, bg=BG_INPUT, highlightthickness=1,
                               highlightbackground=BORDER)
        search_wrap.pack(side="left", fill="x", expand=True, ipady=2)
        tk.Label(search_wrap, text="🔎", bg=BG_INPUT, fg=TEXT_DIM,
                 font=("Segoe UI", 10)).pack(side="left", padx=(10, 0))
        self._search_var = tk.StringVar()
        search_entry = tk.Entry(search_wrap, textvariable=self._search_var,
                                bg=BG_INPUT, fg=TEXT_H1, bd=0,
                                insertbackground=BLUE, font=("Segoe UI", 9))
        search_entry.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        search_entry.bind("<KeyRelease>", lambda e: self._refresh())

        self._sort_var = tk.StringVar(value="Newest first")
        sort_menu = ttk.Combobox(controls, textvariable=self._sort_var,
                                 values=list(self.SORT_LABELS.keys()),
                                 state="readonly", width=20, font=("Segoe UI", 9))
        sort_menu.pack(side="left", padx=(10, 0))
        sort_menu.bind("<<ComboboxSelected>>", lambda e: self._refresh())

        # Stats row
        self._stats_frame = tk.Frame(self, bg=BG_ROOT)
        self._stats_frame.pack(fill="x", padx=28, pady=(14, 0))

        # Column header
        col_hdr = tk.Frame(self, bg=BG_SIDEBAR)
        col_hdr.pack(fill="x", padx=28, pady=(16, 0))
        for text, w in [("Status", 120), ("URL / Domain", 0), ("Score", 70), ("Time", 160), ("", 60)]:
            tk.Label(col_hdr, text=text, bg=BG_SIDEBAR, fg=TEXT_SEC,
                     font=("Segoe UI", 8, "bold"),
                     width=w if w else None, anchor="w").pack(
                     side="left", padx=(12 if text == "Status" else 0, 0), pady=5)

        # Scrollable list
        lc = tk.Canvas(self, bg=BG_ROOT, highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=lc.yview)
        lc.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        lc.pack(fill="both", expand=True, padx=28, pady=(2, 16))
        self._list_inner = tk.Frame(lc, bg=BG_ROOT)
        cw = lc.create_window((0, 0), window=self._list_inner, anchor="nw")

        def _cfg(e): lc.configure(scrollregion=lc.bbox("all"))
        def _rsz(e): lc.itemconfig(cw, width=e.width)
        self._list_inner.bind("<Configure>", _cfg)
        lc.bind("<Configure>", _rsz)
        lc.bind_all("<MouseWheel>",
            lambda e: lc.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    def _refresh(self):
        username = self.main_app.current_user
        method = self.SORT_LABELS.get(self._sort_var.get(), "newest")
        query = self._search_var.get().strip()

        if query:
            records = app.search_history(username, query)
            # search_history is newest-first; still honor the sort dropdown
            if method == "oldest":
                records = list(reversed(records))
            elif method == "highest":
                records = sorted(records, key=lambda r: r.get("risk_score", 0), reverse=True)
            elif method == "lowest":
                records = sorted(records, key=lambda r: r.get("risk_score", 0))
        else:
            records = app.sort_history(username, method)

        self._records = records
        self._render_stats()
        self._render_list()

    def _render_stats(self):
        for w in self._stats_frame.winfo_children():
            w.destroy()

        all_records = app.get_history(self.main_app.current_user)
        danger_c = sum(1 for s in all_records if s.get("danger_level") == "DANGER")
        susp_c   = sum(1 for s in all_records if s.get("danger_level") == "SUSPICIOUS")
        safe_c   = sum(1 for s in all_records if s.get("danger_level") == "SAFE")
        total_c  = len(all_records)

        for val, label, fg in [
            (total_c,  "Total",      BLUE),
            (danger_c, "Danger",     DANGER_FG),
            (susp_c,   "Suspicious", WARN_FG),
            (safe_c,   "Safe",       SAFE_FG),
        ]:
            chip = tk.Frame(self._stats_frame, bg=BG_PANEL, highlightthickness=1,
                            highlightbackground=BORDER)
            chip.pack(side="left", padx=(0, 8), ipadx=10, ipady=6)
            tk.Label(chip, text=str(val), bg=BG_PANEL, fg=fg,
                     font=("Segoe UI", 18, "bold")).pack(side="left", padx=(12, 4))
            tk.Label(chip, text=label, bg=BG_PANEL, fg=TEXT_SEC,
                     font=("Segoe UI", 8)).pack(side="left", padx=(0, 10))

    def _render_list(self):
        for w in self._list_inner.winfo_children():
            w.destroy()

        if not self._records:
            Toast(self._list_inner, "No matching scans found.",
                  "info", auto_hide_ms=0).pack(fill="x", pady=8)
        else:
            for entry in self._records:
                self._make_row(self._list_inner, entry)

    def _make_row(self, parent, entry):
        tag = str(entry.get("danger_level", "SAFE")).upper()
        fg, bg_row, bdr = tag_palette(tag)
        score = entry.get("risk_score", 0)

        row = tk.Frame(parent, bg=BG_CARD, highlightthickness=1,
                       highlightbackground=BORDER_DIM)
        row.pack(fill="x", pady=(0, 1))

        badge = tk.Label(row, text=f"  {tag}  ", bg=bg_row, fg=fg,
                         font=("Courier New", 8, "bold"),
                         highlightthickness=1, highlightbackground=bdr)
        badge.pack(side="left", padx=12, pady=10)

        url_txt = str(entry.get("url", ""))
        tk.Label(row, text=url_txt[:55] + ("…" if len(url_txt) > 55 else ""),
                 bg=BG_CARD, fg=TEXT_BODY,
                 font=("Segoe UI", 9)).pack(side="left", padx=12)

        del_btn = tk.Button(row, text="🗑", bg=BG_CARD, fg=DANGER_FG, bd=0,
                            cursor="hand2", font=("Segoe UI", 10),
                            activebackground=DANGER_BG,
                            command=lambda eid=entry.get("scan_id"): self._delete(eid))
        del_btn.pack(side="right", padx=12)

        tk.Label(row, text=entry.get("timestamp", ""), bg=BG_CARD,
                 fg=TEXT_DIM, font=("Segoe UI", 8)).pack(side="right", padx=16)

        tk.Label(row, text=str(score), bg=BG_CARD, fg=score_color(score),
                 font=("Segoe UI", 14, "bold")).pack(side="right", padx=(0, 8))
        tk.Label(row, text="risk", bg=BG_CARD, fg=TEXT_DIM,
                 font=("Segoe UI", 7)).pack(side="right")

        row.bind("<Enter>", lambda e, r=row: r.config(bg=BG_HOVER))
        row.bind("<Leave>", lambda e, r=row: r.config(bg=BG_CARD))

    def _delete(self, scan_id):
        if not scan_id:
            return
        app.delete_scan(self.main_app.current_user, scan_id)
        self._refresh()


# ══════════════════════════════════════════════════════════════════════════════
#  PROFILE PAGE
# ══════════════════════════════════════════════════════════════════════════════
class ProfilePage(tk.Frame):
    def __init__(self, parent, main_app):
        super().__init__(parent, bg=BG_ROOT)
        self.main_app = main_app
        self.pack(fill="both", expand=True)
        self._avatar_image = None  # keep a reference so it isn't garbage-collected
        self._build()

    def _build(self):
        tk.Label(self, text="My Profile", bg=BG_ROOT, fg=TEXT_H1,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=28, pady=(24, 2))
        tk.Label(self, text="Account details and settings.",
                 bg=BG_ROOT, fg=TEXT_SEC, font=("Segoe UI", 9)).pack(anchor="w", padx=28)

        Separator(self, padx=28, pady=(16, 0))

        profile = app.get_profile(self.main_app.current_user)

        # Identity card
        id_card = tk.Frame(self, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER)
        id_card.pack(fill="x", padx=28, pady=(14, 0))

        self._avatar_frame = tk.Frame(id_card, bg=BLUE_PALE, width=58, height=58)
        self._avatar_frame.pack(side="left", padx=20, pady=20)
        self._avatar_frame.pack_propagate(False)
        self._render_avatar(profile.get("profile_image"))

        info = tk.Frame(id_card, bg=BG_CARD)
        info.pack(side="left", pady=20, fill="x", expand=True)
        self._username_label = tk.Label(info, text=profile.get("username", "").upper(),
                                        bg=BG_CARD, fg=TEXT_H1, font=("Segoe UI", 14, "bold"))
        self._username_label.pack(anchor="w")
        Toast(info, "Account active — local session", "success", auto_hide_ms=0).pack(
            anchor="w", pady=(6, 0))

        btn_col = tk.Frame(id_card, bg=BG_CARD)
        btn_col.pack(side="right", padx=20, pady=20)
        tk.Button(btn_col, text="Change image", bg=BG_INPUT, fg=BLUE, bd=0,
                  cursor="hand2", font=("Segoe UI", 9, "bold"),
                  highlightthickness=1, highlightbackground=BLUE_PALE,
                  activebackground=BLUE_PALE,
                  command=self._change_image).pack(fill="x", pady=(0, 6), ipady=4)
        tk.Button(btn_col, text="Change username", bg=BG_INPUT, fg=BLUE, bd=0,
                  cursor="hand2", font=("Segoe UI", 9, "bold"),
                  highlightthickness=1, highlightbackground=BLUE_PALE,
                  activebackground=BLUE_PALE,
                  command=self._change_username).pack(fill="x", ipady=4)

        self._toast_slot = tk.Frame(self, bg=BG_ROOT)
        self._toast_slot.pack(fill="x", padx=28, pady=(10, 0))

        # Stats
        stats_card = tk.Frame(self, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER)
        stats_card.pack(fill="x", padx=28, pady=(12, 0))
        tk.Label(stats_card, text="Account Statistics", bg=BG_CARD,
                 fg=TEXT_SEC, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(14, 6))
        sg = tk.Frame(stats_card, bg=BG_CARD)
        sg.pack(fill="x", padx=16, pady=(0, 14))
        for val, label, fg in [
            (profile.get("total_scans", 0),      "Scans performed",  BLUE),
            (profile.get("threats_detected", 0), "Threats detected", DANGER_FG),
        ]:
            tk.Label(sg, text=str(val), bg=BG_CARD, fg=fg,
                     font=("Segoe UI", 22, "bold")).pack(side="left", padx=(0, 4))
            tk.Label(sg, text=label, bg=BG_CARD, fg=TEXT_SEC,
                     font=("Segoe UI", 8)).pack(side="left", padx=(0, 30))

        Separator(self, padx=28, pady=(16, 4))

        tk.Button(self, text="  ⇥  Logout and end session",
                  bg=DANGER_BG, fg=DANGER_FG, bd=0, cursor="hand2",
                  font=("Segoe UI", 10, "bold"),
                  highlightthickness=1, highlightbackground=DANGER_BDR,
                  activebackground=DANGER_BG, activeforeground=DANGER_FG,
                  command=self.main_app.master._show_login, padx=18, pady=10).pack(
                  padx=28, anchor="w")

    def _render_avatar(self, profile_image_rel_path):
        for w in self._avatar_frame.winfo_children():
            w.destroy()

        full_path = None
        if profile_image_rel_path:
            full_path = os.path.join(app.BASE_DIR, profile_image_rel_path)

        if full_path and os.path.exists(full_path):
            try:
                img = tk.PhotoImage(file=full_path)
                # Cheap downscale to fit the 58x58 avatar slot without Pillow.
                w, h = img.width(), img.height()
                factor = max(1, max(w, h) // 58)
                if factor > 1:
                    img = img.subsample(factor, factor)
                self._avatar_image = img
                tk.Label(self._avatar_frame, image=img, bg=BLUE_PALE).pack(expand=True)
                return
            except Exception:
                pass  # fall through to the placeholder glyph

        tk.Label(self._avatar_frame, text="👤", bg=BLUE_PALE, fg=BLUE,
                 font=("Segoe UI", 22)).pack(expand=True)

    def _show_toast(self, message, kind):
        for w in self._toast_slot.winfo_children():
            w.destroy()
        Toast(self._toast_slot, message, kind).pack(fill="x")

    def _change_image(self):
        path = filedialog.askopenfilename(
            title="Choose a profile image (PNG or GIF)",
            filetypes=[("PNG/GIF images", "*.png *.gif")])
        if not path:
            return
        result = app.set_profile_image(self.main_app.current_user, path)
        if result["success"]:
            self._show_toast("Profile image updated.", "success")
            self._render_avatar(result.get("profile_image"))
        else:
            self._show_toast(result.get("error", "Could not update image."), "error")

    def _change_username(self):
        new_name = simpledialog.askstring(
            "Change username", "Enter a new username:", parent=self)
        if not new_name:
            return
        result = app.update_profile(self.main_app.current_user, new_name)
        if result["success"]:
            self.main_app.master._current_user = result["username"]
            self._username_label.config(text=result["username"].upper())
            self._show_toast("Username updated.", "success")
        else:
            self._show_toast(result.get("error", "Could not update username."), "error")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    gui = ShieldAI()
    gui.mainloop()
