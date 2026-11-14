"""Offline test with synthetic series (no network). Run: python pipeline/tests/test_offline.py"""
import sys, pathlib, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import fetchers, run
random.seed(3)
def fake(source, code):
    y = list(range(1995, 2025)); v = 5.0; out = {}
    for i in y:
        v = 0.6 * v + 2 + random.gauss(0, 0.8); out[i] = round(v if code != "PA.NUS.FCRF" else 40 + i - 1995 + random.gauss(0, 1), 3)
    return out, "https://api.worldbank.org/test/" + code
cache = {}
def stable(source, code):
    code = "FP.CPI.TOTL.ZG" if code == "PCPIPCH" else code
    if code not in cache: cache[code] = fake(source, code)
    return cache[code]
fetchers.get = stable
run.main(force_topic="inflation")
