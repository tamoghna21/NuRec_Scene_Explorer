import numpy as np
import matplotlib.pyplot as plt
from pyxodr.road_objects.network import RoadNetwork

positions = np.load("positions.npy")
net = RoadNetwork("data/sample_set/26.02_release/01d503d4-449b-46fc-8d78-9085e70d3554/unzipped/map.xodr")   # adjust path to your map.xodr

fig, ax = plt.subplots(figsize=(8, 8))

rx_min = ry_min = 1e18
rx_max = ry_max = -1e18
for road in net.get_roads():
    rl = road.reference_line                 # Nx2 array
    ax.plot(rl[:, 0], rl[:, 1], color="0.7", lw=0.6, zorder=1)
    rx_min, rx_max = min(rx_min, rl[:, 0].min()), max(rx_max, rl[:, 0].max())
    ry_min, ry_max = min(ry_min, rl[:, 1].min()), max(ry_max, rl[:, 1].max())

ax.plot(positions[:, 0], positions[:, 1], "-", color="crimson", lw=2,
        zorder=3, label="ego path")
ax.scatter(*positions[0, :2],  c="green", s=45, zorder=4, label="start")
ax.scatter(*positions[-1, :2], c="black", s=45, zorder=4, label="end")

ax.set_aspect("equal"); ax.legend()
ax.set_title("Ego trajectory over OpenDRIVE map")
ax.set_xlabel("X"); ax.set_ylabel("Y")
plt.savefig("trajectory_on_map.png", dpi=150, bbox_inches="tight")
print("Saved trajectory_on_map.png")

# diagnostic: do map and trajectory share a frame?
print(f"road  X [{rx_min:.1f}, {rx_max:.1f}]  Y [{ry_min:.1f}, {ry_max:.1f}]")
print(f"traj  X [{positions[:,0].min():.1f}, {positions[:,0].max():.1f}]"
      f"  Y [{positions[:,1].min():.1f}, {positions[:,1].max():.1f}]")

# zoomed view around the trajectory
pad = 30
ax.set_xlim(positions[:, 0].min() - pad, positions[:, 0].max() + pad)
ax.set_ylim(positions[:, 1].min() - pad, positions[:, 1].max() + pad)
plt.savefig("trajectory_on_map_zoom.png", dpi=150, bbox_inches="tight")
print("Saved trajectory_on_map_zoom.png")
