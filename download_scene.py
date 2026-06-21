from huggingface_hub import snapshot_download

REPO = "nvidia/PhysicalAI-Autonomous-Vehicles-NuRec"

# A scene id from the dataset. Releases update over time, so browse the
# "Files" tab on the HF page and confirm/replace this path if needed.
#SCENE = "sample_set/25.07_release/Batch0002/001b28cb-b8f7-4627-ae65-fda88612d5bf"
SCENE = "sample_set/26.02_release/01d503d4-449b-46fc-8d78-9085e70d3554"


path = snapshot_download(
    repo_id=REPO,
    repo_type="dataset",
    allow_patterns=f"{SCENE}/*",
    local_dir="data",
)
print("Downloaded into:", path)
