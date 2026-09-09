import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader    # Load the data
from langchain_text_splitters import CharacterTextSplitter                      # chunck the text
#from langchain_openai import OpenAIEmbeddings                                   # embeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
import torch


load_dotenv()

#loading the data 
def load_documents(docs_path = "data"):
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"The specified path '{docs_path}' does not exist.")

    loader = DirectoryLoader(
        path = docs_path,
        glob = "*.txt",
        loader_cls = TextLoader,
        loader_kwargs={'encoding': 'utf-8'}
    )
    documents = loader.load()

    if len(documents) == 0:
        raise FileNotFoundError(f"No text files found in the specified path '{docs_path}'.")   

    for i,doc in enumerate(documents):
        print(f"Document {i+1}: {doc.metadata['source']} - {len(doc.page_content)} characters")
        #print(f'Content : {doc.page_content[:100]}')
    return documents



# chuncking the text
def chunk_data(documents, chunk_size, chunk_overlap): #chunk overlap - num of prevous chunk's words in new one

    text_splitter = CharacterTextSplitter(separator='\n',chunk_size = chunk_size, chunk_overlap = chunk_overlap)
    chunks = text_splitter.split_documents(documents)

    for i,chunk in enumerate(chunks[:5]):
        print(f'chunk {i+1} : {chunk.metadata["source"]} - {len(chunk.page_content)} characters')
        #print(f'content : {chunk.page_content[:100]}')
    if len(chunks) >5:
        print(f'{len(chunks) - 5} more chunks remain')
    return chunks 


#create embeddings and store in vector database

current_device = "cuda" if torch.cuda.is_available() else "cpu"

def create_embeddings(chunks, persist_directory):
    embed_model = HuggingFaceEmbeddings(
        model_name="nomic-ai/nomic-embed-text-v1",
        model_kwargs={"trust_remote_code": True, "device": current_device},
        #encode_kwargs = {'prompt':'search_document'}
    )
    # create chromadb vector db
    vector_db = Chroma.from_documents(
        documents = chunks,
        embedding=embed_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space":'cosine'}
    )
    print(f'Vector database created and persisted at {persist_directory}')
    return vector_db

def main():
    for file in os.listdir('data'):
        if file.endswith('.txt'):
            print('file found')
            
    documents = load_documents(docs_path="data")
    chunks = chunk_data(documents,1,0)
    create_embeddings(chunks, persist_directory='C:\\Users\\ADMIN\\Desktop\\llm_poke_game\\chroma_db')
    

if __name__ == '__main__':
    main()
