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
        """
        Market Data
        """
        self.info = yf.Ticker(ticker).info
        self.shares_outstanding = self.info.get("sharesOutstanding") / 1e6
        self.beta = self.info.get("beta")
        self.price = self.info.get("currentPrice")
        self.market_cap = self.shares_outstanding * self.price

        """
        Financials
        """
        self.financials = json_read(
            Path("../extracted_financials_ford/structured.json"))
        self.first_year = self.financials["years"][0]
        self.current_year = self.financials["years"][-1]
        self.previous_year = self.financials["years"][-2]

        # Income Statement
        self.interest_expense = self.financials["income_statement"]["interest_expense"][self.current_year]
        self.net_income_attrib = self.financials["income_statement"]["net_income"][self.current_year]
        self.operating_income = self.financials["income_statement"]["operating_income"][self.current_year]
        self.income_tax_expense = self.financials["income_statement"]["income_tax_expense"][self.current_year]
        self.revenue = self.financials["income_statement"]["revenue"][self.current_year]

        # Balance Sheet
        self.net_debt = \
            self.financials["balance_sheet"]["total_debt"][self.current_year] -  \
            (self.financials["balance_sheet"]["cash"][self.current_year] +
             self.financials["balance_sheet"]["marketable_securities"][self.current_year])
        self.avg_debt = (self.financials["balance_sheet"]["total_debt"][self.current_year] +
                         self.financials["balance_sheet"]["total_debt"][self.previous_year]) / 2
        self.book_equity_begin = self.financials["balance_sheet"]["equity"][self.previous_year]
        self.delta_operating_working_capital = get_delta_owc(
            self.financials["years"],
            self.financials["balance_sheet"]["current_assets"],
            self.financials["balance_sheet"]["cash"],
            self.financials["balance_sheet"]["marketable_securities"],
            self.financials["balance_sheet"]["current_liabilities"],
            self.financials["balance_sheet"]["short_term_debt"]
        )

        # Cash Flow
        self.depreciation_amortization = self.financials["cash_flow"][
            "depreciation_amortization"][self.current_year]
        self.capex = abs(
            self.financials["cash_flow"]["capex"][self.current_year])
        self.net_debt_issuance = self.financials["cash_flow"]["net_debt_issuance"][self.current_year]
        self.dividends_paid = abs(
            self.financials["cash_flow"]["dividends_paid"][self.current_year])

        # Calculations
        self.total_capital = self.market_cap + self.net_debt
        self.equity_weight = self.market_cap / self.total_capital
        self.debt_weight = self.net_debt / self.total_capital
        self.pre_tax_cost_of_debt = self.interest_expense / self.avg_debt
        self.pretax_income = self.net_income_attrib + self.income_tax_expense
        self.tax_rate = self.income_tax_expense / self.pretax_income
        self.nopat = self.operating_income * (1 - self.tax_rate)
        self.payout_ratio = self.dividends_paid / self.net_income_attrib

        # Growth Rate
        self.risk_free_rate = get_risk_free_rate()
        self.equity_risk_premium = get_equity_risk_premium()
        self.required_return = self.risk_free_rate + \
            self.beta * self.equity_risk_premium
        self.calculated_equity_risk_premium = self.required_return - self.risk_free_rate
        self.weighted_average_cost_per_capital = (
            self.equity_weight * self.required_return
            + self.debt_weight * self.pre_tax_cost_of_debt *
            (1 - self.tax_rate)
        )
        self.revenue_growth_rate = ((self.financials["income_statement"]["revenue"][self.current_year] /
                                    self.financials["income_statement"]["revenue"][self.first_year]) ** (1/len(self.financials["years"] - 1))) - 1
        self.short_growth_rate = max(0.025, min(
            0.06, self.revenue_growth_rate * 0.6))
        self.terminal_growth_rate = get_terminal_growth_rate(
            len(self.financials["years"]))
