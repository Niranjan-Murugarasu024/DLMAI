"""
Regression test for BUG-006 (second external review round): the
inheritance resolver only resolved one level of parent in a single pass
over the parent_map dict. A grandchild district (carved from a district
that was itself carved from another) only inherited correctly if its
immediate parent happened to be processed FIRST in dict iteration order
-- which depends on row order in the district master CSV, which has no
guaranteed relationship to actual district lineage (e.g. "Bapatla" sorts
alphabetically before its own parent "Guntur"). Fixed with a fixpoint
loop that resolves any chain depth regardless of row order.
"""

from district_crosswalk import InheritanceResolver


class FakeDistrict:
    def __init__(self, code, parent):
        self.lgd_code = code
        self.parent_lgd_code = parent


class FakeCrosswalk:
    def __init__(self, districts):
        self.districts = districts


print("=" * 78)
print("TEST 1 -- parent listed BEFORE child (the case that worked even before the fix)")
print("=" * 78)
xwalk1 = FakeCrosswalk([FakeDistrict("A", None), FakeDistrict("B", "A"), FakeDistrict("C", "B")])
filled1, mask1 = InheritanceResolver(xwalk1).fill_missing({"A": 100.0, "B": None, "C": None})
print(f"  filled = {filled1}")
assert filled1 == {"A": 100.0, "B": 100.0, "C": 100.0}

print()
print("=" * 78)
print("TEST 2 -- child listed BEFORE parent (the realistic failure case -- this is the actual bug)")
print("=" * 78)
xwalk2 = FakeCrosswalk([FakeDistrict("A", None), FakeDistrict("C", "B"), FakeDistrict("B", "A")])
filled2, mask2 = InheritanceResolver(xwalk2).fill_missing({"A": 100.0, "B": None, "C": None})
print(f"  filled = {filled2}")
assert filled2["C"] == 100.0, "grandchild must inherit transitively regardless of row order"
print(f"  mask = {mask2}")
print("  PASS -- C correctly inherits via B from A, even though listed before its own parent")

print()
print("=" * 78)
print("TEST 3 -- three-generation chain in REVERSE order (D <- C <- B <- A, listed D,C,B,A)")
print("=" * 78)
xwalk3 = FakeCrosswalk([
    FakeDistrict("D", "C"), FakeDistrict("C", "B"), FakeDistrict("B", "A"), FakeDistrict("A", None),
])
filled3, mask3 = InheritanceResolver(xwalk3).fill_missing({"A": 77.0, "B": None, "C": None, "D": None})
print(f"  filled = {filled3}")
assert filled3 == {"A": 77.0, "B": 77.0, "C": 77.0, "D": 77.0}
print("  PASS -- three-generation chain resolved correctly in fully reversed order")

print()
print("=" * 78)
print("TEST 4 -- a parent that genuinely has no data leaves the chain correctly unresolved")
print("=" * 78)
filled4, mask4 = InheritanceResolver(xwalk1).fill_missing({"A": None, "B": None, "C": None})
print(f"  filled = {filled4}, mask = {mask4}")
assert filled4 == {"A": None, "B": None, "C": None}
assert all(v == "still_missing" for v in mask4.values())
print("  PASS -- correctly left missing, not fabricated, when even the root has no data")

print()
print("ALL CHECKS PASSED")
