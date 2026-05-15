"""Normalization utilities for prescription fields."""

import re

FREQ_MAP = {
    "qd": "once_daily",
    "od": "once_daily",
    "bid": "twice_daily",
    "tid": "three_times_daily",
    "qid": "four_times_daily",
    "qhs": "every_night",
    "qn": "every_night",
    "prn": "as_needed",
}

ROUTE_MAP = {
    "po": "oral",
    "oral": "oral",
    "iv": "intravenous",
    "im": "intramuscular",
    "sc": "subcutaneous",
    "inh": "inhalation",
    "topical": "topical",
}

def normalize_space(x):
    if x is None:
        return None
    return re.sub(r"\s+", " ", str(x)).strip()

def normalize_frequency(x):
    x = normalize_space(x)
    if not x: return x
    return FREQ_MAP.get(x.lower().replace(".", ""), x.lower())

def normalize_route(x):
    x = normalize_space(x)
    if not x: return x
    return ROUTE_MAP.get(x.lower().replace(".", ""), x.lower())

def normalize_unit(x):
    x = normalize_space(x)
    if not x: return x
    x = x.replace("毫克", "mg").replace("克", "g").replace("毫升", "ml")
    x = re.sub(r"\bMG\b", "mg", x)
    x = re.sub(r"\bML\b", "ml", x)
    return x
