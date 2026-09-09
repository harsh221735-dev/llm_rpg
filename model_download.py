from huggingface_hub import hf_hub_download

hf_hub_download(
    repo_id="Qwen/Qwen2.5-3B-Instruct-GGUF",
    filename="qwen2.5-3b-instruct-q4_k_m.gguf",
    local_dir="C:\\Users\\ADMIN\\Desktop\\llm_poke_game",  # Change to your folder path
    local_dir_use_symlinks=False
)
