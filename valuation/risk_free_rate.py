import requests

def get_risk_free_rate() -> float:
    try:
        r = requests.get(
            "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10",
            timeout=20,
        )
        r.raise_for_status()
        last_rate = r.text.splitlines()[-1].split(",")[1]
        if last_rate:
                return round(float(last_rate) / 100.0, 4)
        else:
            raise ValueError("No last rate found")
    except Exception as e:
        print(f"FRED fetch failed ({e})")
        return 0.0