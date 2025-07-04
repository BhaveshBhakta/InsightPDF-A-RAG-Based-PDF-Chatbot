document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const pdfFile = document.getElementById('pdfFile');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadStatus = document.getElementById('uploadStatus');

    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatHistoryDiv = document.getElementById('chatHistory');

    // Function to add a message to the chat history
    function addMessage(role, content, sources = []) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', role);

        const contentParagraph = document.createElement('p');
        contentParagraph.innerHTML = role === 'user' ? `🧑 You: ${content}` : `🤖 Assistant: ${content}`;
        messageDiv.appendChild(contentParagraph);

        if (sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.classList.add('source-info');
            sourcesDiv.innerHTML = '<strong>Sources:</strong><br>';
            sources.forEach((source, index) => {
                sourcesDiv.innerHTML += `${index + 1}. From: <code>${source.source}</code><br>Content: <code>${source.content_preview}</code><br>`;
            });
            messageDiv.appendChild(sourcesDiv);
        }

        chatHistoryDiv.appendChild(messageDiv);
        chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight; // Scroll to bottom
    }

    // Function to fetch and display chat history
    async function loadChatHistory() {
        try {
            const response = await fetch('/history');
            const data = await response.json();
            if (data.success && data.history) {
                chatHistoryDiv.innerHTML = ''; // Clear existing history
                if (data.history.length === 0) {
                    addMessage('assistant', 'Hi there! Upload a PDF to start chatting.');
                } else {
                    data.history.forEach(msg => {
                        addMessage(msg.role, msg.content);
                    });
                }
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }


    // Handle PDF upload
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const file = pdfFile.files[0];
        if (!file) {
            uploadStatus.textContent = 'Please select a PDF file.';
            uploadStatus.className = 'status-message error';
            return;
        }

        uploadStatus.textContent = 'Uploading and processing PDF... This may take a moment.';
        uploadStatus.className = 'status-message';
        uploadBtn.disabled = true;
        chatInput.disabled = true;
        sendBtn.disabled = true;

        const formData = new FormData();
        formData.append('pdf_file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.success) {
                uploadStatus.textContent = data.message;
                uploadStatus.className = 'status-message success';
                chatInput.disabled = false;
                sendBtn.disabled = false;
                addMessage('assistant', 'PDF processed successfully! You can now ask questions.');
                loadChatHistory(); // Load initial chat history (should be empty after new upload)
            } else {
                uploadStatus.textContent = `Error: ${data.message}`;
                uploadStatus.className = 'status-message error';
                chatInput.disabled = true;
                sendBtn.disabled = true;
            }
        } catch (error) {
            console.error('Error during upload:', error);
            uploadStatus.textContent = `An unexpected error occurred: ${error.message}`;
            uploadStatus.className = 'status-message error';
            chatInput.disabled = true;
            sendBtn.disabled = true;
        } finally {
            uploadBtn.disabled = false;
        }
    });

    // Handle chat message submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const userMessage = chatInput.value.trim();
        if (!userMessage) {
            return;
        }

        addMessage('user', userMessage);
        chatInput.value = ''; 
        sendBtn.disabled = true;
        chatInput.disabled = true;

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: userMessage })
            });
            const data = await response.json();

            if (data.success) {
                const botResponse = data.response.answer;
                const sources = data.response.sources || [];
                addMessage('assistant', botResponse, sources);
            } else {
                addMessage('assistant', `Error: ${data.message}`);
            }
        } catch (error) {
            console.error('Error during chat:', error);
            addMessage('assistant', `An unexpected error occurred: ${error.message}`);
        } finally {
            sendBtn.disabled = false;
            chatInput.disabled = false;
            chatInput.focus();
        }
    });

    loadChatHistory();
});