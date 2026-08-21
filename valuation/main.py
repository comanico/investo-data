from pathlib import Path

import pandas as pd

import yfinance as yf
from valuation.equity_risk_premium import get_equity_risk_premium
from valuation.risk_free_rate import get_risk_free_rate
from lib import json_read
from valuation.owc import get_delta_owc
from valuation.terminal_growth_rate import get_terminal_growth_rate

class AbsoluteValuation:
    def __init__(self, ticker: str):
        # Market Data
        self.info = yf.Ticker(ticker).info
        self.shares_outstanding = self.info.get("sharesOutstanding")
        self.beta = self.info.get("beta")
        self.price = self.info.get("currentPrice")
        self.market_cap = self.shares_outstanding * self.price

        # Financials
        self.financials = json_read(Path("../extracted_financials_ford/structured.json"))
        self.net_debt = 0
        self.total_capital = 0
        self.equity_weight = 0
        self.debt_weight = 0
        self.interest_expense = 0
        self.avg_debt = 0
        self.pre_tax_cost_of_debt = 0
        self.net_income_attrib = 0
        self.operating_income = 0
        self.income_tax_expense = 0
        self.tax_rate = abs(self.income_tax_expense) /  abs(self.operating_income)
        self.nopat = self.operating_income * (1 - self.tax_rate)
        self.deprecation_amortization = 0
        self.capex = 0
        self.delta_operating_working_capital = get_delta_owc(
            self.financials["years"],
            self.financials["balance_sheet"]["current_assets"], 
            self.financials["balance_sheet"]["cash"], 
            self.financials["balance_sheet"]["marketable_securities"], 
            self.financials["balance_sheet"]["current_liabilities"], 
            self.financials["balance_sheet"]["short_term_debt"]
            )
        self.net_debt_issuance = 0
        self.equity_begin = 0
        self.dividends_paid = 0
        self.revenue = 0
        self.payout_ratio = 0

        # Growth Rate
        self.risk_free_rate = get_risk_free_rate()
        self.equity_risk_premium = get_equity_risk_premium()
        self.required_return = 0
        self.calculated_equity_risk_premium = 0
        self.weighted_average_cost_per_capital = 0
        self.revenue_growth_rate = 0
        self.short_growth_rate = max(0.025, min(0.06, self.revenue_growth_rate * 0.6))
        self.terminal_growth_rate = get_terminal_growth_rate(len(self.financials["years"]))

    