

import csv                  # For saving portfolio as a .csv file
import os                   # For checking if a save file already exists
from datetime import datetime  # For timestamping reports


# ── 1. HARDCODED STOCK PRICE DATABASE ───────────────────────────
# A dictionary mapping ticker symbols → price per share (USD).
# This acts as our "live market feed" for this simplified tracker.
STOCK_PRICES = {
    "AAPL":  182.50,   # Apple Inc.
    "TSLA":  251.00,   # Tesla Inc.
    "GOOGL": 175.30,   # Alphabet Inc. (Google)
    "MSFT":  415.80,   # Microsoft Corporation
    "AMZN":  189.20,   # Amazon.com Inc.
    "NVDA":  875.40,   # NVIDIA Corporation
    "META":  512.60,   # Meta Platforms Inc.
    "NFLX":  645.90,   # Netflix Inc.
    "AMD":   165.75,   # Advanced Micro Devices
    "INTC":   30.10,   # Intel Corporation
}

# Output filenames
TXT_FILE = "portfolio_report.txt"
CSV_FILE = "portfolio_data.csv"


# ════════════════════════════════════════════════════════════════
#   SECTION 2 — DISPLAY HELPERS
# ════════════════════════════════════════════════════════════════

def print_banner():
    """Prints the welcome banner when the program starts."""
    print("\n" + "═" * 55)
    print("   📈   STOCK PORTFOLIO TRACKER   📈")
    print("        NovaMind Technologies")
    print("═" * 55)
    print("  Track your investments with ease.\n")


def print_available_stocks():
    """Displays the full stock catalogue in a formatted table."""
    print("\n" + "─" * 45)
    print(f"  {'TICKER':<8}  {'COMPANY / ASSET':<24}  {'PRICE (USD)':>10}")
    print("─" * 45)

    # Map ticker → company name for display purposes
    company_names = {
        "AAPL":  "Apple Inc.",
        "TSLA":  "Tesla Inc.",
        "GOOGL": "Alphabet Inc. (Google)",
        "MSFT":  "Microsoft Corporation",
        "AMZN":  "Amazon.com Inc.",
        "NVDA":  "NVIDIA Corporation",
        "META":  "Meta Platforms Inc.",
        "NFLX":  "Netflix Inc.",
        "AMD":   "Advanced Micro Devices",
        "INTC":  "Intel Corporation",
    }

    # Iterate over dictionary items to print each row
    for ticker, price in STOCK_PRICES.items():
        name = company_names.get(ticker, "N/A")
        print(f"  {ticker:<8}  {name:<24}  ${price:>9.2f}")

    print("─" * 45 + "\n")


def print_portfolio_summary(portfolio):
    """
    Displays a detailed summary table of the user's portfolio.

    Args:
        portfolio (list of dict): Each dict contains ticker, qty,
                                  price_per_share, and total_value.
    """
    if not portfolio:
        print("\n  ⚠  Your portfolio is empty.\n")
        return

    grand_total = sum(item["total_value"] for item in portfolio)

    print("\n" + "═" * 65)
    print("   📊  YOUR PORTFOLIO SUMMARY")
    print("═" * 65)
    print(f"  {'#':<4} {'TICKER':<8} {'QTY':>6}  {'PRICE/SH':>10}  "
          f"{'TOTAL VALUE':>13}  {'SHARE %':>8}")
    print("─" * 65)

    # Loop through each holding and print its row
    for i, item in enumerate(portfolio, start=1):
        # Calculate what percentage of the portfolio this stock is
        share_pct = (item["total_value"] / grand_total * 100) if grand_total > 0 else 0

        print(f"  {i:<4} {item['ticker']:<8} {item['qty']:>6}  "
              f"${item['price_per_share']:>9.2f}  "
              f"${item['total_value']:>12,.2f}  "
              f"{share_pct:>7.1f}%")

    print("─" * 65)
    print(f"  {'GRAND TOTAL':>40}   ${grand_total:>12,.2f}")
    print("═" * 65)

    # ── Portfolio analytics ──────────────────────────────────
    # Find the most and least valuable holding
    best  = max(portfolio, key=lambda x: x["total_value"])
    worst = min(portfolio, key=lambda x: x["total_value"])

    print(f"\n  💹  Most valuable  : {best['ticker']}  "
          f"(${best['total_value']:,.2f})")
    print(f"  📉  Least valuable : {worst['ticker']}  "
          f"(${worst['total_value']:,.2f})")
    print(f"  📦  Total holdings : {len(portfolio)} stock(s)\n")


# ════════════════════════════════════════════════════════════════
#   SECTION 3 — INPUT HANDLER
# ════════════════════════════════════════════════════════════════

def get_portfolio_from_user():
    """
    Prompts the user to enter stock tickers and quantities.
    Validates every input before accepting.

    Returns:
        list of dict: Validated portfolio entries.
    """
    portfolio = []          # Will hold the final list of holdings
    added_tickers = set()   # Prevent the user from adding same stock twice

    print("  Enter your stocks below.")
    print("  Type  'LIST'  to see available stocks.")
    print("  Type  'DONE'  when you're finished.\n")

    while True:
        # ── Get ticker ───────────────────────────────────────
        raw = input("  Enter stock ticker (or DONE): ").strip().upper()

        if raw == "DONE":
            # User finished entering stocks
            if not portfolio:
                print("\n  ⚠  You haven't added any stocks yet!")
                continue     # Loop back instead of breaking with empty portfolio
            break

        if raw == "LIST":
            # Show the available stock catalogue on demand
            print_available_stocks()
            continue

        # Validate: must exist in our price database
        if raw not in STOCK_PRICES:
            print(f"  ✘  '{raw}' is not in our database. "
                  f"Type LIST to see valid tickers.\n")
            continue

        # Prevent duplicate entries
        if raw in added_tickers:
            print(f"  ⚠  You already added {raw}. "
                  f"Each stock can only be entered once.\n")
            continue

        # ── Get quantity ─────────────────────────────────────
        while True:
            qty_input = input(f"  How many shares of {raw}? ").strip()

            # Validate: must be a positive integer
            if not qty_input.isdigit() or int(qty_input) <= 0:
                print("  ✘  Please enter a positive whole number (e.g. 10).")
            else:
                qty = int(qty_input)
                break

        # ── Calculate value and store ─────────────────────────
        price = STOCK_PRICES[raw]         # Look up price from dictionary
        total = price * qty               # Basic arithmetic: price × quantity

        # Add this holding as a dictionary to the portfolio list
        portfolio.append({
            "ticker":          raw,
            "qty":             qty,
            "price_per_share": price,
            "total_value":     total,
        })

        added_tickers.add(raw)  # Mark ticker as already added

        print(f"  ✔  Added {qty} × {raw} @ ${price:.2f} = ${total:,.2f}\n")

    return portfolio


# ════════════════════════════════════════════════════════════════
#   SECTION 4 — FILE SAVING
# ════════════════════════════════════════════════════════════════

def save_to_txt(portfolio):
    """
    Saves the portfolio summary to a human-readable .txt file.

    Args:
        portfolio (list of dict): The user's portfolio data.
    """
    grand_total = sum(item["total_value"] for item in portfolio)
    timestamp   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Open file in write mode ('w'); creates it if it doesn't exist
    with open(TXT_FILE, "w") as f:
        f.write("=" * 55 + "\n")
        f.write("   STOCK PORTFOLIO REPORT — NovaMind Technologies\n")
        f.write(f"   Generated: {timestamp}\n")
        f.write("=" * 55 + "\n\n")

        # Write each holding
        f.write(f"  {'TICKER':<8}  {'QTY':>6}  {'PRICE/SH':>10}  {'TOTAL':>13}\n")
        f.write("─" * 45 + "\n")

        for item in portfolio:
            f.write(
                f"  {item['ticker']:<8}  {item['qty']:>6}  "
                f"${item['price_per_share']:>9.2f}  "
                f"${item['total_value']:>12,.2f}\n"
            )

        f.write("─" * 45 + "\n")
        f.write(f"  {'GRAND TOTAL':<30}  ${grand_total:>12,.2f}\n")
        f.write("\n" + "=" * 55 + "\n")
        f.write("  Thank you for using Stock Portfolio Tracker!\n")
        f.write("=" * 55 + "\n")

    print(f"  ✔  Text report saved  →  {TXT_FILE}")


def save_to_csv(portfolio):
    """
    Saves the portfolio data to a .csv file (spreadsheet-ready).

    Args:
        portfolio (list of dict): The user's portfolio data.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Define the column headers for the CSV
    fieldnames = ["Timestamp", "Ticker", "Quantity",
                  "Price_Per_Share_USD", "Total_Value_USD"]

    # Open file in write mode; newline='' prevents extra blank rows on Windows
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()   # Write the header row

        # Write one row per stock holding
        for item in portfolio:
            writer.writerow({
                "Timestamp":           timestamp,
                "Ticker":              item["ticker"],
                "Quantity":            item["qty"],
                "Price_Per_Share_USD": f"{item['price_per_share']:.2f}",
                "Total_Value_USD":     f"{item['total_value']:.2f}",
            })

    print(f"  ✔  CSV data saved     →  {CSV_FILE}")


def ask_to_save(portfolio):
    """
    Asks the user whether they want to save their report,
    and to which format(s).
    """
    print("\n" + "─" * 45)
    print("  💾  SAVE YOUR REPORT")
    print("─" * 45)
    print("  [1]  Save as .txt (human-readable report)")
    print("  [2]  Save as .csv (spreadsheet-ready data)")
    print("  [3]  Save BOTH formats")
    print("  [4]  Don't save — exit without saving")
    print("─" * 45)

    while True:
        choice = input("  Your choice (1/2/3/4): ").strip()

        if choice == "1":
            save_to_txt(portfolio)
            break
        elif choice == "2":
            save_to_csv(portfolio)
            break
        elif choice == "3":
            save_to_txt(portfolio)
            save_to_csv(portfolio)
            break
        elif choice == "4":
            print("  ℹ  Exiting without saving.")
            break
        else:
            print("  ✘  Invalid choice. Please enter 1, 2, 3, or 4.")


# ════════════════════════════════════════════════════════════════
#   SECTION 5 — MAIN FUNCTION
# ════════════════════════════════════════════════════════════════

def main():
    """
    Entry point — orchestrates the full tracker workflow:
        1. Show banner
        2. Show available stocks
        3. Collect user input
        4. Display portfolio summary
        5. Offer to save the report
    """
    # Step 1 — Welcome the user
    print_banner()

    # Step 2 — Show available stocks upfront
    print("  Here are the stocks available to track:\n")
    print_available_stocks()

    # Step 3 — Collect stock entries from the user
    portfolio = get_portfolio_from_user()

    # Step 4 — Display the full portfolio summary
    print_portfolio_summary(portfolio)

    # Step 5 — Optionally save results to file(s)
    ask_to_save(portfolio)

    # Goodbye message
    print("\n  👋  Thank you for using NovaMind Stock Tracker!")
    print("  Stay invested. Stay smart. 📈\n")


# ── ENTRY POINT GUARD ────────────────────────────────────────────
# Ensures main() only runs when this script is executed directly,
# not when imported as a module into another Python file.
if __name__ == "__main__":
    main()
