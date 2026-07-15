"""
Analyze transactions.csv: monthly volume trends, category breakdown,
and a simple high-value flagging rule (analogous to threshold-based
transaction monitoring in compliance workflows).
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("transactions.csv", parse_dates=["date"])

# ---- Monthly trend ----
monthly = df.set_index("date").resample("ME")["amount"].agg(["count", "sum"])
monthly.index = monthly.index.strftime("%Y-%m")

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.bar(monthly.index, monthly["count"], color="#2c6e9e")
ax.set_title("Transaction Volume by Month")
ax.set_ylabel("Number of Transactions")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("transactions_by_month.png", dpi=140)
plt.close()

# ---- Category breakdown ----
by_cat = df.groupby("category")["amount"].agg(["count", "sum", "mean"]).sort_values("sum", ascending=False)

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.barh(by_cat.index, by_cat["sum"], color="#3f9e8f")
ax.set_title("Total Transaction Value by Category")
ax.set_xlabel("Total Amount ($)")
plt.tight_layout()
plt.savefig("total_value_by_category.png", dpi=140)
plt.close()

# ---- High-value flagging (analogous to threshold-based monitoring) ----
THRESHOLD = 10000
flagged = df[df["amount"] >= THRESHOLD].copy()
flag_rate_by_cat = (
    df.assign(flagged=df["amount"] >= THRESHOLD)
    .groupby("category")["flagged"]
    .mean()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(flag_rate_by_cat.index, flag_rate_by_cat.values * 100, color="#e8a33d")
ax.set_title(f"Share of Transactions ≥ ${THRESHOLD:,} by Category")
ax.set_ylabel("% of Transactions Flagged")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("flag_rate_by_category.png", dpi=140)
plt.close()

# ---- Write summary ----
with open("summary.txt", "w") as f:
    f.write("TRANSACTION DATA ANALYSIS SUMMARY\n")
    f.write("=" * 40 + "\n\n")
    f.write(f"Total transactions analyzed: {len(df):,}\n")
    f.write(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}\n")
    f.write(f"Total value: ${df['amount'].sum():,.2f}\n")
    f.write(f"Average transaction: ${df['amount'].mean():,.2f}\n\n")

    f.write("Volume & value by category:\n")
    f.write(by_cat.round(2).to_string())
    f.write("\n\n")

    f.write(f"Transactions >= ${THRESHOLD:,} (flagged for review): {len(flagged)} "
            f"({len(flagged) / len(df) * 100:.1f}% of all transactions)\n\n")

    f.write("Flag rate by category:\n")
    f.write((flag_rate_by_cat * 100).round(1).astype(str).add(" %").to_string())
    f.write("\n\n")

    top_cat = by_cat["sum"].idxmax()
    top_flag_cat = flag_rate_by_cat.idxmax()
    f.write(f"Key finding: '{top_cat}' accounts for the highest total transaction value, "
            f"while '{top_flag_cat}' has the highest rate of high-value transactions "
            f"flagged for review.\n")

print("Analysis complete. Generated:")
print(" - transactions_by_month.png")
print(" - total_value_by_category.png")
print(" - flag_rate_by_category.png")
print(" - summary.txt")
