from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
import threading, queue, time, os
import pandas as pd

import comparaRegistros as cr  # módulo já existente
# ===================== utilidades de geração de dados sintéticos =================
# Funções de geração em gerador_amostra.py

from gerador_amostra import generate_sample


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
        self.protocol("WM_DELETE_WINDOW", lambda: None)  # desabilita fechar
        ttk.Label(self, text=title, font=("Segoe UI", 10, "bold")).pack(pady=10)
        self.pb = ttk.Progressbar(self, orient="horizontal", length=350, mode="determinate")
        self.pb.pack(pady=5)
        self.lbl_info = ttk.Label(self, text="0%")
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
            ttk.Label(frm, text=f"{k}:", font=("Segoe UI", 10, "bold")).grid(row=i, column=0, sticky="w", pady=3)
            ttk.Label(frm, text=v, font=("Segoe UI", 10)).grid(row=i, column=1, sticky="w", pady=3)

# ============================ GUI principal ==========================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Comparação de Registros")
        self.geometry("840x440")
        self.resizable(False, False)
        self.filepath: str = ""
        self.output_csv: str = ""
        self.n_vars = simpledialog.askinteger(
            "Variáveis", "Quantas variáveis deseja comparar?", minvalue=1, parent=self
        ) or 1
        self.left_map: dict[str, tuple[int, str]] = {}
        self.right_map: dict[str, tuple[int, str]] = {}
        self._build()

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
            if prefix == 'R':
                self.left_map[nome] = (idx, tipo)
                left_names.append(nome)
            elif prefix == 'C':
                self.right_map[nome] = (idx, tipo)
                right_names.append(nome)
        for cb1, cb2 in self.boxes:
            cb1['values'] = left_names
            cb2['values'] = right_names
            if left_names:
                cb1.current(0)
            if right_names:
                cb2.current(0)

    # -------- build interface --------
    def _build(self):
        ttk.Label(
            self,
            text="Selecione as colunas para comparação",
            font=("Segoe UI", 10, "bold"),
        ).place(x=10, y=5)

        self.frm_campos = ttk.Frame(self)
        self.frm_campos.place(x=10, y=30)
        ttk.Label(self.frm_campos, text="Registro 1").grid(row=0, column=1, padx=5)
        ttk.Label(self.frm_campos, text="Registro 2").grid(row=0, column=2, padx=5)
        self.boxes = []
        for i in range(self.n_vars):
            ttk.Label(self.frm_campos, text=f"Variável {i+1}:").grid(row=i+1, column=0, sticky="w")
            cb1 = ttk.Combobox(self.frm_campos, state="readonly", width=20)
            cb2 = ttk.Combobox(self.frm_campos, state="readonly", width=20)
            cb1.grid(row=i+1, column=1, padx=5, pady=2)
            cb2.grid(row=i+1, column=2, padx=5, pady=2)
            self.boxes.append((cb1, cb2))

                # arquivo entrada / saída
        ttk.Label(self, text="Arquivo de entrada:").place(x=10, y=230)
        self.e_in = ttk.Entry(self, width=55)
        self.e_in.place(x=150, y=227)
        ttk.Button(self, text="Procurar", command=self._abrir_csv).place(x=650, y=223)

        ttk.Label(self, text="Arquivo de saída (base):").place(x=10, y=260)
        self.e_out = ttk.Entry(self, width=30)
        self.e_out.insert(0, "saida")
        self.e_out.place(x=200, y=257)

        # Amostra
        ttk.Label(self, text="Tam. amostra:").place(x=10, y=300)
        self.e_size = ttk.Entry(self, width=8)
        self.e_size.insert(0, "100")
        self.e_size.place(x=100, y=300)
        ttk.Button(self, text="Gerar amostra", command=self._gera_amostra).place(x=180, y=297)

        # Botões principais
        ttk.Button(self, text="Comparar", command=self._comparar).place(x=650, y=252)
        ttk.Button(self, text="Estatísticas", command=self._mostrar_stats).place(x=650, y=281)

    # ---------------- callbacks ----------------
    def _abrir_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if path:
            self.filepath = path
            self.e_in.delete(0, tk.END)
            self.e_in.insert(0, Path(path).name)
            self._load_header()

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
        for cb1, cb2 in self.boxes:
            c1 = cb1.get()
            c2 = cb2.get()
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
