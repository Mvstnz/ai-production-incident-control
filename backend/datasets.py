"""The application's exclusively invented manufacturing demo world."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {"SUPPLIER_DELAY": "hero_supplier_delay.json", "MACHINE_BREAKDOWN": "machine_breakdown.json", "QUALITY_ISSUE": "quality_issue.json"}


def dataset_name():
    name = os.getenv("DEMO_DATASET", "fictional-v2")
    if name != "fictional-v2":
        raise ValueError("Unknown demo dataset")
    return name


def load_fixture(kind, dataset=None):
    name = dataset or dataset_name()
    if name != "fictional-v2":
        raise ValueError("Unknown demo dataset")
    folder = ROOT / "fixtures"
    return json.loads((folder / FILES[kind]).read_text(encoding="utf-8"))


def demo_clock():
    return load_fixture("SUPPLIER_DELAY")["analysis_time"]


def demo_timezone():
    return load_fixture("SUPPLIER_DELAY")["business_timezone"]
