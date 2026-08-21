import pandas as pd

def compute_dupont_ratios_from_structured(data: dict) -> pd.DataFrame:
    years = [str(y) for y in data["years"]]
    inc = data.get("income_statement", {})
    bal = data.get("balance_sheet", {})
    cf  = data.get("cash_flow", {})

    def v(section, key, year):
        return section.get(key, {}).get(year)

    rows = {}
    for y in years:
        rev   = v(inc, "revenue", y)
        opinc = v(inc, "operating_income", y)
        tax   = v(inc, "income_tax_expense", y)
        ni    = v(inc, "net_income", y)
        tliab = v(bal, "total_liabilities", y)
        eq    = v(bal, "equity", y)

        pretax = (ni + tax) if (ni is not None and tax is not None) else ni
        assets = v(bal, "total_assets", y) or (
            (tliab + eq) if (tliab is not None and eq is not None) else None
        )

        r = {}
        r["DuPont Tax Burden"] = ni / pretax if pretax else None
        r["DuPont Interest Burden"] = pretax / opinc if opinc else None
        r["DuPont Operating Margin"] = opinc / rev if rev else None
        r["DuPont Asset Turnover"] = rev / assets if assets else None
        r["DuPont Financial Leverage"] = assets / eq if eq else None
        r["DuPont ROE Check"] = ni / eq if eq else None
        rows[y] = r

    df = pd.DataFrame(rows).T   
    return df