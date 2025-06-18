from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading, queue, time, os, random
from datetime import datetime, timedelta
import pandas as pd

import comparaRegistros as cr  # módulo já existente

# ===================== utilidades de geração de dados sintéticos =====================
random.seed(42)
MALE_FIRST = [
    "João", "Pedro", "Lucas", "Gabriel", "Marcos", "Felipe", "Rafael", "Carlos", "Bruno", "Ricardo",
    "Alex", "Thiago", "Daniel", "Gustavo", "Leonardo", "Matheus", "André", "Diego", "Eduardo", "Henrique",
]
FEMALE_FIRST = [
    "Maria", "Ana", "Beatriz", "Larissa", "Juliana", "Camila", "Patrícia", "Aline", "Fernanda", "Vanessa",
    "Luana", "Carolina", "Helena", "Isabela", "Eduarda", "Gabriela", "Bianca", "Patrícia", "Renata", "Tatiana",
]
LAST_NAMES = [
    "Silva", "Souza", "Oliveira", "Santos", "Pereira", "Lima", "Costa", "Gomes", "Ribeiro", "Almeida",
    "Nunes", "Carvalho", "Araujo", "Rodrigues", "Barbosa", "Moura", "Ferreira", "Medeiros", "Martins", "Duarte",
]
TYPO_FUNCS = [
    lambda s: s[:-1] if len(s) > 3 else s,
    lambda s: s + s[-1] if len(s) > 3 else s,
    lambda s: s.replace("a", "á", 1) if "a" in s else s,
    lambda s: s.replace("e", "3", 1) if "e" in s else s,
    lambda s: s[1:] + s[0] if len(s) > 3 else s,
]


def _random_name(gender: str = "any") -> str:
    pool = FEMALE_FIRST + MALE_FIRST if gender == "any" else (
        FEMALE_FIRST if gender == "female" else MALE_FIRST)
    return f"{random.choice(pool)} {random.choice(LAST_NAMES)}"


def _random_date(start_year: int = 1980, end_year: int = 2010) -> str:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return (start + timedelta(days=random.randint(0, (end - start).days))).strftime("%Y%m%d")


def _maybe_typo(name: str, prob: float = 0.15) -> str:
    if random.random() < prob:
        func = random.choice(TYPO_FUNCS)
        return " ".join(func(p) if random.random() < 0.5 else p for p in name.split())
    return name


def generate_sample(n: int, out_path: Path, progress_cb=None) -> None:
    cols = [chr(ord('A') + i) for i in range(16)]  # A‑P
    rows = []
    for i in range(n):
        r = {c: "" for c in cols}
        r['J'] = _maybe_typo(_random_name())
        r['N'] = _maybe_typo(_random_name())
        r['K'] = _maybe_typo(_random_name("female"))
        r['O'] = _maybe_typo(_random_name("female"))
        r['L'] = _random_date()
        r['P'] = _random_date()
        rows.append(r)
        if progress_cb and (i + 1) % max(1, n // 100) == 0:
            progress_cb(int((i + 1) / n * 100))
    pd.DataFrame(rows, columns=cols).to_csv(out_path, sep=';', index=False)

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
    _LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    _DEFAULT_IDX = [9, 10, 11, 13, 14, 15]

    def __init__(self):
        super().__init__()
        self.title("Comparação de Registros")
        self.geometry("840x440")
        self.resizable(False, False)
        self.filepath: str = ""
        self.output_csv: str = ""
        self._build()

    # -------- build interface --------
    def _build(self):
        ttk.Label(self, text="Indique as colunas referentes aos seguintes dados:", font=("Segoe UI", 10, "bold")).place(x=10, y=5)
        campos = (
            ("Nome 1", 30, 10), ("Nome Mãe 1", 86, 10), ("Nascimento 1", 142, 10),
            ("Nome 2", 30, 370), ("Nome Mãe 2", 86, 370), ("Nascimento 2", 142, 370),
        )
        self.boxes = []
        for i, (lbl, y, x) in enumerate(campos):
            ttk.Label(self, text=lbl+":").place(x=x, y=y)
            cb = ttk.Combobox(self, values=self._LETTERS, width=3, state="readonly")
            cb.current(self._DEFAULT_IDX[i])
            cb.place(x=x, y=y+25)
            self.boxes.append(cb)

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
        idxs = tuple(cb.current() for cb in self.boxes)
        dlg = ProgressDialog(self, "Comparando registros")
        dlg.put(-1, "Processando…")  # modo indeterminate
        def worker():
            try:
                cr.processar(self.filepath, out_base, idxs)
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
