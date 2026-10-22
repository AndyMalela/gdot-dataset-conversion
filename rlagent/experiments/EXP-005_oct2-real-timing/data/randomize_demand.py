"""Exact-count random arrivals: each 5-min flow of N vehicles becomes N vehicles with departure
times drawn uniformly at random inside that 5 minutes (fixed seed). Counts per movement per bin
are unchanged (fidelity); only the even spacing of SUMO's <flow number=N> is replaced by random
arrivals, which leaves realistic gaps in opposing traffic for permissive left turns.

  python3 randomize_demand.py in.rou.xml out.rou.xml [impatience] [seed]"""
import random
import sys
import xml.etree.ElementTree as ET


def main(src, dst, impatience=None, seed=12345):
    rng = random.Random(seed)
    root = ET.parse(src).getroot()
    vtype = root.find("vType")
    if impatience is not None:
        vtype.set("impatience", str(impatience))
    vehs = []
    for f in root.iter("flow"):
        b, e, n = float(f.get("begin")), float(f.get("end")), int(f.get("number"))
        for i in range(n):
            vehs.append((round(rng.uniform(b, e), 2), f"{f.get('id')}.{i}", f))
    vehs.sort()
    L = ["<routes>", "  " + ET.tostring(vtype, encoding="unicode").strip()]
    for t, vid, f in vehs:
        L.append(f'  <trip id="{vid}" type="{f.get("type")}" depart="{t}" from="{f.get("from")}" '
                 f'via="{f.get("via")}" to="{f.get("to")}" departLane="{f.get("departLane")}" '
                 f'departSpeed="{f.get("departSpeed")}"/>')
    L.append("</routes>")
    open(dst, "w").write("\n".join(L) + "\n")
    print(f"{len(vehs)} vehicles -> {dst}")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], float(a[2]) if len(a) > 2 else None, int(a[3]) if len(a) > 3 else 12345)
