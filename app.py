from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import secrets
import logging
from pdf_chatbot import initialize_chatbot, chat_with_pdf, get_chat_history

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploaded_pdfs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app.chatbot_instance = None 

@app.route('/')
def index():
    logger.info("Serving index.html")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    logger.info("Received PDF upload request.")
    if 'pdf_file' not in request.files:
        logger.warning("No file part in upload request.")
        return jsonify({"success": False, "message": "No file part"}), 400

    file = request.files['pdf_file']

    if file.filename == '':
        logger.warning("No selected file in upload request.")
        return jsonify({"success": False, "message": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(pdf_path)
            logger.info(f"File '{filename}' saved to: {pdf_path}")

            # Initialize the chatbot and store the returned instance
            initialized_chain = initialize_chatbot(pdf_path)
            
            if initialized_chain:
                app.chatbot_instance = initialized_chain # Store the chain directly here
                session['current_pdf_path'] = pdf_path # Still store path in session

                logger.info(f"Chatbot initialized and '{filename}' path stored in session.")
                
                # Clear chat history using the *stored* instance
                if app.chatbot_instance.memory:
                    app.chatbot_instance.memory.clear()
                    logger.info("Chat history cleared for new PDF.")

                return jsonify({"success": True, "message": "PDF uploaded and processed successfully!"})
            else:
                os.remove(pdf_path)
                logger.error(f"Failed to initialize chatbot for '{filename}'. Deleted uploaded file.")
                return jsonify({"success": False, "message": "Failed to process PDF. Please check the file content."}), 500
        except Exception as e:
            logger.exception(f"Error during file upload or processing for '{filename}'.")
            return jsonify({"success": False, "message": f"Server error during PDF processing: {str(e)}"}), 500
    else:
        logger.warning(f"Invalid file type uploaded: {file.filename}")
        return jsonify({"success": False, "message": "Invalid file type. Please upload a PDF."}), 400

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    logger.info(f"Received chat message: '{user_message}'")

    if not user_message:
        logger.warning("No message provided in chat request.")
        return jsonify({"success": False, "message": "No message provided"}), 400
    
    if app.chatbot_instance is None and 'current_pdf_path' in session:
        pdf_path = session['current_pdf_path']
        logger.info(f"Chatbot instance missing in app.py's state. Attempting to re-initialize with PDF from session: {pdf_path}")
        re_initialized_chain = initialize_chatbot(pdf_path) # Call initialize_chatbot to get a new chain
        
        if re_initialized_chain:
            app.chatbot_instance = re_initialized_chain # Store the newly initialized chain
            logger.info("Chatbot successfully re-initialized from session PDF path and stored.")
        else:
            logger.error("Failed to re-initialize chatbot from session PDF path.")
            session.pop('current_pdf_path', None) # Clear session path to force re-upload
            return jsonify({"success": False, "message": "Chatbot re-initialization failed. Please re-upload the PDF."}), 500
            
    if app.chatbot_instance is None: 
        logger.warning("Chat request before PDF upload or chatbot initialization (final check for app.chatbot_instance).")
        return jsonify({"success": False, "message": "Please upload a PDF first."}), 400

    try:
        # Pass the actual chatbot instance to the chat_with_pdf function
        response = chat_with_pdf(app.chatbot_instance, user_message) 
        if response.get('error'):
            logger.error(f"Error from chat_with_pdf: {response['error']}")
            return jsonify({"success": False, "message": response['error']}), 500
        
        logger.info("Successfully received response from chatbot.")
        return jsonify({"success": True, "response": response})
    except Exception as e:
        logger.exception(f"Unhandled error during chat for message: '{user_message}'")
        return jsonify({"success": False, "message": f"An unexpected server error occurred during chat: {str(e)}"}), 500

@app.route('/history', methods=['GET'])
def get_history():
    logger.info("Fetching chat history.")
    # Pass the actual chatbot instance to get_chat_history
    history = get_chat_history(app.chatbot_instance) 
    return jsonify({"success": True, "history": history})

@app.route('/check_groq_api')
def check_groq_api():
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        return jsonify({"status": "GROQ_API_KEY is set."})
    else:
        return jsonify({"status": "GROQ_API_KEY is NOT set. Please set it as an environment variable."})

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000)
    logger.info("Flask application finished.")