import re
import requests


def get_equity_risk_premium() -> float:
    try:
        r = requests.get(
            "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histimpl.html",
            timeout=20,
        )
        if r.ok:
            # Last table row often has most recent year ERP
            matches = re.findall(
                r"<td[^>]*>\s*(\d{4})\s*</td>.*?(\d+\.\d+)\s*%\s*</td>\s*</tr>",
                r.text,
                flags=re.I | re.S,
            )
            if matches:
                year, erp = matches[-1]
                erp_f = round(float(erp) / 100.0, 4)
                if erp_f:
                    print(f"Damodaran histimpl last row year={year} ERP={erp_f:.2%}")
                    return erp_f
                else: 
                    raise ValueError("No ERP found")
            else:
                raise ValueError("No ERP Match found")
        else:
            raise ValueError("Could not fetch ERP from link")
    except Exception as e:
        print(f"Damodaran fetch failed ({e})")
        return 0.0