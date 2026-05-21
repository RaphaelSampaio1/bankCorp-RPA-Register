# BankCorp Register — Requirements Gathering

---

## 1. PROJECT OVERVIEW

| | |
|---|---|
| **Goal** | Automate the registration of 50 bank transactions from a CSV file into the BankCorp test portal |
| **Tools** | Python 3 + Playwright (sync API) + Pandas + python-dotenv |
| **Expected Output** | A script that logs into the portal, reads `transacoes.csv` line by line, fills in the form, registers each transaction, and generates a success/error log |
| **Target Site** | `https://banco-site-rpa-test.vercel.app/` (static SPA — no backend) |
| **Execution Mode** | Headless=False (visible browser, for development/debugging) |

---

## 2. TARGET SITE ANALYSIS

> The site is a **single-page application** (SPA) with no backend. All logic runs in the browser via JavaScript. No API calls, no real authentication, no network requests. The login `fazerLogin()` always succeeds after an 800ms delay regardless of input.

### 2.1 URL Structure

| Route | Description |
|---|---|
| `/` | Single page — login + dashboard in one HTML |

### 2.2 Login Screen (`#login-screen`)

| Element | Selector | Type | Notes |
|---|---|---|---|
| Username input | `#username` | `<input type="text">` | Not validated — any value works |
| Password input | `#password` | `<input type="password">` | Not validated — any value works |
| Login button | `#btn-login` | `<button>` | Calls `fazerLogin()` — adds 800ms delay, then hides login and shows dashboard |
| After login | `#main-app.hidden` removed | | Login screen gets `hidden` class; dashboard removes `hidden` class |

**Critical:** After login, the button text changes to `"Autenticando..."` during the 800ms delay. The RPA must wait for `#main-app` to become visible (not `hidden`), NOT just wait for `page.wait_for_load_state()`.

### 2.3 Dashboard Navigation

| Tab | Selector | Visible By Default |
|---|---|---|
| Registro de Transações | `#btn-registro` | Yes (active) |
| Consultas | `#btn-consulta` | No (placeholder) |
| Relatórios | `#btn-relatorios` | No (placeholder) |
| Logout | Button with `onclick="location.reload()"` | Yes |

### 2.4 Transaction Registration Form (`#sec-registro`)

| Field | Selector | Type | Required | Notes |
|---|---|---|---|---|
| Número da Conta | `#conta` | `<input type="text">` | Yes | IBAN (e.g., `PT506048363982761533571`) |
| Nome do Favorecido | `#favorecido` | `<input type="text">` | Yes | Beneficiary name |
| Valor (€) | `#valor` | `<input type="number" step="0.01">` | Yes | Decimal number |
| Tipo | `#tipo` | `<select>` | — | Dropdown with 4 options |
| Add button | `#btn-adicionar` | `<button>` | — | Calls `adicionarLinha()` |

### 2.5 Status / Feedback

| Element | Selector | Behavior |
|---|---|---|
| Success message | `#status` | Text: `"Sucesso: Transação registrada."` (green) |
| Error message | `#status` | Text: `"Erro: Preencha todos os campos."` (red) |
| Row status cell | `<td>` (5th) | Text: `"Pendente"` (orange) after insert |

### 2.6 Transaction Table (`#tabelaTransacoes`)

| Column | Index | Example |
|---|---|---|
| Conta (IBAN) | 0 | `PT506048363982761533571` |
| Favorecido | 1 | `Miguel Rodrigues` |
| Valor (€) | 2 | `3345.92` |
| Tipo | 3 | `SEPA` |
| Status | 4 | `Pendente` |

---

## 3. DATA SOURCE ANALYSIS

**File:** `data/transacoes.csv`
**Records:** 50

### 3.1 CSV Schema

| Column | Type | Example |
|---|---|---|
| `Número da Conta` | `string` | `PT506048363982761533571` |
| `Nome do Favorecido` | `string` | `Miguel Rodrigues` |
| `Valor (€)` | `float` | `3345.92` |
| `Tipo` | `string` | `SEPA` |

### 3.2 ⚠️ TYPE MAPPING ISSUE (CSV → Site)

| CSV Value | Site `<option>` | Match? | Action |
|---|---|---|---|
| `SEPA` | `SEPA` | Yes | Use as-is |
| `SWIFT` | `SWIFT` | Yes | Use as-is |
| `SISB` | `SIBS` | **No** | Map `SISB` → `SIBS` |
| `MBWAY` | `MB WAY` | **No** | Map `MBWAY` → `MB WAY` |

This mapping MUST be handled in the extraction logic.

### 3.3 Value Formatting

- The CSV amount is a `float` (e.g., `3345.92`)
- The site input `#valor` accepts a number
- Should be formatted as string with dot separator (e.g., `"3345.92"`)
- No Euro symbol needed (the placeholder says `(€)`, it's cosmetic)

---

## 4. TECHNICAL ARCHITECTURE

### 4.1 Class Diagram

```
BrowserManager (src/browser.py)
├── playwright: sync_playwright
├── context: BrowserContext (persistent, with cookies)
└── page: Page
    ├── __init__(headless, user_data_dir)
    └── close()

BankCorp (src/bankCorp.py)
├── page: Page (from BrowserManager)
├── SITE_URL: str (class constant)
├── TYPE_MAP: dict (class constant)
├── __init__(page: Page)
├── navigate()
├── login(user, password)
├── fill_transaction(data: dict)
├── register_all(transactions: list[dict])
└── close()

extract_csv_data (src/extract_data.py)
├── extract_csv_data(filepath: str) -> list[dict]
└── map_transaction_type(tipo: str) -> str
```

### 4.2 Data Flow

```
main.py
  │
  ├─1. BrowserManager()              → Open Chromium (persistent context)
  │
  ├─2. BankCorp(browser.page)        → Initialize bot with page
  │       ├── navigate(SITE_URL)     → Go to site
  │       └── login(user, pass)      → Authenticate
  │
  ├─3. extract_csv_data(filepath)    → Read CSV, apply type mapping
  │
  ├─4. bank.register_all(data)       → Loop: fill + submit each row
  │       └── fill_transaction(dict) → Fill form fields, click "Adicionar"
  │
  └─5. browser.close()               → Shut down
```

---

## 5. IMPLEMENTATION PLAN (Step by Step)

### 5.1 `src/browser.py` — REFACTOR (Fix type hint + bug)

No functional change needed. Just add type annotation for `self.page` so the IDE can infer the `Page` type.

```python
from playwright.sync_api import sync_playwright, Page, BrowserContext

class BrowserManager:
    def __init__(self, headless: bool = False, user_data_dir: str = "./data/Cookies"):
        self.playwright = sync_playwright().start()
        self.context: BrowserContext = self.playwright.chromium.launch_persistent_context(...)
        self.page: Page = self.context.pages[0] if self.context.pages else self.context.new_page()
```

### 5.2 `src/bankCorp.py` — COMPLETE IMPLEMENTATION

**Step 1:** Fix `__init__` — use lowercase parameter + type hint

```python
from playwright.sync_api import Page

class BankCorp:
    SITE_URL = "https://banco-site-rpa-test.vercel.app/"
    TYPE_MAP = {"SISB": "SIBS", "MBWAY": "MB WAY"}

    def __init__(self, page: Page):
        self.page = page
```

**Step 2:** Refactor `navigate()` — use parameter (or class constant)

```python
def navigate(self):
    self.page.goto(self.SITE_URL, wait_until="domcontentloaded")
```

**Step 3:** Implement `login()`

```python
def login(self, user: str, password: str):
    self.page.fill("#username", user)
    self.page.fill("#password", password)
    self.page.click("#btn-login")
    self.page.wait_for_selector("#main-app:not(.hidden)", timeout=5000)
```

> **ELI5 analogy:** `self.page.fill(...)` is like typing with a robot hand. It clicks the input box and types the text. `wait_for_selector(...)` is like the robot waiting at the door until the dashboard says "come in".

**Step 4:** Implement `fill_transaction()`

```python
def fill_transaction(self, data: dict):
    self.page.fill("#conta", data["conta"])
    self.page.fill("#favorecido", data["favorecido"])
    self.page.fill("#valor", data["valor"])
    self.page.select_option("#tipo", data["tipo"])
    self.page.click("#btn-adicionar")
    self.page.wait_for_selector("#status", timeout=3000)
```

**Step 5:** Implement `register_all()`

```python
def register_all(self, transactions: list[dict]):
    results = []
    for i, t in enumerate(transactions):
        try:
            self.fill_transaction(t)
            results.append({"row": i, "status": "OK", "favorecido": t["favorecido"]})
        except Exception as e:
            results.append({"row": i, "status": "ERROR", "favorecido": t["favorecido"], "error": str(e)})
    return results
```

### 5.3 `src/extract_data.py` — IMPLEMENT

```python
import pandas as pd

TYPE_MAP = {"SISB": "SIBS", "MBWAY": "MB WAY"}

def extract_csv_data(filepath: str) -> list[dict]:
    df = pd.read_csv(filepath)
    transactions = []
    for _, row in df.iterrows():
        tipo = str(row["Tipo"]).strip()
        mapped_tipo = TYPE_MAP.get(tipo, tipo)
        transactions.append({
            "conta": str(row["Número da Conta"]).strip(),
            "favorecido": str(row["Nome do Favorecido"]).strip(),
            "valor": f"{float(row["Valor (€)"]):.2f}",
            "tipo": mapped_tipo
        })
    return transactions
```

### 5.4 `main.py` — ORCHESTRATOR

```python
import os
from dotenv import load_dotenv
from src.browser import BrowserManager
from src.bankCorp import BankCorp
from src.extract_data import extract_csv_data

load_dotenv("data/.env")

def main():
    browser = BrowserManager(headless=False)
    bank = BankCorp(browser.page)

    bank.navigate()
    bank.login(
        user=os.getenv("user"),
        password=os.getenv("password")
    )

    transactions = extract_csv_data("data/transacoes.csv")
    results = bank.register_all(transactions)

    ok = sum(1 for r in results if r["status"] == "OK")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    print(f"\nDone! {ok} OK, {errors} errors.")

    input("Press Enter to finish...")
    browser.close()

if __name__ == "__main__":
    main()
```

---

## 6. ERROR HANDLING STRATEGY

| Scenario | Detection | Action |
|---|---|---|
| Site unreachable | Playwright `goto()` timeout | Log error, retry 2x, then exit |
| Login fails (element not found) | `wait_for_selector()` timeout | Log error, exit |
| Form field not visible | `fill()/select_option()` timeout | Skip this row, log error, continue to next |
| Empty/missing field in CSV | `pd.isna()` check | Skip row, log warning |
| Type not mapped | KeyError on TYPE_MAP | Use original value as fallback |

**Log output format:**

```
[OK]       001 | Miguel Rodrigues        | SEPA   | €3345.92
[ERROR]    002 | João Silva              | SWIFT  | Timeout on #conta
[SKIP]     003 | (empty name)            | —      | Missing data in CSV
```

---

## 7. TESTING & VALIDATION PLAN

### 7.1 Pre-Run Checklist

- [ ] `pip install playwright pandas python-dotenv`
- [ ] `playwright install chromium`
- [ ] `data/.env` exists with user/password
- [ ] `data/transacoes.csv` exists with 50 rows
- [ ] `data/Cookies/` directory exists (for persistent context)

### 7.2 Unit Tests (Pytest)

| Test | File | What it checks |
|---|---|---|
| `test_extract_csv_reads_all_rows()` | `tests/test_extract.py` | 50 records loaded |
| `test_extract_maps_sisb_to_sibs()` | `tests/test_extract.py` | `SISB` → `SIBS` |
| `test_extract_maps_mbway_to_mb_way()` | `tests/test_extract.py` | `MBWAY` → `MB WAY` |
| `test_extract_formats_value()` | `tests/test_extract.py` | `3345.92` stays `"3345.92"` |
| `test_browser_opens_page()` | `tests/test_browser.py` | BrowserManager opens URL |

### 7.3 Manual Validation

1. Run `main.py` with `headless=False`
2. Watch the first 3 transactions register visually
3. Verify the table `#tabelaTransacoes` has rows
4. Check the console output for OK/ERROR counts
5. Verify the status column shows "Pendente" for each row

---

## 8. DEPLOYMENT & SIGN-OFF CHECKLIST

- [ ] All 50 transaction types mapped correctly (SEPA, SWIFT, SIBS, MB WAY)
- [ ] Script runs `headless=True` without errors (production mode)
- [ ] `.env` excluded from git via `.gitignore`
- [ ] `data/Cookies/` excluded from git via `.gitignore`
- [ ] `input("Press Enter to finish...")` at end of script
- [ ] Log output includes row-level status
- [ ] 0 `SKIP` rows in final run
- [ ] Browser closes cleanly after script ends

---

## 9. BLUE PRISM → PYTHON PARALLEL (For Reference)

| Blue Prism Concept | Python Equivalent |
|---|---|
| Process Studio Page | `.py` file (a function/class) |
| Application Modeller | CSS Selectors (`#conta`, `#favorecido`) |
| Wait Stage | `page.wait_for_selector(...)` |
| Write Stage | `page.fill("#conta", value)` |
| Navigate Stage | `page.goto(url)` |
| Decision Stage | `if` / `else` block |
| Exception Stage | `try:` / `except:` block |
| Collection (Data Table) | `pandas DataFrame` → `list[dict]` |
| Environment Variables | `.env` file + `python-dotenv` |
| Logging | `print()` or `logging` module |
| Loop Stage | `for item in list:` |

---

## 10. FILE STRUCTURE (After Implementation)

```
BankCorp Register/
├── agents/
│   ├── RPA_Senior.md          # Agent profile (mentor)
│   └── requirements.md        # This document
├── data/
│   ├── .env                   # Credentials
│   ├── .gitkeep
│   └── transacoes.csv         # 50 transactions
├── src/
│   ├── __init__.py
│   ├── bankCorp.py            # BankCorp class (site interactions)
│   ├── browser.py             # BrowserManager class (Playwright)
│   └── extract_data.py        # CSV extraction + type mapping
├── main.py                    # Orchestrator (entry point)
└── README.md                  # (optional — how to run)
```

---

## 11. KNOWN LIMITATIONS

1. **No real auth**: The site has no backend. Login always succeeds. The `.env` credentials are for practice/realism.
2. **No deduplication**: Running the script twice will insert duplicate rows. The site has no `unique` constraint.
3. **No session persistence needed**: Since the site has no backend, cookies in `data/Cookies/` are unnecessary for this project (but kept for good practice when targeting real sites).
4. **Type mapping is hardcoded**: If new transaction types appear in the CSV, they will be used as-is (fallback). Add them to `TYPE_MAP` as needed.

---

> **Next Step:** Implement `src/bankCorp.py` (login + fill_transaction + register_all), then `src/extract_data.py`, then wire everything in `main.py`.
