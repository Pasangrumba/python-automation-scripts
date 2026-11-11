"""Work out a person's zodiac sign from their birth date and append the result to a CSV with pandas.

Usage:
    python scripts/zodiac_sign.py "Pasang" 1986-03-08
"""
import argparse
import os
from datetime import date

import pandas as pd

# (sign, start month, start day) in calendar order; a sign runs until the next one starts
SIGNS = [
    ("Capricorn", 1, 1), ("Aquarius", 1, 20), ("Pisces", 2, 19), ("Aries", 3, 21),
    ("Taurus", 4, 20), ("Gemini", 5, 21), ("Cancer", 6, 21), ("Leo", 7, 23),
    ("Virgo", 8, 23), ("Libra", 9, 23), ("Scorpio", 10, 23), ("Sagittarius", 11, 22),
    ("Capricorn", 12, 22),
]


def get_zodiac_sign(day, month):
    """Return the zodiac sign for a day and month, raising ValueError for invalid dates."""
    date(2000, month, day)  # validates the date (2000 is a leap year, so 29 Feb is allowed)
    sign = SIGNS[0][0]
    for name, start_month, start_day in SIGNS:
        if (month, day) >= (start_month, start_day):
            sign = name
    return sign


def save(name, birth_date, path):
    """Append one row to the CSV, creating it with headers if it does not exist."""
    row = pd.DataFrame([{
        "Name": name,
        "BirthDate": birth_date.isoformat(),
        "ZodiacSign": get_zodiac_sign(birth_date.day, birth_date.month),
    }])
    row.to_csv(path, mode="a", header=not os.path.exists(path), index=False)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("name")
    parser.add_argument("birth_date", type=date.fromisoformat, help="YYYY-MM-DD")
    parser.add_argument("--csv", default="output/zodiac_sign_data.csv")
    args = parser.parse_args()

    row = save(args.name, args.birth_date, args.csv)
    print(row.to_string(index=False))
    print(f"Saved to {args.csv}")


if __name__ == "__main__":
    main()
