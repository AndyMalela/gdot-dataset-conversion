#!/usr/bin/env python3
"""Re-digitize intersection 7065 directly from the georeferenced aerial, instead
of trusting OSM (whose Piedmont-north leg is un-tagged / wrong).

The junction center and one centerline point per leg were picked by eye on the
1000x1000 Esri World Imagery tile (satellite_ref.png) whose geographic bounds are
known, so pixels -> lon/lat -> local meters. Each approach is then rebuilt as a
straight 100 m leg on that measured bearing, with lane counts + turn lanes read
from the aerial / Google Maps (and the correctly-tagged OSM south & Peachtree
legs). Writes plain node/edge/connection XML for netconvert.

Ground-truth lane config (inbound toward J / outbound away):
  Piedmont N : 4 in / 2 out     Piedmont S : 4 in / 2 out
  Peachtree NE: 5 in / 3 out    Peachtree SW: 5 in / 3 out
"""
import math
import xml.etree.ElementTree as ET

# --- georeference of the satellite tile (same bbox used everywhere) ---
W, S, E, N = -84.373350, 33.842115, -84.369458, 33.845349
def px2lonlat(px, py):
    return W + px / 1000 * (E - W), N - py / 1000 * (N - S)

# --- aerial picks (pixels, y down): junction + one point per leg centerline ---
# NE re-picked lower (bearing ~55 deg) so Peachtree NE rides the travel-lane
# centerline instead of the upper edge (it was sitting too high vs the south leg).
J_PX = (608, 582)
LEG_PX = {"N": (492, 250), "S": (712, 905), "NE": (857, 414), "SW": (250, 780)}

# inbound / outbound lane counts per leg
LANES = {"N": (4, 2), "S": (4, 2), "NE": (5, 3), "SW": (5, 3)}
# per-leg approach length, meters from J (junction center, not the stop bar):
# bottom (S) + left (SW) shortened to 70 m, right (NE) lengthened to 105 m,
# top (N) stays the default 100 m.
LEG_LEN = {"N": 100.0, "S": 70.0, "NE": 105.0, "SW": 70.0}
SPEED = 15.6                  # ~35 mph
NAME = {"N": "Piedmont Rd NE", "S": "Piedmont Rd NE",
        "NE": "Peachtree Rd NE", "SW": "Peachtree Rd NE"}
PRIO = {"N": 10, "S": 10, "NE": 12, "SW": 12}   # Peachtree = major

# --- local metric frame centered on J (equirectangular, fine at this scale) ---
lonJ, latJ = px2lonlat(*J_PX)
mlon = math.cos(math.radians(latJ)) * 111320.0
mlat = 111320.0
def to_xy(px):
    lon, lat = px2lonlat(*px)
    return (lon - lonJ) * mlon, (lat - latJ) * mlat

def unit(px):
    vx, vy = to_xy(px)
    d = math.hypot(vx, vy)
    return vx / d, vy / d

# Piedmont N & S share ONE straight axis through J (collinear), so the through
# lanes line up instead of shearing. Axis = direction from the S pick to the N
# pick; place nN/nS on that same axis, each at its own LEG_LEN distance.
sx, sy = to_xy(LEG_PX["S"]); nx, ny = to_xy(LEG_PX["N"])
avx, avy = nx - sx, ny - sy
am = math.hypot(avx, avy); axu = (avx / am, avy / am)

outer = {}
outer["N"] = (axu[0] * LEG_LEN["N"], axu[1] * LEG_LEN["N"])
outer["S"] = (-axu[0] * LEG_LEN["S"], -axu[1] * LEG_LEN["S"])
for leg in ("NE", "SW"):                 # Peachtree legs keep their own picks
    ux, uy = unit(LEG_PX[leg])
    outer[leg] = (ux * LEG_LEN[leg], uy * LEG_LEN[leg])
for leg in ("N", "S", "NE", "SW"):
    ox, oy = outer[leg]
    brg = (math.degrees(math.atan2(ox, oy)) + 360) % 360
    print(f"leg {leg:2s} bearing={brg:5.1f} deg  outer=({ox:6.1f},{oy:6.1f})")

# --- N ("top") leg inbound: dedicated left-turn pocket starting 40 m before
# the stop bar (rather than a full-length left lane). nNleft sits on the same
# straight N/S axis (axu) as nN, just closer to J.
N_LEFT_DIST = 40.0      # where the dedicated left-turn pocket begins
nNleft_xy = (axu[0] * N_LEFT_DIST, axu[1] * N_LEFT_DIST)

# --- write nodes ---
OFF = 150.0  # keep coords positive
nodes = ET.Element("nodes")
ET.SubElement(nodes, "node", id="J", x=f"{OFF:.2f}", y=f"{OFF:.2f}", type="traffic_light")
for leg, (x, y) in outer.items():
    ET.SubElement(nodes, "node", id=f"n{leg}", x=f"{x+OFF:.2f}", y=f"{y+OFF:.2f}",
                  type="priority")
ET.SubElement(nodes, "node", id="nNleft", x=f"{nNleft_xy[0]+OFF:.2f}", y=f"{nNleft_xy[1]+OFF:.2f}",
              type="priority")
ET.ElementTree(nodes).write("7065twinv2/plain/7065.nod.xml", encoding="UTF-8",
                            xml_declaration=True)

# --- write edges (in + out per leg) ---
edges = ET.Element("edges")
for leg in LEG_PX:
    nin, nout = LANES[leg]
    if leg == "N":
        # inbound N split into 2 segments instead of one straight N_in:
        #   N_far  (100m->40m, 3 lanes) -- no left lane yet
        #   N_near (40m->0m,   4 lanes) -- the left-turn pocket begins here
        ET.SubElement(edges, "edge", id="N_far", attrib={"from": "nN", "to": "nNleft",
            "numLanes": "3", "speed": f"{SPEED}", "priority": str(PRIO[leg]),
            "name": NAME[leg], "spreadType": "roadCenter"})
        ET.SubElement(edges, "edge", id="N_near", attrib={"from": "nNleft", "to": "J",
            "numLanes": "4", "speed": f"{SPEED}", "priority": str(PRIO[leg]),
            "name": NAME[leg], "spreadType": "roadCenter"})
        ET.SubElement(edges, "edge", id=f"{leg}_out", attrib={"from": "J", "to": f"n{leg}",
            "numLanes": str(nout), "speed": f"{SPEED}", "priority": str(PRIO[leg]),
            "name": NAME[leg], "spreadType": "roadCenter"})
    else:
        ET.SubElement(edges, "edge", id=f"{leg}_in", attrib={"from": f"n{leg}", "to": "J",
            "numLanes": str(nin), "speed": f"{SPEED}", "priority": str(PRIO[leg]),
            "name": NAME[leg], "spreadType": "roadCenter"})
        ET.SubElement(edges, "edge", id=f"{leg}_out", attrib={"from": "J", "to": f"n{leg}",
            "numLanes": str(nout), "speed": f"{SPEED}", "priority": str(PRIO[leg]),
            "name": NAME[leg], "spreadType": "roadCenter"})
ET.ElementTree(edges).write("7065twinv2/plain/7065.edg.xml", encoding="UTF-8",
                            xml_declaration=True)
print("wrote plain/7065.nod.xml + plain/7065.edg.xml")

# --- explicit lane-use assignment for the two Peachtree approaches ---
# (N_in / S_in are left to netconvert's default: 1 right + 2 straight + 1 left)
# NE ("right leg", 5 lanes, index 0=rightmost .. 4=leftmost): 2 left, 3 straight.
# No right-turn lane -- the real channelized free-right is a separate slip lane
# well upstream of this junction and is intentionally not modeled here.
# SW ("left leg", 5 lanes): 2 left, 2 straight, 1 shared straight/right.
conns = ET.Element("connections")
for from_e, to_left, to_straight, lefts, straights in (
    ("NE_in", "S_out", "SW_out", (3, 4), (0, 1, 2)),
    ("SW_in", "N_out", "NE_out", (3, 4), (1, 2)),
):
    for i, lane in enumerate(lefts):
        ET.SubElement(conns, "connection", attrib={"from": from_e, "to": to_left,
            "fromLane": str(lane), "toLane": str(i)})
    for lane in straights:
        ET.SubElement(conns, "connection", attrib={"from": from_e, "to": to_straight,
            "fromLane": str(lane), "toLane": str(lane)})
# SW_in lane 0: shared straight (-> NE_out) / right (-> S_out)
ET.SubElement(conns, "connection", attrib={"from": "SW_in", "to": "NE_out", "fromLane": "0", "toLane": "0"})
ET.SubElement(conns, "connection", attrib={"from": "SW_in", "to": "S_out", "fromLane": "0", "toLane": "0"})

# N leg (top): nNleft (40 m) -- the 3 continuing lanes feed N_near's lanes
# 0-2 as-is; N_near's new lane 3 (the left pocket) has no upstream feed here
# (reachable via in-lane lane-changing once on N_near); netconvert's default
# lane-use at J then applies to N_near same as it would to a plain 4-lane N_in.
ET.SubElement(conns, "connection", attrib={"from": "N_far", "to": "N_near", "fromLane": "0", "toLane": "0"})
ET.SubElement(conns, "connection", attrib={"from": "N_far", "to": "N_near", "fromLane": "1", "toLane": "1"})
ET.SubElement(conns, "connection", attrib={"from": "N_far", "to": "N_near", "fromLane": "2", "toLane": "2"})

ET.ElementTree(conns).write("7065twinv2/plain/7065.con.xml", encoding="UTF-8",
                            xml_declaration=True)
print("wrote plain/7065.con.xml")
