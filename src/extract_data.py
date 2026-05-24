"""
Data extraction module — reads CSV files and returns transactions as a list of dicts.

Each transaction dict contains the keys: account_number, customer_name, amount,
and transaction_type — ready to be consumed by BankCorp.register_transactions().
"""

import pandas as pd


def extract_csv_data(filepath: str) -> list[dict]:
    """
    Read a CSV file of bank transactions and return a list of dicts.

    Renames Portuguese column headers to English keys:
        - "Número da Conta"      → "account_number"
        - "Nome do Favorecido"   → "customer_name"
        - "Valor (€)"            → "amount"
        - "Tipo"                 → "transaction_type"

    Args:
        filepath (str): Path to the CSV file (e.g., "data/transacoes.csv").

    Returns:
        list[dict]: List of transaction dicts, one per row.
    """
    df = pd.read_csv(filepath)

    df = df.rename(columns={
        "Número da Conta": "account_number",
        "Nome do Favorecido": "customer_name",
        "Valor (€)": "amount",
        "Tipo": "transaction_type"
    })

    return df.to_dict(orient="records")
