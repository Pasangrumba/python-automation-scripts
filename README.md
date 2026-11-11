# Python Automation Scripts

Practical Python scripts for data extraction, ETL, file automation and email, built during my Data Science programme at Future Connect (2026) and extended with command-line interfaces, error handling and automated tests.

| Script | What it does | Skills |
|--------|--------------|--------|
| [`company_revenue_etl.py`](scripts/company_revenue_etl.py) | Scrapes the largest US companies by revenue from Wikipedia, cleans the data with pandas, loads it into SQLite and runs a SQL report by industry | Web scraping, ETL, pandas, SQL, SQLite |
| [`bulk_file_renamer.py`](scripts/bulk_file_renamer.py) | Renames all files with an extension to a numbered pattern, with a dry-run mode and protection against overwriting | File automation, `os`, argparse |
| [`send_email.py`](scripts/send_email.py) | Sends an email to multiple recipients over SMTP, with credentials read from environment variables | SMTP, `email`, secure config |
| [`zodiac_sign.py`](scripts/zodiac_sign.py) | Works out a zodiac sign from a birth date and appends results to a CSV | Date handling, pandas, CSV |

## ETL pipeline example

```
$ python scripts/company_revenue_etl.py
Extracted 100 rows
100 rows after cleaning
Saved to output/largest_us_companies.csv and output/companies.db

Top industries by total revenue (USD millions):
     Industry  companies  total_revenue_usd_m  avg_revenue_usd_m
   Financials         16            1874315.0           117145.0
   Healthcare          7            1719550.0           245650.0
       Retail          9            1628090.0           180899.0
    Petroleum          9            1208185.0           134243.0
   Technology          9            1041637.0           115737.0
```

**Extract:** `requests` + BeautifulSoup read the Wikipedia table.
**Transform:** pandas converts revenue and growth strings (commas, %, footnotes, Unicode minus) to numbers and drops invalid rows.
**Load:** results are written to CSV and a SQLite `companies` table, then queried with SQL (`GROUP BY`, `SUM`, `AVG`).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python scripts/company_revenue_etl.py
python scripts/bulk_file_renamer.py ./photos .jpg holiday --dry-run
python scripts/zodiac_sign.py "Pasang" 1986-03-08

export SMTP_EMAIL="you@gmail.com"
export SMTP_APP_PASSWORD="your-app-password"
python scripts/send_email.py "Subject" "Message" person1@example.com person2@example.com
```

## Tests

```bash
pytest
```

20 tests cover revenue parsing, data cleaning, zodiac date boundaries (including leap years), file renaming (dry run and overlapping names) and email message building.

## Author

**Pasang Rumba**, Software Engineer, London · [LinkedIn](https://www.linkedin.com/in/pasang-rumba-45a02194/) · [GitHub](https://github.com/Pasangrumba)
