from huggingface_hub import snapshot_download

# We use the AWQ version because it fits perfectly in your 16GB 4060 Ti
# while leaving room for the context window.
model_id = "TheBloke/Mistral-7B-Instruct-v0.2-AWQ"

print(f"⬇️ Downloading {model_id} to ./shared_models...")
snapshot_download(
    repo_id=model_id,
    local_dir="./shared_models/TheBloke/Mistral-7B-Instruct-v0.2-AWQ",
    local_dir_use_symlinks=False
)
print("✅ Download Complete. Ready for Docker.")