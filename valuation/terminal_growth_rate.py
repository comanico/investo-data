import requests

def fred_series(series_id: str) -> list[tuple[str, float]]:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    out = []
    for line in r.text.strip().splitlines()[1:]:
        date, val = line.split(",")
        if val not in (".", ""):
            out.append((date, float(val)))
    return out

def cagr(series: list[tuple[str, float]], years: int = 5) -> float:
    if len(series) < 2:
        raise ValueError("not enough data")
    end_date, end_val = series[-1]
    # find point ~years earlier
    target_year = int(end_date[:4]) - years
    start_val = None
    for date, val in series:
        if int(date[:4]) >= target_year:
            start_val = val
            start_date = date
            break
    if start_val is None or start_val <= 0:
        raise ValueError("could not find start value")
    n = years  
    return (end_val / start_val) ** (1 / n) - 1

def get_terminal_growth_rate(years) -> float:
    gdp = fred_series("GDPC1")
    g_real = cagr(gdp, years=10)

    infl_series = fred_series("T5YIFR")
    pi = infl_series[-1][1] / 100.0

    g_terminal = g_real + pi
    return g_terminal