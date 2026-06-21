import json, os

folder = "data/sample_set/26.02_release/01d503d4-449b-46fc-8d78-9085e70d3554/unzipped"   # run this from the scene folder, or set the full path
for f in ["rig_trajectories.json", "sequence_tracks.json", "pose_record.json"]:
    print("=" * 50, f)
    d = json.load(open(os.path.join(folder, f)))
    print("type:", type(d).__name__)
    if isinstance(d, dict):
        print("top-level keys:", list(d.keys()))
        # peek one level deeper
        for k in list(d.keys())[:3]:
            v = d[k]
            print(f"  {k}: {type(v).__name__}", end="")
            if isinstance(v, list):
                print(f" (len {len(v)}), first item: {v[0] if v else None}")
            elif isinstance(v, dict):
                print(f" keys: {list(v.keys())}")
            else:
                print(f" = {v}")
    elif isinstance(d, list):
        print("len:", len(d))
        print("first item:", d[0] if d else None)
