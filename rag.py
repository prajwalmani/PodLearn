import pinecone
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings

# Define the vector store with which to perform a semantic search against
# the Pinecone vector database
pinecone.init(
    api_key=os.environ.get("PINECONE_API_KEY"), environment="gcp-starter"
)
pinecone_index = pinecone.Index(os.environ.get("INDEX_NAME"), pool_threads=4)
vector_store = Pinecone(
    index=pinecone_index,
    embedding=OpenAIEmbeddings(),
    text_key="text",
)

# Define the retrieval chain that will perform the steps in RAG
# with conversation memory as outlined above.
chain = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(), retriever=vector_store.as_retriever()
)

# Call the chain passing in the current question and the chat history
response = chain({"question": query, "chat_history": chat_history})["answer"]