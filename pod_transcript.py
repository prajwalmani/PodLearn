# Check Listen Notes API and AssemblyAI API documentation for endpoints and API keys
# 
# For Listen Notes API:
# Ensure you have an API key from Listen Notes. Documentation for endpoints and API keys can be found at:
# https://www.listennotes.com/api/docs/
# 
# For AssemblyAI API:
# Ensure you have an API key from AssemblyAI. Documentation for endpoints and API keys can be found at:
# https://www.assemblyai.com/app

import requests
import os
import time
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec




# intilaize the pinecone vector database
load_dotenv()

# Initialize Pinecone
pc=Pinecone(api_key=os.environ.get("PINECONE_API_KEY"), environment="gcp-starter")
pinecone_index_name = os.environ.get("INDEX_NAME")

# Check if the index exists, otherwise create it
if pinecone_index_name not in pc.list_indexes().names():
    index=pc.create_index(
        name=pinecone_index_name,
        # The huggingface embedding gives use out of 384 sp the dimension will be 384 
        dimension=384,  
        metric="cosine", 
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
else:
    print("Alreday created the index")
    index=pc.Index(pinecone_index_name)

# Initialize Hugging Face embeddings
embeddings_model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)


# Function to add documents to Pinecone vector store
def add_to_vectore_database(episode_id,transcript): 
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
    )

    chunks = text_splitter.split_text(transcript)

    docs = [
    Document(
        page_content=chunk,
        metadata={"episode_id": episode_id}
    ) for chunk in chunks
]


    vector_store = PineconeVectorStore(
        index_name=pinecone_index_name,
        embedding=embeddings,
        text_key="text",
    )
    response=vector_store.add_documents(documents=docs)
    if response:
        print("Documents added successfully.")
    else:
        print(f"Failed to add documents: {response.error_message}")

# Function to check if episode exists in Pinecone
def check_episode_exists_in_pinecone(episode_id):
    try:
        vectorstore = PineconeVectorStore(index_name=pinecone_index_name, embedding=embeddings)
        
        search_filter = {"episode_id": episode_id}

        retriever = vectorstore.as_retriever(search_kwargs={
            "filter": search_filter
        })

        results = retriever.get_relevant_documents("")

        if results:
            print(f"Episode ID {episode_id} is present in the index.")
            return True
        else:
            print(f"Episode ID {episode_id} is not found in the index.")
            return False

    except Exception as e:
        print(f"Error checking episode in Pinecone: {e}")
        return False  # Handle error gracefully




def main():
    # Define API endpoints
    url_episodes_endpoint='https://listen-api.listennotes.com/api/v2/episodes'
    transcript_endpoint = "https://api.assemblyai.com/v2/transcript"

    #Episode ID for the episode to process from listen notes
    #this episode talks about how self care is making worst of us
    episode_id='856027fd92734ebf928aa6b07e9813c8'



    if not check_episode_exists_in_pinecone(episode_id):
        # If transcript does not exist, fetch and transcribe the episode

        try: 
            # code get audio url from listen notes api
            headers = {
            'X-ListenAPI-Key':os.getenv('LISTEN_NOTES_API_KEY')
            }

            url = f"{url_episodes_endpoint}/{episode_id}"

            response = requests.request('GET', url, headers=headers)
            data = response.json()
            audio_url = data['audio']

            transcript_request = {
                'audio_url': audio_url,
                'auto_chapters': False
            }

            headers = {
                "authorization": os.getenv('aai.settings.api_key'),
                "content-type": "application/json"
            }

            transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
            transcript_id = transcript_response.json()['id']
            polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
            
            # Poll for transcription completion

            while True:
                transcription_result = requests.get(polling_endpoint, headers=headers).json()

                if transcription_result['status'] == 'completed' and transcription_result['text'] is not None:
                    transcript_text=transcription_result['text']
                    # Insert episode details into the database
                    add_to_vectore_database(episode_id,transcript_text)
                    break
                elif transcription_result['status'] == 'error':
                    raise RuntimeError(f"Transcription failed: {transcription_result['error']}")

                else:
                    time.sleep(3)
        except Exception as e:
            print(f"Error occurred: {e}")
            raise SystemExit(1)

    else:
            print("Episode already in the database")


if __name__ == "__main__":
    main()








    



