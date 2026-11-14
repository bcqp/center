"""Fail-closed validation: every variable fetched twice and compared; optional second-source cross-check."""
import fetchers

def fetch_validated(var):
    a, url = fetchers.get(var["source"], var["code"])
    b, _ = fetchers.get(var["source"], var["code"])
    if a != b:
        raise ValueError("two fetches of %s disagree" % var["code"])
    if len(a) < 15:
        raise ValueError("too few observations for %s (%d)" % (var["code"], len(a)))
    return a, url

def cross_check(series, spec, log):
    """Compare overlapping years with a second official source. Returns True only if within tolerance."""
    if not spec: return True
    other, url = fetchers.get(spec["source"], spec["code"])
    common = sorted(set(series) & set(other))[-6:]
    if len(common) < 3:
        raise ValueError("cross-check has no overlap")
    worst = max(abs(series[y] - other[y]) for y in common)
    log.append("cross-check %s vs %s: max gap %.2f over %s-%s" % (spec["code"], spec["source"], worst, common[0], common[-1]))
    if worst > spec["tolerance"]:
        raise ValueError("sources disagree by %.2f (tolerance %.2f)" % (worst, spec["tolerance"]))
    return True
