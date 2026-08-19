import os
import json
from typing import Any
from openai import OpenAI

client = OpenAI(
    api_key="xai-J8jdd1RZRTlRhAEr315lwvI0kyW97q75UsGyItSxk9zWDxUjvjQNlu7eJ7Xz7Cfhcc1gbqxGE12U3aqZ",
    base_url="https://api.x.ai/v1",
)

MODEL = "grok-4"

FINANCIAL_EXTRACTOR_SYSTEM = """
You are an expert at reading SEC 10-K filings and extracting the exact numbers needed for financial ratio analysis.

You receive Markdown from the table-containing pages of a 10-K.
Extract ONLY the canonical fields listed below. 
Use the company's own labels but map them to these exact keys.
If a value is not clearly present, put null.
Convert all numbers to plain floats (parentheses = negative). Strip $, commas, and unit notes.
Return years as integers and values in the same unit the company uses (usually millions).

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
    "interest_paid": {},
    "taxes_paid": {}
  }
}

Mapping guidance (what to look for in the 10-K):

INCOME STATEMENT
- revenue                  ← Total revenues, Net sales, Total net sales, Revenue
- cost_of_sales            ← Cost of sales, Cost of goods sold, Cost of products sold
- operating_income         ← Operating income/(loss), Operating profit, Income from operations
- interest_expense         ← Interest expense (Company, excluding Ford Credit if broken out)
- income_tax_expense       ← Provision for/(Benefit from) income taxes
- net_income               ← Net income/(loss) attributable to [Company], Net income attributable to shareholders
- dividends_paid           ← Dividends paid (often in cash-flow statement or equity statement)

BALANCE SHEET
- cash                     ← Cash and cash equivalents
- marketable_securities    ← Marketable securities, Short-term investments
- receivables              ← Trade and other receivables, Accounts receivable, Finance receivables (trade portion)
- current_assets           ← Total current assets
- current_liabilities      ← Total current liabilities
- short_term_debt          ← Short-term debt, Current portion of long-term debt, Notes payable
- long_term_debt           ← Long-term debt, Long-term borrowings
- total_debt               ← Sum of short-term + long-term debt if not given directly; also look for "Total debt"
- total_liabilities        ← Total liabilities
- equity                   ← Total equity attributable to [Company], Total stockholders' equity, Total equity

CASH FLOW
- cfo                      ← Net cash provided by/(used in) operating activities
- taxes_paid               ← Income taxes paid (supplemental disclosure)
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