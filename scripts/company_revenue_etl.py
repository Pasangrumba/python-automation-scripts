"""ETL pipeline: scrape the largest US companies by revenue from Wikipedia,
clean the data with pandas, and load it into a SQLite database for SQL reporting.

Usage:
    python scripts/company_revenue_etl.py
    python scripts/company_revenue_etl.py --csv output/companies.csv --db output/companies.db
"""
import argparse
import re
import sqlite3

import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://en.wikipedia.org/wiki/List_of_largest_companies_in_the_United_States_by_revenue"
HEADERS = {"User-Agent": "python-automation-scripts/1.0 (portfolio project)"}


def extract(url=URL):
    """Download the page and return the rows of the first wikitable."""
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "wikitable"})
    if table is None:
        raise ValueError("No wikitable found on the page")

    data = []
    for row in table.find_all("tr")[1:]:  # skip header row
        cols = [col.get_text(strip=True) for col in row.find_all(["th", "td"])]
        if len(cols) >= 7:
            data.append({
                "Rank": cols[0],
                "Name": cols[1],
                "Industry": cols[2],
                "Revenue": cols[3],
                "RevenueGrowth": cols[4],
                "Headquarters": cols[6],
            })
    return pd.DataFrame(data)


def parse_number(text):
    """Turn strings like '648,125' or '5.5%' into floats; return None if not numeric."""
    cleaned = re.sub(r"\[.*?\]", "", str(text))  # remove footnotes like [1]
    cleaned = cleaned.replace(",", "").replace("%", "").replace("$", "").strip()
    cleaned = cleaned.replace("−", "-")  # Unicode minus sign
    try:
        return float(cleaned)
    except ValueError:
        return None


def transform(df):
    """Clean types, convert revenue and growth to numbers, and drop invalid rows."""
    df = df.copy()
    df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")
    df["RevenueUSDm"] = df["Revenue"].map(parse_number)
    df["RevenueGrowthPct"] = df["RevenueGrowth"].map(parse_number)
    df = df.dropna(subset=["Rank", "RevenueUSDm"])
    df["Rank"] = df["Rank"].astype(int)
    return df[["Rank", "Name", "Industry", "RevenueUSDm", "RevenueGrowthPct", "Headquarters"]]


def load(df, csv_path, db_path):
    """Save the clean data to CSV and to a SQLite table called 'companies'."""
    df.to_csv(csv_path, index=False)
    with sqlite3.connect(db_path) as conn:
        df.to_sql("companies", conn, if_exists="replace", index=False)


def report(db_path):
    """Run a SQL aggregation: total and average revenue per industry."""
    query = """
        SELECT Industry,
               COUNT(*)                  AS companies,
               ROUND(SUM(RevenueUSDm))   AS total_revenue_usd_m,
               ROUND(AVG(RevenueUSDm))   AS avg_revenue_usd_m
        FROM companies
        GROUP BY Industry
        ORDER BY total_revenue_usd_m DESC
        LIMIT 10
    """
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", default="output/largest_us_companies.csv")
    parser.add_argument("--db", default="output/companies.db")
    args = parser.parse_args()

    raw = extract()
    print(f"Extracted {len(raw)} rows")
    clean = transform(raw)
    print(f"{len(clean)} rows after cleaning")
    load(clean, args.csv, args.db)
    print(f"Saved to {args.csv} and {args.db}\n")
    print("Top industries by total revenue (USD millions):")
    print(report(args.db).to_string(index=False))


if __name__ == "__main__":
    main()
