"""
Mark.me - Interface gráfica (Tkinter).
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser

from mark_me.core import contar_ocorrencias_multi, destacar_pdf_multi
from mark_me.i18n import t, set_lang, get_lang


# Paleta moderna (dark)
BG = "#0f0f12"
SURFACE = "#18181c"
BORDER = "#2a2a30"
TEXT = "#e4e4e7"
TEXT_MUTED = "#71717a"
BTN_BG = "#000000"

CORES_PADRAO = ("#ffff00", "#00ff00", "#00bfff", "#ff69b4", "#ffa500")

# (display name, locale code) for language switcher
LANGUAGES = [
    ("English", "en"),
    ("Português", "pt_BR"),
    ("Deutsch", "de"),
    ("Español", "es"),
]


def _make_btn(parent, text, command, padx=14, pady=8, font=("Helvetica", 10), bold=False):
    """Botão como Frame+Label para cor preta garantida."""
    f = tk.Frame(parent, bg=BTN_BG, cursor="hand2")
    font_tuple = (font[0], font[1], "bold") if bold else font
    lbl = tk.Label(f, text=text, fg=TEXT, bg=BTN_BG, font=font_tuple, cursor="hand2")
    lbl.pack(padx=padx, pady=pady)
    for w in (f, lbl):
        w.bind("<Button-1>", lambda e, c=command: c())
        w.bind("<Enter>", lambda e, ww=lbl: ww.config(fg=TEXT, bg=BTN_BG))
        w.bind("<Leave>", lambda e, ww=lbl: ww.config(fg=TEXT, bg=BTN_BG))
    return f


class MarkMeApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(t("app.title"))
        self.root.resizable(True, True)
        self.root.minsize(420, 520)
        self.root.configure(bg=BG)

        self.pdf_path: str = ""
        self.pdf_label_var = tk.StringVar(value=t("ui.no_file"))
        self.termo_rows: list[dict] = []  # {"frame", "entry", "patch", "color"}
        self.max_termos = 32
        self.scroll_canvas = None
        self.scroll_inner = None

        self._build_ui()

    def _build_ui(self):
        pad_label = {"padx": 16, "pady": 6}
        pad_row = {"padx": 16, "pady": 10}
        row = 0

        self._titulo = tk.Label(self.root, text=t("app.title"), font=("Helvetica", 22, "bold"), fg=TEXT, bg=BG)
        self._titulo.grid(row=row, column=0, **pad_row, sticky="w")
        self._lang_var = tk.StringVar()
        lang_frame = tk.Frame(self.root, bg=BG)
        lang_frame.grid(row=row, column=1, **pad_row, sticky="e")
        tk.Label(lang_frame, text=t("ui.language"), fg=TEXT_MUTED, bg=BG, font=("Helvetica", 10)).pack(side="left", padx=(0, 6))
        self._lang_menu = tk.OptionMenu(
            lang_frame,
            self._lang_var,
            *[name for name, _ in LANGUAGES],
            command=self._on_lang_change,
        )
        self._lang_menu.config(bg=SURFACE, fg=TEXT, activebackground=SURFACE, activeforeground=TEXT, highlightthickness=0)
        self._lang_menu.pack(side="left")
        self._sync_lang_dropdown()
        row += 1

        self._subtitulo = tk.Label(
            self.root,
            text=t("app.tagline"),
            font=("Helvetica", 11),
            fg=TEXT_MUTED,
            bg=BG,
        )
        self._subtitulo.grid(row=row, column=0, columnspan=2, **pad_row, sticky="w")
        row += 2

        card = tk.Frame(self.root, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1, padx=16, pady=16)
        card.grid(row=row, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="ew")
        row += 1

        # PDF
        self._label_pdf = tk.Label(card, text=t("ui.pdf_file"), fg=TEXT_MUTED, bg=SURFACE, font=("Helvetica", 10))
        self._label_pdf.grid(row=0, column=0, **pad_label, sticky="w")
        lbl_pdf = tk.Label(card, textvariable=self.pdf_label_var, fg=TEXT_MUTED, bg=SURFACE, font=("Helvetica", 10))
        lbl_pdf.grid(row=0, column=1, **pad_label, sticky="ew")
        row_inner = 1
        self._btn_pdf = _make_btn(card, t("ui.select_pdf"), self._escolher_pdf)
        self._btn_pdf.grid(row=row_inner, column=0, columnspan=2, **pad_label, sticky="w")
        row_inner += 2

        # Termos e cores (label)
        self._label_terms = tk.Label(card, text=t("ui.terms_and_colors"), fg=TEXT_MUTED, bg=SURFACE, font=("Helvetica", 10))
        self._label_terms.grid(row=row_inner, column=0, columnspan=2, **pad_label, sticky="w")
        row_inner += 1

        # Área rolável com altura fixa + 4 colunas × 8 linhas (máx. 32 termos)
        scroll_frame = tk.Frame(card, bg=SURFACE)
        scroll_frame.grid(row=row_inner, column=0, columnspan=2, **pad_label, sticky="nsew")
        row_inner += 1

        self.scroll_canvas = tk.Canvas(scroll_frame, bg=SURFACE, highlightthickness=0, height=320)
        scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=self.scroll_canvas.yview, bg=BORDER)
        self.scroll_inner = tk.Frame(self.scroll_canvas, bg=SURFACE)
        self.scroll_inner.bind("<Configure>", self._on_scroll_configure)
        self._scroll_win_id = self.scroll_canvas.create_window((0, 0), window=self.scroll_inner, anchor="nw")
        self.scroll_canvas.configure(yscrollcommand=scrollbar.set)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        self.scroll_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scroll_canvas.bind("<Button-4>", self._on_mousewheel)
        self.scroll_canvas.bind("<Button-5>", self._on_mousewheel)

        for c in range(4):
            self.scroll_inner.columnconfigure(c, weight=1)

        self._btn_add = _make_btn(card, t("ui.add_term"), self._adicionar_termo, padx=10, pady=6)
        self._btn_add.grid(row=row_inner, column=0, columnspan=2, **pad_label, sticky="w")
        row_inner += 1

        card.columnconfigure(1, weight=1)
        self._adicionar_termo()

        # Botão principal (sempre visível: card row absorve espaço extra)
        row += 1
        self._btn_gerar = _make_btn(self.root, t("ui.generate"), self._gerar, padx=24, pady=12, font=("Helvetica", 12), bold=True)
        self._btn_gerar.grid(row=row, column=0, columnspan=2, pady=20, padx=16, sticky="ew")
        row += 1

        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)

    def _sync_lang_dropdown(self) -> None:
        """Set dropdown to current language display name."""
        for name, code in LANGUAGES:
            if code == get_lang():
                self._lang_var.set(name)
                break

    def _on_lang_change(self, display_name: str) -> None:
        for name, code in LANGUAGES:
            if name == display_name:
                set_lang(code)
                self._refresh_ui_texts()
                break

    def _refresh_ui_texts(self) -> None:
        """Update all UI strings to current language."""
        self.root.title(t("app.title"))
        self._titulo.config(text=t("app.title"))
        self._subtitulo.config(text=t("app.tagline"))
        self._label_pdf.config(text=t("ui.pdf_file"))
        if not self.pdf_path:
            self.pdf_label_var.set(t("ui.no_file"))
        self._btn_pdf.winfo_children()[0].config(text=t("ui.select_pdf"))
        self._label_terms.config(text=t("ui.terms_and_colors"))
        self._btn_add.winfo_children()[0].config(text=t("ui.add_term"))
        self._btn_gerar.winfo_children()[0].config(text=t("ui.generate"))
        # Update "Language" label next to dropdown
        for w in self._lang_menu.master.winfo_children():
            if isinstance(w, tk.Label):
                w.config(text=t("ui.language"))
                break

    def _on_scroll_configure(self, event) -> None:
        if self.scroll_canvas:
            self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        if self.scroll_canvas and hasattr(self, "_scroll_win_id"):
            self.scroll_canvas.itemconfig(self._scroll_win_id, width=event.width)
        if self.scroll_canvas:
            self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_mousewheel(self, event) -> None:
        if not self.scroll_canvas:
            return
        # macOS: event.delta; Linux: event.num (4=up, 5=down)
        if getattr(event, "num", None) == 5:
            self.scroll_canvas.yview_scroll(1, "units")
        elif getattr(event, "num", None) == 4:
            self.scroll_canvas.yview_scroll(-1, "units")
        else:
            delta = getattr(event, "delta", 0)
            self.scroll_canvas.yview_scroll(int(-1 * (delta / 120)), "units")

    def _atualizar_patch(self, patch: tk.Canvas, hex_color: str) -> None:
        try:
            patch.delete("all")
            patch.create_rectangle(0, 0, 32, 32, fill=hex_color, outline=BORDER, width=1)
        except tk.TclError:
            pass

    def _adicionar_termo(self) -> None:
        if len(self.termo_rows) >= self.max_termos:
            messagebox.showinfo(t("msg.limit_title"), t("msg.limit_body", n=self.max_termos))
            return
        idx = len(self.termo_rows)
        cor = CORES_PADRAO[idx % len(CORES_PADRAO)] if idx < len(CORES_PADRAO) else "#ffff00"

        row_frame = tk.Frame(self.scroll_inner, bg=SURFACE)
        row_frame.grid(row=idx // 4, column=idx % 4, sticky="ew", pady=2, padx=(0, 6))
        row_frame.columnconfigure(0, weight=1)

        entry = tk.Entry(row_frame, width=14, bg=BG, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Menlo", 10))
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)

        patch = tk.Canvas(row_frame, width=32, height=32, bg=SURFACE, highlightthickness=0, cursor="hand2")
        patch.grid(row=0, column=1, padx=(0, 4))
        self._atualizar_patch(patch, cor)

        def pick_color() -> None:
            rgb, hex_str = colorchooser.askcolor(title=t("dialog.color_title"), initialcolor=data["color"])
            if hex_str:
                data["color"] = hex_str.strip()
                self._atualizar_patch(patch, data["color"])

        patch.bind("<Button-1>", lambda e: pick_color())

        def remove_row() -> None:
            for i, r in enumerate(self.termo_rows):
                if r["frame"] == row_frame:
                    r["frame"].destroy()
                    self.termo_rows.pop(i)
                    break
            self._reindex_rows()

        lbl_remove = tk.Label(row_frame, text="×", fg=TEXT_MUTED, bg=SURFACE, font=("Helvetica", 14), cursor="hand2")
        lbl_remove.grid(row=0, column=2)
        lbl_remove.bind("<Button-1>", lambda e: remove_row())
        row_frame.columnconfigure(0, weight=1)

        data = {"frame": row_frame, "entry": entry, "patch": patch, "color": cor}
        self.termo_rows.append(data)

    def _reindex_rows(self) -> None:
        for i, data in enumerate(self.termo_rows):
            data["frame"].grid(row=i // 4, column=i % 4, sticky="ew", pady=2, padx=(0, 6))
        if self.scroll_canvas:
            self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _escolher_pdf(self) -> None:
        path = filedialog.askopenfilename(
            title=t("dialog.select_pdf_title"),
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")],
        )
        if path:
            self.pdf_path = path
            nome = os.path.basename(path)
            if len(nome) > 40:
                nome = nome[:37] + "..."
            self.pdf_label_var.set(nome)
            self.root.update_idletasks()

    def _gerar(self) -> None:
        if not self.pdf_path or not os.path.isfile(self.pdf_path):
            messagebox.showerror(t("error.title"), t("error.no_pdf"))
            return

        pares = []
        for data in self.termo_rows:
            termo = data["entry"].get().strip()
            if termo:
                pares.append((termo, data["color"]))

        if not pares:
            messagebox.showerror(t("error.title"), t("error.no_term"))
            return

        termos = [t for t, _ in pares]
        try:
            n = contar_ocorrencias_multi(self.pdf_path, termos)
        except Exception as e:
            messagebox.showerror(t("error.title"), t("error.read_pdf", e=str(e)))
            return
        if n == 0:
            messagebox.showwarning(
                t("warn.no_occurrence_title"),
                t("warn.no_occurrence_body"),
            )
            return

        nome_base = os.path.splitext(os.path.basename(self.pdf_path))[0]
        dir_base = os.path.dirname(self.pdf_path)
        sugestao = os.path.join(dir_base, f"{nome_base}_marcado.pdf")

        out_path = filedialog.asksaveasfilename(
            title=t("dialog.save_title"),
            defaultextension=".pdf",
            initialfile=os.path.basename(sugestao),
            initialdir=dir_base,
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")],
        )
        if not out_path:
            return

        try:
            destacar_pdf_multi(self.pdf_path, out_path, pares)
            messagebox.showinfo(t("info.done_title"), t("info.done_body", path=out_path))
        except Exception as e:
            messagebox.showerror(t("error.title"), t("error.process", e=str(e)))

    def run(self) -> None:
        self.root.mainloop()
