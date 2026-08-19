import pandas as pd

def compute_ratios_from_structured(data: dict) -> pd.DataFrame:
    years = [str(y) for y in data["years"]]
    inc = data.get("income_statement", {})
    bal = data.get("balance_sheet", {})
    cf  = data.get("cash_flow", {})

    def v(section, key, year):
        return section.get(key, {}).get(year)

    rows = {}
    for y in years:
        rev   = v(inc, "revenue", y)
        cos   = v(inc, "cost_of_sales", y)
        opinc = v(inc, "operating_income", y)
        intexp= v(inc, "interest_expense", y)
        tax   = v(inc, "income_tax_expense", y)
        ni    = v(inc, "net_income", y)
        div   = v(inc, "dividends_paid", y)

        cash  = v(bal, "cash", y)
        mkt   = v(bal, "marketable_securities", y)
        rec   = v(bal, "receivables", y)
        ca    = v(bal, "current_assets", y)
        cl    = v(bal, "current_liabilities", y)
        std   = v(bal, "short_term_debt", y)
        ltd   = v(bal, "long_term_debt", y)
        tdebt = v(bal, "total_debt", y) or ((std or 0) + (ltd or 0) if (std is not None or ltd is not None) else None)
        tliab = v(bal, "total_liabilities", y)
        eq    = v(bal, "equity", y)

        cfo   = v(cf, "cfo", y)
        taxpd = v(cf, "taxes_paid", y)

        avg_eq = eq

        owc = None
        if ca is not None and cl is not None:
            owc = (ca - (cash or 0) - (mkt or 0)) - (cl - (std or 0))

        tax_rate = 0.25
        if tax is not None and opinc and opinc != 0:
            tax_rate = min(abs(tax) / abs(opinc), 0.5)
        nopat = opinc * (1 - tax_rate) if opinc is not None else None

        r = {}
        r["ROE"] = ni / avg_eq if (ni is not None and avg_eq) else None
        r["Gross Profit Margin"] = (rev - cos) / rev if (rev and cos is not None) else None
        r["EBITA Margin"] = opinc / rev if (opinc is not None and rev) else None
        r["NOPAT Margin"] = nopat / rev if (nopat is not None and rev) else None
        r["Recurring NOPAT Margin"] = r["NOPAT Margin"]
        r["Current Ratio"] = ca / cl if (ca and cl) else None
        r["Quick Ratio"] = ((cash or 0) + (mkt or 0) + (rec or 0)) / cl if cl else None
        r["Cash Ratio"] = ((cash or 0) + (mkt or 0)) / cl if cl else None
        r["Operating Cash Flow Ratio"] = cfo / cl if (cfo is not None and cl) else None
        r["Liabilities-to-Equity"] = tliab / eq if (tliab is not None and eq) else None
        r["Debt-to-Equity"] = tdebt / eq if (tdebt is not None and eq) else None
        r["Debt-to-Capital"] = tdebt / (tdebt + eq) if (tdebt is not None and eq is not None) else None
        r["Interest Coverage (Earnings)"] = opinc / intexp if (opinc is not None and intexp) else None
        r["Interest Coverage (Cash Flow)"] = (
            (cfo + (intexp or 0) + (taxpd or 0)) / intexp
            if (cfo is not None and intexp) else None
        )
        r["OWC / Sales"] = owc / rev if (owc is not None and rev) else None
        r["OWC Turnover"] = rev / owc if (owc and owc != 0 and rev) else None
        r["Dividend Payout Ratio"] = div / ni if (div is not None and ni and ni != 0) else None
        r["Sustainable Growth Rate"] = (
            r["ROE"] * (1 - r["Dividend Payout Ratio"])
            if (r["ROE"] is not None and r["Dividend Payout Ratio"] is not None) else None
        )
        rows[y] = r

    df = pd.DataFrame(rows).T   
    return df