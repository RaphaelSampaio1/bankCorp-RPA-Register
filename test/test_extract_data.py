import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


import src.extract_data as extract_data


data_path = r"data\transacoes.csv"
df = extract_data.extract_csv_data(data_path)

for _ in df[:5]:
    print(_)