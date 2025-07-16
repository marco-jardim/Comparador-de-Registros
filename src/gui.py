from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkfont
from pathlib import Path
import threading, queue, time, os
import pandas as pd

import comparaRegistros as cr  # módulo já existente
# ===================== utilidades de geração de dados sintéticos =================
# Funções de geração em gerador_amostra.py

from gerador_amostra import generate_sample
import csv

# Emojis para tipos de variáveis
EMOJIS = {"C": "🔤", "D": "📅", "N": "🔢"}


class ToolTip:
    def __init__(self, widget: tk.Widget, text: str):
        self.widget = widget
        self.text = text
        self.tipwindow: tk.Toplevel | None = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.geometry(f"+{x}+{y}")
        font_family = self.widget.winfo_toplevel().font_family
        tk.Label(tw, text=self.text, background="#ffffe0", relief="solid", borderwidth=1,
                 font=(font_family, 12)).pack()

    def hide(self, _=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


# ============================ Barra de progresso modal ===============================
class ProgressDialog(tk.Toplevel):
    """Exibe progresso determinate ou indeterminate.
    Para atualizar progresso: use queue e método update_from_queue."""
    def __init__(self, parent: tk.Tk, title: str = "Progresso"):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x120")
        self.resizable(False, False)
        self.grab_set()
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        self.protocol("WM_DELETE_WINDOW", lambda: None)  # desabilita fechar
        ttk.Label(self, text=title, font=(parent.font_family, 15, "bold")).pack(pady=10)
        self.pb = ttk.Progressbar(self, orient="horizontal", length=350, mode="determinate")
        self.pb.pack(pady=5)
        self.lbl_info = ttk.Label(self, text="0%", font=(parent.font_family, 15))
        self.lbl_info.pack()
        self.start_time = time.time()
        self.queue: queue.Queue[tuple[int, str]] = queue.Queue()
        self.after(100, self._poll)

    def _poll(self):
        try:
            while True:
                pct, msg = self.queue.get_nowait()
                if pct < 0:
                    # indeterminate update message only
                    self.pb.config(mode="indeterminate")
                    if not self.pb['value']:
                        self.pb.start(5)
                    self.lbl_info.config(text=msg)
                else:
                    if self.pb['mode'] != "determinate":
                        self.pb.stop()
                        self.pb.config(mode="determinate")
                    self.pb['value'] = pct
                    eta = (time.time() - self.start_time) * (100 - pct) / pct if pct else 0
                    self.lbl_info.config(text=f"{pct}%  • ETA {int(eta)}s  {msg}")
                    if pct >= 100:
                        self.destroy()
                        return
        except queue.Empty:
            pass
        self.after(100, self._poll)

    def put(self, pct: int, msg: str = ""):
        self.queue.put((pct, msg))
# ============================ GUI principal ==========================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Comparação de Registros")
        self.geometry("900x520")
        self.resizable(False, False)

        default_font = tkfont.nametofont("TkDefaultFont")
        self.font_family = default_font.actual("family")
        base_size = int(default_font.cget("size") * 1.5)
        default_font.configure(size=base_size)
        ttk.Style().configure(".", font=(self.font_family, base_size))
        self.option_add("*Font", (self.font_family, base_size))

        self.filepath: str = ""
        self.output_csv: str = ""
        self.left_map: dict[str, tuple[int, str]] = {}
        self.right_map: dict[str, tuple[int, str]] = {}
        self.left_labels: dict[str, str] = {}
        self.right_labels: dict[str, str] = {}
        self.label_to_left: dict[str, str] = {}
        self.label_to_right: dict[str, str] = {}
        self.boxes: list[dict[str, any]] = []
        self.openreclink_format = tk.BooleanVar(value=True)
        self.sep_var = tk.StringVar()
        self._set_default_sep()
        self._build()

    def _set_default_sep(self) -> None:
        """Atualiza ``sep_var`` conforme o formato escolhido."""
        self.sep_var.set("|" if self.openreclink_format.get() else ",")

    def _on_format_toggle(self) -> None:
        """Callback para alternar o formato e atualizar o separador."""
        self._set_default_sep()
        self._load_header()
        self._update_tipo_widgets()

    def _sep(self) -> str:
        """Return the column separator chosen by the user."""
        return self.sep_var.get()

    def _guess_sep(self, path: str) -> str:
        """Detect a likely column separator for ``path``."""
        try:
            with open(path, newline="") as fh:
                sample = fh.read(2048)
            dialect = csv.Sniffer().sniff(sample, [",", "|", ";", "\t"])
            return dialect.delimiter
        except Exception:
            return self.sep_var.get()

    def _build_fields(self):
        ttk.Label(self.frm_campos, text="Referência").grid(row=0, column=1, padx=5)
        ttk.Label(self.frm_campos, text="Comparação").grid(row=0, column=2, padx=5)
        self.lbl_tipo = ttk.Label(self.frm_campos, text="Tipo")
        if not self.openreclink_format.get():
            self.lbl_tipo.grid(row=0, column=3, padx=5)
        btn_add = ttk.Button(self.frm_campos, text="➕", width=3, command=self._add_field)
        btn_add.grid(row=0, column=4)
        ToolTip(btn_add, "Adicionar")
        self.boxes.clear()
        self._add_field()
        self._update_tipo_widgets()

    def _update_tipo_widgets(self) -> None:
        show = not self.openreclink_format.get()
        if show:
            self.lbl_tipo.grid(row=0, column=3, padx=5)
        else:
            self.lbl_tipo.grid_remove()
        for i, widgets in enumerate(self.boxes, start=1):
            if show:
                widgets["frm_tipo"].grid(row=i, column=3, padx=5)
                widgets["btn"].grid_configure(column=4)
            else:
                widgets["frm_tipo"].grid_remove()
                widgets["btn"].grid_configure(column=3)

    def _add_field(self):
        row = len(self.boxes) + 1
        lbl = ttk.Label(self.frm_campos, text=f"Variável {row}:")
        cb1 = ttk.Combobox(self.frm_campos, state="readonly", width=20)
        cb2 = ttk.Combobox(self.frm_campos, state="readonly", width=20)
        tipo_var = tk.StringVar(value="C")
        frm_tipo = ttk.Frame(self.frm_campos)
        ttk.Radiobutton(frm_tipo, text="Txt", variable=tipo_var, value="C").grid(row=0, column=0)
        ttk.Radiobutton(frm_tipo, text="Nome", variable=tipo_var, value="N").grid(row=0, column=1)
        ttk.Radiobutton(frm_tipo, text="Data", variable=tipo_var, value="D").grid(row=0, column=2)
        btn = ttk.Button(self.frm_campos, text="🗑", width=3)
        lbl.grid(row=row, column=0, sticky="w")
        cb1.grid(row=row, column=1, padx=5, pady=2)
        cb2.grid(row=row, column=2, padx=5, pady=2)
        frm_tipo.grid(row=row, column=3, padx=5)
        btn.grid(row=row, column=4)
        ToolTip(btn, "Remover")
        cb1.bind("<<ComboboxSelected>>", lambda e, a=cb1, b=cb2: self._sync_pair(a, b))
        widgets = {"lbl": lbl, "cb1": cb1, "cb2": cb2, "btn": btn,
                   "tipo_var": tipo_var, "frm_tipo": frm_tipo}
        btn.config(command=lambda w=widgets: self._del_field(w))
        self.boxes.append(widgets)
        self._load_header()
        self._update_tipo_widgets()

    def _del_field(self, widgets):
        widgets["lbl"].destroy()
        widgets["cb1"].destroy()
        widgets["cb2"].destroy()
        widgets["btn"].destroy()
        self.boxes.remove(widgets)
        for i, w in enumerate(self.boxes, start=1):
            w["lbl"].config(text=f"Variável {i}:")
            for widget in w.values():
                widget.grid_configure(row=i)
        self._update_tipo_widgets()

    def _load_header(self):
        if not self.filepath:
            return
        try:
            df = pd.read_csv(self.filepath, sep=self._sep(), nrows=0)
        except Exception as exc:
            messagebox.showerror('Erro', f'Falha ao ler CSV:\n{exc}')
            return
        self.left_map.clear()
        self.right_map.clear()
        self.left_labels.clear()
        self.right_labels.clear()
        self.label_to_left.clear()
        self.label_to_right.clear()
        left_names: list[str] = []
        right_names: list[str] = []
        use_openrl = self.openreclink_format.get()
        if use_openrl and not self._is_openreclink_header(df.columns):
            use_openrl = False
        if use_openrl:
            for idx, col in enumerate(df.columns):
                parts = col.split(',')
                base = parts[0]
                tipo = parts[1] if len(parts) > 1 else 'C'
                if '_' in base:
                    prefix, nome = base.split('_', 1)
                else:
                    prefix, nome = base[0], base[1:]
                emoji = EMOJIS.get(tipo.upper(), '')
                label = f"{emoji + ' ' if emoji else ''}{nome}"
                if prefix == 'R':
                    self.left_map[nome] = (idx, tipo)
                    self.left_labels[nome] = label
                    self.label_to_left[label] = nome
                    left_names.append(label)
                elif prefix == 'C':
                    self.right_map[nome] = (idx, tipo)
                    self.right_labels[nome] = label
                    self.label_to_right[label] = nome
                    right_names.append(label)
        else:
            for idx, col in enumerate(df.columns):
                nome = col.strip()
                tipo = 'D' if any(k in nome.lower() for k in ('data', 'nasc', 'dt')) else 'C'
                label = f"{EMOJIS.get(tipo, '') + ' ' if EMOJIS.get(tipo, '') else ''}{nome}"
                self.left_map[nome] = (idx, tipo)
                self.right_map[nome] = (idx, tipo)
                self.left_labels[nome] = label
                self.right_labels[nome] = label
                self.label_to_left[label] = nome
                self.label_to_right[label] = nome
                left_names.append(label)
                right_names.append(label)
        old_selections = [
            (w["cb1"].get(), w["cb2"].get()) for w in self.boxes
        ]
        for widgets, (old_l, old_r) in zip(self.boxes, old_selections):
            cb1 = widgets["cb1"]
            cb2 = widgets["cb2"]
            cb1['values'] = left_names
            cb2['values'] = right_names
            cb1.set(old_l if old_l in left_names else "")
            cb2.set(old_r if old_r in right_names else "")

    def _is_openreclink_header(self, cols: list[str]) -> bool:
        """Return True if all columns start with R_ or C prefix."""
        for col in cols:
            base = col.split(',')[0]
            if '_' in base:
                prefix = base.split('_', 1)[0]
            else:
                prefix = base[:1]
            if prefix not in ('R', 'C'):
                return False
        return True

    def _sync_pair(self, cb_left: ttk.Combobox, cb_right: ttk.Combobox) -> None:
        nome = self.label_to_left.get(cb_left.get(), cb_left.get())
        if nome in self.right_labels:
            cb_right.set(self.right_labels[nome])

    # -------- build interface --------
    def _build(self):
        ttk.Label(
            self,
            text="Selecione as colunas para comparação",
            font=(self.font_family, 15, "bold"),
        ).place(x=10, y=5)

        self.frm_campos = ttk.Frame(self)
        self.frm_campos.place(x=10, y=30)
        self._build_fields()

        chk = ttk.Checkbutton(
            self,
            text="Formato OpenRecLink",
            variable=self.openreclink_format,
            command=self._on_format_toggle,
        )
        chk.place(x=650, y=210)
        ToolTip(chk, "Desmarque para cabeçalho simples")

        ttk.Label(self, text="Delimitador:").place(x=640, y=140)
        self.e_sep = ttk.Entry(self, textvariable=self.sep_var, width=6)
        self.e_sep.place(x=740, y=137)

        # arquivo entrada / saída
        ttk.Label(self, text="Arquivo de entrada:").place(x=10, y=250)
        self.e_in = ttk.Entry(self, width=30)
        self.e_in.place(x=200, y=247)
        btn_open = ttk.Button(self, text="Abrir", command=self._abrir_csv)
        btn_open.place(x=650, y=243)
        ToolTip(btn_open, "Ctrl+O")

        ttk.Label(self, text="Arquivo de saída (base):").place(x=10, y=280)
        self.e_out = ttk.Entry(self, width=30)
        self.e_out.insert(0, "saida")
        self.e_out.place(x=200, y=277)

        # Amostra
        ttk.Label(self, text="Tamanho da amostra:").place(x=10, y=325)
        self.e_size = ttk.Entry(self, width=8)
        self.e_size.insert(0, "100")
        self.e_size.place(x=200, y=325)
        btn_sample = ttk.Button(self, text="Gerar amostra", command=self._gera_amostra)
        btn_sample.place(x=290, y=322)
        ToolTip(btn_sample, "Ctrl+G")

        # Botões principais
        btn_comp = ttk.Button(self, text="Comparar", command=self._comparar)
        btn_comp.place(x=650, y=272)
        ToolTip(btn_comp, "Ctrl+C")
        btn_reset = ttk.Button(self, text="Reiniciar", command=self._reset_vars)
        btn_reset.place(x=650, y=330)
        ToolTip(btn_reset, "F5")
        btn_help = ttk.Button(self, text="Ajuda", command=self._show_help)
        btn_help.place(x=650, y=359)
        ToolTip(btn_help, "F1")

        # Atalhos de teclado
        self.bind("<Control-o>", lambda e: self._abrir_csv())
        self.bind("<Control-g>", lambda e: self._gera_amostra())
        self.bind("<Control-c>", lambda e: self._comparar())
        self.bind("<F1>", lambda e: self._show_help())
        self.bind("<F5>", lambda e: self._reset_vars())

    # ---------------- callbacks ----------------
    def _abrir_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if path:
            self.filepath = path
            self.e_in.delete(0, tk.END)
            self.e_in.insert(0, Path(path).name)
            self.sep_var.set(self._guess_sep(path))
            self._load_header()
            self._update_tipo_widgets()

    def _reset_vars(self):
        for widget in self.frm_campos.winfo_children():
            widget.destroy()
        self.boxes.clear()
        self._build_fields()
        self._load_header()
        self._set_default_sep()
        self._update_tipo_widgets()

    def _show_help(self):
        help_win = tk.Toplevel(self)
        help_win.title("Ajuda")
        help_win.geometry("500x300")
        ttk.Label(
            help_win,
            text=(
                "1. Abra ou gere um CSV.\n"
                "2. Escolha as colunas de referência e comparação.\n"
                "3. Clique em Comparar para gerar o resultado.\n\n"
                "Atalhos:\n"
                "Ctrl+O – Abrir CSV\n"
                "Ctrl+G – Gerar amostra\n"
                "Ctrl+C – Comparar\n"
                "F5 – Reiniciar\n"
                "F1 – Ajuda"
            ),
            justify="left",
            padding=10,
        ).pack(fill="both", expand=True)

    def _gera_amostra(self):
        try:
            n = int(self.e_size.get())
            if n <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Informe um tamanho inteiro positivo.")
            return
        dest = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not dest:
            return
        dlg = ProgressDialog(self, "Gerando amostra")
        def worker():
            try:
                generate_sample(
                    n,
                    Path(dest),
                    sep=self._sep(),
                    progress_cb=lambda p: dlg.put(p),
                )
                dlg.put(100, "Concluído")
                self.filepath = dest
                self.e_in.delete(0, tk.END)
                self.e_in.insert(0, Path(dest).name)
                self._load_header()
                messagebox.showinfo("Ok", f"Amostra criada em {dest}")
            except Exception as e:
                dlg.destroy()
                messagebox.showerror("Erro", f"Falha ao gerar amostra: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def _comparar(self):
        if not self.filepath:
            messagebox.showwarning("Atenção", "Selecione ou gere um arquivo de entrada.")
            return
        out_base = self.e_out.get().strip()
        if not out_base:
            messagebox.showwarning("Atenção", "Informe um nome de saída.")
            return
        pares = []
        for widgets in self.boxes:
            cb1 = widgets["cb1"]
            cb2 = widgets["cb2"]
            c1_label = cb1.get()
            c2_label = cb2.get()
            c1 = self.label_to_left.get(c1_label, c1_label)
            c2 = self.label_to_right.get(c2_label, c2_label)
            if c1 not in self.left_map or c2 not in self.right_map:
                messagebox.showerror("Erro", "Seleção inválida de colunas.")
                return
            idx1, tipo = self.left_map[c1]
            idx2, _ = self.right_map[c2]
            if not self.openreclink_format.get():
                tipo = widgets["tipo_var"].get() or tipo
            pares.append((idx1, idx2, tipo, c1))
        dlg = ProgressDialog(self, "Comparando registros")
        dlg.put(-1, "Processando…")
        def worker():
            try:
                cr.processar_generico(
                    self.filepath,
                    out_base,
                    pares,
                    sep=self._sep(),
                )
                self.output_csv = f"{out_base}.csv"
                dlg.put(100, "Concluído")
                messagebox.showinfo("Pronto", "Comparação concluída.")
            except Exception as exc:
                dlg.destroy()
                messagebox.showerror("Erro", f"Falha no processamento: {exc}")
        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()
