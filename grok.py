from dotenv import load_dotenv
import os
import json
from typing import Any
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROK_API"),
    base_url="https://api.x.ai/v1",
)

MODEL = "grok-4"

FINANCIAL_EXTRACTOR_SYSTEM = """
You are an expert at reading SEC 10-K filings and extracting the exact numbers needed for financial ratio analysis and DCF valuation.

You receive Markdown from the table-containing pages of a 10-K.
Extract ONLY the canonical fields listed below.
Use the company's own labels but map them to these exact keys.
If a value is not clearly present, put null.
Convert all numbers to plain floats (parentheses = negative). Strip $, commas, and unit notes.
Return years as integers and values in the same unit the company uses (usually millions).
Use string keys for years in nested objects, e.g. "2024".

Return ONLY valid JSON in this schema:

{
  "company": "string or null",
  "currency": "USD",
  "unit": "millions",
  "years": [2023, 2024, 2025],
  "income_statement": {
    "revenue": {},
    "cost_of_sales": {},
    "operating_income": {},
    "interest_expense": {},
    "income_tax_expense": {},
    "net_income": {},
    "dividends_paid": {}
  },
  "balance_sheet": {
    "cash": {},
    "marketable_securities": {},
    "receivables": {},
    "current_assets": {},
    "current_liabilities": {},
    "short_term_debt": {},
    "long_term_debt": {},
    "total_debt": {},
    "total_liabilities": {},
    "equity": {}
  },
  "cash_flow": {
    "cfo": {},
    "depreciation_amortization": {},
    "capex": {},
    "dividends_paid": {},
    "proceeds_from_debt": {},
    "repayments_of_debt": {},
    "net_debt_issuance": {},
    "interest_paid": {},
    "taxes_paid": {}
  }
}

Mapping guidance:

INCOME STATEMENT
- revenue                  ← Total revenues, Net sales, Total net sales, Revenue
- cost_of_sales            ← Cost of sales, Cost of goods sold, Cost of products sold
- operating_income         ← Operating income/(loss), Income from operations
- interest_expense         ← Interest expense (prefer Company excluding finance subsidiary if broken out)
- income_tax_expense       ← Provision for/(Benefit from) income taxes
- net_income               ← Net income/(loss) attributable to [parent], Net income attributable to shareholders
- dividends_paid           ← Common dividends declared (if only on equity/CF statement, still fill here when found)

BALANCE SHEET
- cash                     ← Cash and cash equivalents
- marketable_securities    ← Marketable securities, Short-term investments
- receivables              ← Trade and other receivables, Accounts receivable
- current_assets           ← Total current assets
- current_liabilities      ← Total current liabilities
- short_term_debt          ← Short-term debt, Current portion of long-term debt, Notes payable
- long_term_debt           ← Long-term debt
- total_debt               ← Total debt, or short-term + long-term debt
- total_liabilities        ← Total liabilities
- equity                   ← Total equity attributable to parent / stockholders' equity

CASH FLOW (critical for valuation)
- cfo                      ← Net cash provided by/(used in) operating activities
- depreciation_amortization← Depreciation and amortization, Depreciation and tooling amortization
- capex                    ← Capital expenditures, Purchase of property and equipment, Additions to property/equipment
                             (usually negative or shown as use of cash; store as signed number, negative = outflow)
- dividends_paid           ← Payments of dividends, Cash dividends paid, Dividends to shareholders
                             (usually negative; store signed)
- proceeds_from_debt       ← Proceeds from issuance of long-term debt, Proceeds from debt
- repayments_of_debt       ← Principal payments on debt, Payments of long-term debt, Repayments of debt
- net_debt_issuance        ← proceeds_from_debt + repayments_of_debt if both present (repayments negative),
                             or a single net line if the company reports one
- interest_paid            ← Cash paid for interest (supplemental)
- taxes_paid               ← Cash paid for income taxes (supplemental)

Prefer consolidated figures. If automotive vs financial-services (e.g. Ford Credit) are split, prefer totals that match the consolidated statements unless a field explicitly asks for Company excluding finance subsidiary.
"""

def extract_financials_with_grok(markdown: str, model: str = MODEL) -> dict[str, Any]:

    content = "Extract the four consolidated financial statements from the following 10-K Markdown:\n\n" + markdown
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": FINANCIAL_EXTRACTOR_SYSTEM},
            {
                "role": "user",
                "content": (
                    content
                ),
            },
        ],
    )
    return json.loads(response.choices[0].message.content)
