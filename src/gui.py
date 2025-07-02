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

# ============================ janela de estatísticas =================================
class StatsWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk, csv_path: Path):
        super().__init__(parent)
        self.title("Estatísticas do Resultado")
        self.geometry("420x280")
        self.resizable(False, False)
        try:
            df = pd.read_csv(csv_path, sep=';', dtype=str)
            nota = df["nota final"].str.replace(",", ".", regex=False).astype(float)
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha ao ler CSV:\n{exc}")
            self.destroy()
            return
        stats = {
            "Registros totais": len(df),
            "Nota média": f"{nota.mean():.2f}",
            "Desvio padrão": f"{nota.std(ddof=0):.2f}",
            "Nota mínima": f"{nota.min():.2f}",
            "Nota máxima": f"{nota.max():.2f}",
            "Nota ≥ 5,0": f"{(nota >= 5).mean() * 100:.1f}%",
        }
        frm = ttk.Frame(self, padding=20)
        frm.pack(expand=True, fill="both")
        for i, (k, v) in enumerate(stats.items()):
            ttk.Label(frm, text=f"{k}:", font=(parent.font_family, 15, "bold")).grid(row=i, column=0, sticky="w", pady=3)
            ttk.Label(frm, text=v, font=(parent.font_family, 15)).grid(row=i, column=1, sticky="w", pady=3)

# ============================ GUI principal ==========================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Comparação de Registros")
        self.geometry("860x460")
        self.resizable(False, False)
        ttk.Style().theme_use("clam")

        fonts = tkfont.families()
        self.font_family = (
            "Segoe UI Emoji"
            if "Segoe UI Emoji" in fonts
            else ("Noto Color Emoji" if "Noto Color Emoji" in fonts else "Segoe UI")
        )
        base_size = 15
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
        self._build()

    def _build_fields(self):
        ttk.Label(self.frm_campos, text="Referência").grid(row=0, column=1, padx=5)
        ttk.Label(self.frm_campos, text="Comparação").grid(row=0, column=2, padx=5)
        btn_add = ttk.Button(self.frm_campos, text="➕", width=3, command=self._add_field)
        btn_add.grid(row=0, column=3)
        ToolTip(btn_add, "Adicionar")
        self.boxes.clear()
        self._add_field()

    def _add_field(self):
        row = len(self.boxes) + 1
        lbl = ttk.Label(self.frm_campos, text=f"Variável {row}:")
        cb1 = ttk.Combobox(self.frm_campos, state="readonly", width=20)
        cb2 = ttk.Combobox(self.frm_campos, state="readonly", width=20)
        btn = ttk.Button(self.frm_campos, text="🗑", width=3)
        lbl.grid(row=row, column=0, sticky="w")
        cb1.grid(row=row, column=1, padx=5, pady=2)
        cb2.grid(row=row, column=2, padx=5, pady=2)
        btn.grid(row=row, column=3)
        ToolTip(btn, "Remover")
        cb1.bind("<<ComboboxSelected>>", lambda e, a=cb1, b=cb2: self._sync_pair(a, b))
        widgets = {"lbl": lbl, "cb1": cb1, "cb2": cb2, "btn": btn}
        btn.config(command=lambda w=widgets: self._del_field(w))
        self.boxes.append(widgets)

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

    def _load_header(self):
        if not self.filepath:
            return
        try:
            df = pd.read_csv(self.filepath, sep='|', nrows=0)
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
        for widgets in self.boxes:
            cb1 = widgets["cb1"]
            cb2 = widgets["cb2"]
            cb1['values'] = left_names
            cb2['values'] = right_names
            if left_names:
                cb1.current(0)
            if right_names:
                cb2.current(0)

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

                # arquivo entrada / saída
        ttk.Label(self, text="Arquivo de entrada:").place(x=10, y=230)
        self.e_in = ttk.Entry(self, width=55)
        self.e_in.place(x=150, y=227)
        btn_open = ttk.Button(self, text="Procurar", command=self._abrir_csv)
        btn_open.place(x=650, y=223)
        ToolTip(btn_open, "Ctrl+O")

        ttk.Label(self, text="Arquivo de saída (base):").place(x=10, y=260)
        self.e_out = ttk.Entry(self, width=30)
        self.e_out.insert(0, "saida")
        self.e_out.place(x=200, y=257)

        # Amostra
        ttk.Label(self, text="Tam. amostra:").place(x=10, y=300)
        self.e_size = ttk.Entry(self, width=8)
        self.e_size.insert(0, "100")
        self.e_size.place(x=100, y=300)
        btn_sample = ttk.Button(self, text="Gerar amostra", command=self._gera_amostra)
        btn_sample.place(x=180, y=297)
        ToolTip(btn_sample, "Ctrl+G")

        # Botões principais
        btn_comp = ttk.Button(self, text="Comparar", command=self._comparar)
        btn_comp.place(x=650, y=252)
        ToolTip(btn_comp, "Ctrl+C")
        btn_stats = ttk.Button(self, text="Estatísticas", command=self._mostrar_stats)
        btn_stats.place(x=650, y=281)
        ToolTip(btn_stats, "Ctrl+E")
        btn_reset = ttk.Button(self, text="Reiniciar", command=self._reset_vars)
        btn_reset.place(x=650, y=310)
        ToolTip(btn_reset, "F5")
        btn_help = ttk.Button(self, text="Ajuda", command=self._show_help)
        btn_help.place(x=650, y=339)
        ToolTip(btn_help, "F1")

        # Atalhos de teclado
        self.bind("<Control-o>", lambda e: self._abrir_csv())
        self.bind("<Control-g>", lambda e: self._gera_amostra())
        self.bind("<Control-c>", lambda e: self._comparar())
        self.bind("<Control-e>", lambda e: self._mostrar_stats())
        self.bind("<F1>", lambda e: self._show_help())
        self.bind("<F5>", lambda e: self._reset_vars())

    # ---------------- callbacks ----------------
    def _abrir_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if path:
            self.filepath = path
            self.e_in.delete(0, tk.END)
            self.e_in.insert(0, Path(path).name)
            self._load_header()

    def _reset_vars(self):
        for widget in self.frm_campos.winfo_children():
            widget.destroy()
        self.boxes.clear()
        self._build_fields()
        self._load_header()

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
                "Ctrl+E – Estatísticas\n"
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
                generate_sample(n, Path(dest), progress_cb=lambda p: dlg.put(p))
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
            pares.append((idx1, idx2, tipo, c1))
        dlg = ProgressDialog(self, "Comparando registros")
        dlg.put(-1, "Processando…")
        def worker():
            try:
                cr.processar_generico(self.filepath, out_base, pares)
                self.output_csv = f"{out_base}.csv"
                dlg.put(100, "Concluído")
                messagebox.showinfo("Pronto", "Comparação concluída.")
            except Exception as exc:
                dlg.destroy()
                messagebox.showerror("Erro", f"Falha no processamento: {exc}")
        threading.Thread(target=worker, daemon=True).start()

    def _mostrar_stats(self):
        path = self.output_csv if os.path.isfile(self.output_csv) else filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if path:
            StatsWindow(self, Path(path))

if __name__ == "__main__":
    App().mainloop()
