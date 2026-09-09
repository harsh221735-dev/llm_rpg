from langchain_chroma import Chroma
import torch
from langchain_huggingface import HuggingFaceEmbeddings

# loading main model
from llama_cpp import Llama
# 1. Load the model into your 8GB RAM CPU
# we set n_ctx to 2048 to save RAM memory on your system
llm = Llama(
    model_path="C:\\Users\\ADMIN\\Desktop\\llm_poke_game\\qwen2.5-3b-instruct-q4_k_m.gguf",
    n_ctx=2048,  # Context window size
    n_threads=4  # Number of CPU cores to use (adjust based on your CPU)
)

#loading embedding model and database
current_device = 'cuda' if torch.cuda.is_available() else 'cpu'
persist_directory = 'C:\\Users\\ADMIN\\Desktop\\llm_poke_game\\chroma_db'

embed_model = HuggingFaceEmbeddings(
    model_name = 'nomic-ai/nomic-embed-text-v1',
    model_kwargs = {'trust_remote_code': True, 'device':current_device}
    #encode_kwargs = {'prompt':'search_document'}
)

db = Chroma(
    persist_directory=persist_directory,
    embedding_function= embed_model,
    collection_metadata={"hnsw:space":'cosine'}
)
def loaded_models():
    return llm,db