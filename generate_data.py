"""
Transaction Data Analysis
Generates a synthetic transaction dataset (modeled loosely on the kind of
data reviewed in a BSA/AML compliance role) and analyzes it with pandas —
trends by month, category, and a simple high-value flagging rule.

NOTE: transactions.csv is synthetic/randomly generated for portfolio
purposes only — it does not contain real customer or account data.

Run:
    pip install pandas matplotlib numpy
    python generate_data.py   # creates transactions.csv
    python analyze.py         # creates charts + summary.txt
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

rng = np.random.default_rng(seed=42)

N = 2000
categories = ["Retail", "Utilities", "Payroll", "Wire Transfer", "ATM Withdrawal", "Online Payment"]
category_weights = [0.28, 0.14, 0.12, 0.08, 0.20, 0.18]

start_date = datetime(2025, 1, 1)
dates = [start_date + timedelta(days=int(d)) for d in rng.integers(0, 365, size=N)]

# amounts: mostly small/medium, long tail of larger transactions
base_amounts = rng.gamma(shape=2.0, scale=180, size=N)
category_arr = rng.choice(categories, size=N, p=category_weights)

# wire transfers and ATM withdrawals skew larger
multiplier = np.where(category_arr == "Wire Transfer", 6.0,
             np.where(category_arr == "Payroll", 3.0, 1.0))
amounts = np.round(base_amounts * multiplier, 2)

account_ids = rng.integers(100000, 999999, size=N)

df = pd.DataFrame({
    "transaction_id": np.arange(1, N + 1),
    "date": dates,
    "account_id": account_ids,
    "category": category_arr,
    "amount": amounts,
})

df = df.sort_values("date").reset_index(drop=True)
df.to_csv("transactions.csv", index=False)
print(f"Generated {len(df)} synthetic transactions -> transactions.csv")
