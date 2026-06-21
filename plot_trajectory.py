import sys, json
import numpy as np
import matplotlib.pyplot as plt

traj_json = sys.argv[1]   # unzipped/rig_trajectories.json

def is_4x4(x):
    return (isinstance(x, list) and len(x) == 4
            and all(isinstance(r, list) and len(r) == 4 for r in x)
            and all(isinstance(v, (int, float)) for r in x for v in r))

def collect_matrices(node, out):
    if is_4x4(node):
        out.append(node)
    elif isinstance(node, list):
        for it in node:
            collect_matrices(it, out)
    elif isinstance(node, dict):
        for v in node.values():
            collect_matrices(v, out)

data = json.load(open(traj_json))
mats = []
collect_matrices(data, mats)
positions = np.array([[m[0][3], m[1][3], m[2][3]] for m in mats])
print("Collected", len(positions), "raw poses")

# --- drop global/ECEF outliers: keep poses near the median (local frame) ---
# The real ego path spans well under ~1 km; ECEF junk sits ~1e6 m away.
med = np.median(positions, axis=0)
dist = np.linalg.norm(positions - med, axis=1)
keep = dist < 5000.0
positions = positions[keep]
print("Kept", len(positions), "local-frame poses (dropped",
      int((~keep).sum()), "outliers)")
      
# keep only the longest continuous pass (drops the ~8 inter-segment teleports)
steps = np.linalg.norm(np.diff(positions, axis=0), axis=1)
breaks = np.where(steps > 5.0)[0] + 1
positions = max(np.split(positions, breaks), key=len)
print("Longest continuous segment:", len(positions), "poses")

np.save("positions.npy", positions)

plt.figure(figsize=(6, 6))
plt.plot(positions[:, 0], positions[:, 1], "-o", ms=2)
plt.title("Ego trajectory (top-down)")
plt.xlabel("X"); plt.ylabel("Y"); plt.axis("equal"); plt.grid(True)
plt.savefig("ego_trajectory.png", dpi=150, bbox_inches="tight")
print("Saved ego_trajectory.png and positions.npy")
