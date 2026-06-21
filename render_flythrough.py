import sys
import numpy as np
import open3d as o3d
import imageio.v2 as imageio

mesh_path = sys.argv[1]          # unzipped/mesh.ply
traj_path = sys.argv[2]          # positions.npy

# --- camera framing (stable: always looks forward + slightly down) ---
EYE_HEIGHT = 2.0                 # camera height above the path (m)
LOOK_DISTANCE = 8.0              # how far ahead the camera aims (m)
PITCH_DROP = 2.0                 # how far below eye the aim point sits (m) -> downward tilt
SMOOTH = 3                       # frames each side used to smooth the forward direction
UP = [0, 0, 1]                   # [0, 1, 0] if scene is Y-up
FOV = 70.0

# --- clip / length ---
TARGET_FRAMES = 300
BOUNDS_MARGIN = 8.0
MIN_TRI = 2000                   # drop disconnected mesh clusters smaller than this

up_vec = np.array(UP, dtype=float)

positions = np.load(traj_path)
print("Raw poses:", positions.shape)

mesh = o3d.io.read_triangle_mesh(mesh_path)
mesh.compute_vertex_normals()

# remove small floating clusters (debris)
with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Error):
    cl_idx, cl_ntri, _ = mesh.cluster_connected_triangles()
cl_idx, cl_ntri = np.asarray(cl_idx), np.asarray(cl_ntri)
mesh.remove_triangles_by_mask(cl_ntri[cl_idx] < MIN_TRI)
mesh.remove_unreferenced_vertices()
print("Mesh after cleanup:", mesh)

# keep poses inside the reconstructed footprint, then subsample
bbox = mesh.get_axis_aligned_bounding_box()
bmin, bmax = bbox.get_min_bound(), bbox.get_max_bound()
m = BOUNDS_MARGIN
inside = ((positions[:, 0] >= bmin[0] - m) & (positions[:, 0] <= bmax[0] + m) &
          (positions[:, 1] >= bmin[1] - m) & (positions[:, 1] <= bmax[1] + m))
positions = positions[inside]
if len(positions) > TARGET_FRAMES:
    idx = np.linspace(0, len(positions) - 1, TARGET_FRAMES).astype(int)
    positions = positions[idx]
print("Final frame count:", len(positions))
if len(positions) < 2:
    raise SystemExit("Too few poses survived clipping - widen BOUNDS_MARGIN.")

# precompute a smoothed forward (tangent) direction per frame
n = len(positions)
forward = np.zeros((n, 3))
last = np.array([1.0, 0.0, 0.0])
for i in range(n):
    a, b = max(0, i - SMOOTH), min(n - 1, i + SMOOTH)
    v = positions[b] - positions[a]
    norm = np.linalg.norm(v)
    forward[i] = v / norm if norm > 1e-6 else last
    last = forward[i]

W, H = 960, 540
renderer = o3d.visualization.rendering.OffscreenRenderer(W, H)
mat = o3d.visualization.rendering.MaterialRecord()
mat.shader = "defaultLit"
renderer.scene.add_geometry("scene", mesh, mat)
renderer.scene.set_background([0.0, 0.0, 0.0, 1.0])

writer = imageio.get_writer(
    "flythrough.mp4", fps=10, format="FFMPEG",
    codec="libx264", pixelformat="yuv420p", macro_block_size=16,
)

for i in range(n):
    eye = positions[i] + up_vec * EYE_HEIGHT
    center = eye + forward[i] * LOOK_DISTANCE - up_vec * PITCH_DROP
    renderer.setup_camera(FOV, center.tolist(), eye.tolist(), UP)
    frame = np.asarray(renderer.render_to_image())[:, :, :3]
    if i == n // 2:
        imageio.imwrite("sample_frame.png", frame)
    writer.append_data(frame)

writer.close()
print("Saved flythrough.mp4 and sample_frame.png")
