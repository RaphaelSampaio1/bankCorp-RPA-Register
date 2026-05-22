import pandas as pd


def extract_csv_data(filepath: str) -> list[dict]:
    df = pd.read_csv(filepath)

    df= df.rename(columns={
        "Número da Conta": "account_number",
        "Nome do Favorecido": "customer_name",
        "Valor (€)": "amount",
        "Tipo": "transaction_type"
    })

    return df.to_dict(orient="records")