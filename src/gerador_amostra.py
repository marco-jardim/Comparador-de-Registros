import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

# Lists
male_first = ["João", "Pedro", "Lucas", "Gabriel", "Marcos", "Felipe", "Rafael", "Carlos", "Bruno", "Ricardo"]
female_first = ["Maria", "Ana", "Beatriz", "Larissa", "Juliana", "Camila", "Patrícia", "Aline", "Fernanda", "Vanessa"]
last_names = ["Silva", "Souza", "Oliveira", "Santos", "Pereira", "Lima", "Costa", "Gomes",
              "Ribeiro", "Almeida", "Nunes", "Carvalho", "Araujo", "Rodrigues", "Barbosa"]

def random_name(gender: str = "any") -> str:
    if gender == "female":
        first = random.choice(female_first)
    elif gender == "male":
        first = random.choice(male_first)
    else:
        first = random.choice(female_first + male_first)
    return f"{first} {random.choice(last_names)}"

def random_date(start_year=1980, end_year=2010) -> str:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    date = start + timedelta(days=random.randint(0, (end - start).days))
    return date.strftime("%Y%m%d")

# Columns A..P
columns = [chr(ord('A') + i) for i in range(16)]  # 16 columns (A-P)
rows = []

for _ in range(100):
    row = {col: "" for col in columns}
    row['J'] = random_name()               # Nome 1       (col J = 9)
    row['N'] = random_name()               # Nome 2       (col N = 13)
    row['K'] = random_name("female")       # Mãe 1        (col K =10)
    row['O'] = random_name("female")       # Mãe 2        (col O =14)
    row['L'] = random_date()               # Nasc 1       (col L =11)
    row['P'] = random_date()               # Nasc 2       (col P =15)
    rows.append(row)

df = pd.DataFrame(rows, columns=columns)

file_path = Path("./amostra.csv")
df.to_csv(file_path, sep=';', index=False)

print(f"Sample data generated and saved to {file_path}")