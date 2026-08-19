import sys
import json
import pandas as pd
import pdf_inspector
from pathlib import Path
from grok import extract_financials_with_grok
from ratios import compute_ratios_from_structured


def markdown_to_dataframes(data: dict) -> dict[str, pd.DataFrame]:
    frames = {}
    for key in ["income_statement", "balance_sheet", "cash_flow", "equity"]:
        stmt = data.get(key)
        if not stmt or not stmt.get("rows"):
            continue
        years = [str(y) for y in stmt["years"]]
        rows = []
        for r in stmt["rows"]:
            row = {"item": r["item"]}
            for y, v in zip(years, r["values"]):
                row[y] = v
            rows.append(row)
        frames[key] = pd.DataFrame(rows)
    return frames


def main(pdf_path):
    pdf = Path(pdf_path)
    firm = str(pdf).split(".")[0]
    result = pdf_inspector.process_pdf(str(pdf))

    table_pages = result.pages_with_tables
    table_inspector = pdf_inspector.process_pdf(str(pdf), pages=table_pages)

    structured = extract_financials_with_grok(table_inspector.markdown)

    dfs = markdown_to_dataframes(structured)

    out_dir = Path(f"extracted_financials_{firm}")
    out_dir.mkdir(exist_ok=True)

    with open(out_dir / "structured.json", "w") as f:
        json.dump(structured, f, indent=2)

    ratios_df = compute_ratios_from_structured(structured)
    ratios_df.to_csv(f"{out_dir}/ratios.csv")

    for name, df in dfs.items():
        print(f"\n=== {name.upper()} ===")
        print(df.head(10).to_string(index=False))
        df.to_csv(out_dir / f"{name}.csv", index=False)

    print(f"\nSaved → {out_dir}/")
    return structured, dfs


if __name__ == "__main__":
    pdf = sys.argv[1] if len(sys.argv) > 1 else "./ford.pdf"
    main(pdf)
