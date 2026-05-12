import pandas as pd
from pathlib import Path

# ========= CONFIG =========
FILE_PATH = r"C:\Users\tputze\Downloads\Invoicing - FG Jan 2025 - Mar 2026.xlsx"  # <-- put your full path here
SHEET_NAME = "Test"

# Invoices to include (Timesheets keep ALL statuses)
KEEP_INV_STATUSES = {"Paid", "Payment Pending", "Pending Approval"}
# If you want ALL invoice statuses too, set:
# KEEP_INV_STATUSES = None

# Round amounts before matching (use 2 for cents, or 0 to ignore cents)
DECIMALS = 2
# ==========================


def clean_amount(series, decimals=2):
    """
    Parse amounts robustly:
    - strip € and spaces,
    - keep dot-decimals as-is,
    - convert comma-decimals if present,
    - round to 'decimals'.
    """
    s = series.astype(str).str.strip()
    s = (
        s.str.replace("€", "", regex=False)
         .str.replace("\xa0", "", regex=False)  # NBSP
         .str.replace(" ", "", regex=False)
    )

    def parse_one(x: str):
        if not x or x.lower() in {"nan", "none"}:
            return float("nan")
        if "," in x:  # European format
            x = x.replace(".", "").replace(",", ".")
        return pd.to_numeric(x, errors="coerce")

    out = s.map(parse_one)
    if decimals is not None:
        out = out.round(decimals)
    return out


def pick_duplicate_columns(df):
    """
    Resolve the two side-by-side datasets even if pandas suffixed duplicate
    headers (e.g., 'Status', 'Status.1', ...).

    Returns concrete labels:
      invoices:   inv_status, inv_name, inv_amount
      timesheets: ts_status, ts_name, ts_start, ts_amount
    """
    def base(col):
        return str(col).strip().split('.', 1)[0]

    cols = list(df.columns)
    bases = [base(c) for c in cols]

    idx_status = [i for i, b in enumerate(bases) if b == "Status"]
    idx_name   = [i for i, b in enumerate(bases) if b == "Name"]
    idx_amount = [i for i, b in enumerate(bases) if b == "Amount"]
    idx_start  = [i for i, b in enumerate(bases) if b == "Start"]

    if len(idx_status) < 2 or len(idx_name) < 2 or len(idx_amount) < 2:
        raise ValueError(
            "Could not find two sets of Status/Name/Amount columns. "
            f"Status idx: {idx_status}, Name idx: {idx_name}, Amount idx: {idx_amount}."
        )
    if not idx_start:
        raise ValueError("Could not find a 'Start' column in the timesheets block.")

    # Leftmost set = invoices; second set = timesheets
    inv_status_col = cols[idx_status[0]]
    inv_name_col   = cols[idx_name[0]]
    inv_amount_col = cols[idx_amount[0]]

    ts_status_col  = cols[idx_status[1]]
    ts_name_col    = cols[idx_name[1]]
    ts_amount_col  = cols[idx_amount[1]]
    ts_start_col   = cols[idx_start[-1]]  # prefer the right-side 'Start' if duplicated

    print("Resolved columns ->",
          {"inv_status": inv_status_col, "inv_name": inv_name_col, "inv_amount": inv_amount_col,
           "ts_status": ts_status_col, "ts_name": ts_name_col, "ts_start": ts_start_col, "ts_amount": ts_amount_col})

    return {
        "inv_status": inv_status_col,
        "inv_name": inv_name_col,
        "inv_amount": inv_amount_col,
        "ts_status": ts_status_col,
        "ts_name": ts_name_col,
        "ts_start": ts_start_col,
        "ts_amount": ts_amount_col,
    }


def main():
    path = Path(FILE_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    # Read full sheet (we need the headers exactly as exported)
    df = pd.read_excel(path, sheet_name=SHEET_NAME, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    cmap = pick_duplicate_columns(df)  # auto-detect left/right blocks

    # Build datasets
    inv = df[[cmap["inv_status"], cmap["inv_name"], cmap["inv_amount"]]].copy()
    inv.columns = ["Invoice Status", "Program", "inv_amount_raw"]

    ts  = df[[cmap["ts_status"], cmap["ts_name"], cmap["ts_start"], cmap["ts_amount"]]].copy()
    ts.columns  = ["TS Status", "Person", "Date", "ts_amount_raw"]

    # Parse amounts & dates
    inv["Invoice Amount"] = clean_amount(inv["inv_amount_raw"], decimals=DECIMALS)
    ts["TS Amount"]       = clean_amount(ts["ts_amount_raw"], decimals=DECIMALS)
    ts["Date"]            = pd.to_datetime(ts["Date"], errors="coerce")

    # Trim statuses just in case
    inv["Invoice Status"] = inv["Invoice Status"].astype(str).str.strip()
    ts["TS Status"]       = ts["TS Status"].astype(str).str.strip()

    # Filter invoices by status (timesheets: keep ALL statuses)
    if KEEP_INV_STATUSES is None:
        inv_filt = inv.copy()
    else:
        inv_filt = inv[inv["Invoice Status"].isin(KEEP_INV_STATUSES)].copy()

    # *** CRITICAL: keep only NON-ZERO (positive) amounts on both sides ***
    inv_filt = inv_filt[inv_filt["Invoice Amount"] > 0]
    ts       = ts[ts["TS Amount"] > 0]

    # === INNER JOIN: only real matches remain ===
    matches_exact_nonzero = inv_filt.merge(
        ts,
        left_on="Invoice Amount",
        right_on="TS Amount",
        how="inner",                     # <-- inner join so no empty TS columns
        suffixes=("_inv", "_ts")
    )[["Program", "Invoice Amount", "Invoice Status",
       "TS Status", "Person", "Date", "TS Amount"]]

    # Summary
    summary = pd.DataFrame([
        {"Metric": "Invoices (status filter + amount>0)", "Count": len(inv_filt)},
        {"Metric": "Timesheets (all statuses, amount>0)", "Count": len(ts)},
        {"Metric": "Exact matches (rows)",                 "Count": len(matches_exact_nonzero)},
        {"Metric": "Distinct invoice amounts matched",     "Count": matches_exact_nonzero["Invoice Amount"].nunique()},
    ])

    # Save output next to the input file
    out_path = path.with_name("matches.xlsx")
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        matches_exact_nonzero.to_excel(writer, sheet_name="matches_exact_nonzero", index=False)
        summary.to_excel(writer, sheet_name="summary", index=False)

    print(f"✅ Done. Wrote '{out_path}'.")
    print(summary)


if __name__ == "__main__":
    main()