import os
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import chromadb
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.schema import Document
import warnings

warnings.filterwarnings('ignore')


# Helper function to initialize LLM
def _setup_groq_llm():
    try:
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            print("Error: GROQ_API_KEY environment variable not set. Please set it.")
            return None

        llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=1024
        )
        print("Groq LLM initialized.")
        return llm
    except Exception as e:
        print(f"Error setting up Groq API: {e}")
        return None

# Helper function to load PDF
def load_pdf(pdf_path):
    """
    Loads text from a PDF file.
    Returns a list of Document objects or None if an error occurs.
    """
    documents = []
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if text:
                doc = Document(page_content=text, metadata={"source": pdf_path})
                documents.append(doc)
            else:
                print(f"Warning: No text extracted from {pdf_path}")
                return None

    except PyPDF2.errors.PdfReadError as e:
        print(f"PyPDF2 Error loading PDF '{pdf_path}': {e}. The PDF might be corrupted or malformed or encrypted.")
        return None
    except Exception as e:
        print(f"General Error loading PDF '{pdf_path}': {str(e)}")
        return None

    if documents:
        print(f"PDF '{pdf_path}' loaded successfully! Extracted {len(documents[0].page_content)} characters.")
    else:
        print(f"No documents processed for '{pdf_path}'.")
    return documents

# Helper function to create vectorstore
def _create_vectorstore(documents, collection_name="pdf_chatbot_collection"):
    """
    Creates or loads a Chroma vector store from a list of documents.
    Returns the vectorstore instance.
    """
    print("Creating vector embeddings with Chroma...")

    if not documents:
        print("No documents provided to create vector store.")
        return None

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} text chunks.")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    persist_directory = "./chroma_db"
    os.makedirs(persist_directory, exist_ok=True)
    print(f"Using persistence directory: {persist_directory}")

    client = chromadb.PersistentClient(path=persist_directory)

    try:
        try:
            client.delete_collection(name=collection_name)
            print(f"Deleted existing Chroma collection '{collection_name}' to load new PDF.")
        except Exception as e:
            if "Collection not found" not in str(e):
                print(f"Warning: Could not delete existing collection (might not exist): {e}")

        vectorstore = Chroma.from_documents(
            chunks,
            embeddings,
            client=client,
            collection_name=collection_name,
            persist_directory=persist_directory
        )
        print("Chroma vector store created successfully!")
        return vectorstore

    except Exception as e:
        print(f"Error with ChromaDB during vector store creation: {e}")
        return None
    
# Helper function to setup conversation chain
def _setup_conversation_chain(llm, vectorstore):
    """Sets up and returns the ConversationalRetrievalChain instance."""
    print("🔗 Setting up conversation chain...")

    if llm is None or vectorstore is None:
        print("LLM or Vectorstore not initialized. Cannot set up conversation chain.")
        return None

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    try:
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
            memory=memory,
            return_source_documents=True,
            verbose=False
        )
        print("Conversation chain setup complete!")
        return conversation_chain
    except Exception as e:
        print(f"Error setting up conversation chain: {e}")
        return None

# Main initialization function
def initialize_chatbot(pdf_path):
    """
    Initializes the chatbot with a given PDF.
    Returns the initialized conversation_chain object on success, None on failure.
    """
    print(f"Initializing PDF Chatbot for '{pdf_path}'...")

    llm_instance = _setup_groq_llm()
    if llm_instance is None:
        print("Initialization failed: Groq API setup issue.")
        return None

    documents = load_pdf(pdf_path)
    if not documents:
        print("Initialization failed: PDF loading issue or no text extracted.")
        return None

    vectorstore_instance = _create_vectorstore(documents)
    if vectorstore_instance is None:
        print("Initialization failed: Vector store creation issue.")
        return None

    conversation_chain_instance = _setup_conversation_chain(llm_instance, vectorstore_instance)
    if conversation_chain_instance is None:
        print("Initialization failed: Conversation chain setup issue.")
        return None

    print("Chatbot initialized successfully!")
    return conversation_chain_instance # This is what app.py needs to store

def get_chat_history(conversation_chain_instance):
    """Returns the formatted chat history from a given conversation_chain instance."""
    if conversation_chain_instance is None or not conversation_chain_instance.memory:
        return []

    history = conversation_chain_instance.memory.chat_memory.messages
    formatted_history = []
    for message in history:
        role = "user" if message.type == "human" else "assistant"
        formatted_history.append({"role": role, "content": message.content})
    return formatted_history

def chat_with_pdf(conversation_chain_instance, question):
    """
    Sends a question to the chatbot and returns the response.
    Requires a valid conversation_chain_instance.
    """
    if conversation_chain_instance is None:
        return {"error": "Chatbot not initialized. Please upload a PDF first."}

    try:
        response = conversation_chain_instance({"question": question})
        answer = response.get('answer', "No answer found.")
        source_docs = response.get('source_documents', [])

        sources_info = []
        if source_docs:
            for i, doc in enumerate(source_docs[:2]):
                preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                source_info = doc.metadata.get("source", "Unknown Source")
                sources_info.append({"source": source_info, "content_preview": preview})

        return {"answer": answer, "sources": sources_info}

    except Exception as e:
        print(f"Error during chat: {str(e)}")
        return {"error": f"Error during chat: {str(e)}"}