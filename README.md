# BankCorp RPA Register

Automated bank transaction registration bot built with Python + Playwright.

## What It Does

Reads a CSV file containing 50 bank transactions and automatically registers
each one into the BankCorp corporate portal via browser automation. Eliminates
manual data entry for SEPA, SWIFT, SIBS, and MB WAY transactions.

## Objective

Replace repetitive manual form filling with a reliable, single-click automation
that reads transaction data from a spreadsheet and registers all entries into
the web system without human intervention.

## How to Run

```bash
pip install playwright pandas python-dotenv
playwright install chromium
python main.py
```

## Project Structure

```
BankCorp Register/
├── main.py                    # Entry point — orchestrates the full workflow
├── README.md                  # This file
├── data/
│   ├── .env                   # Credentials (gitignored)
│   └── transacoes.csv         # 50 transactions (account, name, amount, type)
├── src/
│   ├── __init__.py            # Package initializer
│   ├── bank_corp.py           # BankCorp class — site interactions (login, form fill)
│   ├── browser.py             # BrowserManager class — Playwright browser lifecycle
│   ├── config.py              # ConfigData class — environment variables loader
│   └── extract_data.py        # CSV data extraction — reads transactions into list[dict]
└── test/
    └── test_extract_data.py   # Manual test for data extraction output
```
