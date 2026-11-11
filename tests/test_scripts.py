import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from bulk_file_renamer import rename_files  # noqa: E402
from company_revenue_etl import parse_number, transform  # noqa: E402
from send_email import build_message  # noqa: E402
from zodiac_sign import get_zodiac_sign  # noqa: E402


@pytest.mark.parametrize("day, month, expected", [
    (8, 3, "Pisces"), (21, 3, "Aries"), (1, 1, "Capricorn"), (31, 12, "Capricorn"),
    (19, 1, "Capricorn"), (20, 1, "Aquarius"), (29, 2, "Pisces"), (23, 7, "Leo"),
])
def test_zodiac_boundaries(day, month, expected):
    assert get_zodiac_sign(day, month) == expected


def test_zodiac_rejects_invalid_date():
    with pytest.raises(ValueError):
        get_zodiac_sign(31, 2)


@pytest.mark.parametrize("text, expected", [
    ("648,125", 648125.0), ("5.5%", 5.5), ("−2.1%", -2.1), ("611,289[1]", 611289.0), ("n/a", None),
])
def test_parse_number(text, expected):
    assert parse_number(text) == expected


def test_transform_drops_invalid_rows():
    raw = pd.DataFrame([
        {"Rank": "1", "Name": "A", "Industry": "Retail", "Revenue": "648,125",
         "RevenueGrowth": "6.0%", "Headquarters": "X"},
        {"Rank": "2", "Name": "B", "Industry": "Tech", "Revenue": "n/a",
         "RevenueGrowth": "1%", "Headquarters": "Y"},
    ])
    clean = transform(raw)
    assert list(clean["Name"]) == ["A"]
    assert clean.iloc[0]["RevenueUSDm"] == 648125.0


def test_rename_files(tmp_path):
    for name in ["b.txt", "a.txt", "keep.csv"]:
        (tmp_path / name).write_text("x")
    renames = rename_files(str(tmp_path), ".txt", "file")
    assert renames == [("a.txt", "file_1.txt"), ("b.txt", "file_2.txt")]
    assert sorted(os.listdir(tmp_path)) == ["file_1.txt", "file_2.txt", "keep.csv"]


def test_rename_dry_run_changes_nothing(tmp_path):
    (tmp_path / "a.txt").write_text("x")
    rename_files(str(tmp_path), ".txt", "file", dry_run=True)
    assert os.listdir(tmp_path) == ["a.txt"]


def test_rename_keeps_every_file_when_names_overlap(tmp_path):
    for name, content in [("a.txt", "A"), ("b.txt", "B"), ("file_2.txt", "OLD2")]:
        (tmp_path / name).write_text(content)
    rename_files(str(tmp_path), ".txt", "file")
    contents = sorted((tmp_path / f).read_text() for f in os.listdir(tmp_path))
    assert sorted(os.listdir(tmp_path)) == ["file_1.txt", "file_2.txt", "file_3.txt"]
    assert contents == ["A", "B", "OLD2"]


def test_rename_refuses_to_overwrite_other_files(tmp_path):
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "file_1.txt.bak").write_text("x")
    os.mkdir(tmp_path / "file_1.txt")  # a folder with the target name is not renamed, so it clashes
    with pytest.raises(FileExistsError):
        rename_files(str(tmp_path), ".txt", "file")


def test_build_message():
    msg = build_message("me@example.com", ["a@example.com", "b@example.com"], "Hi", "Body")
    assert msg["To"] == "a@example.com, b@example.com"
    assert msg["Subject"] == "Hi"
