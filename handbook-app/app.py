import gradio as gr
import os
from dotenv import load_dotenv
from pdf_processor import PDFProcessor
from handbook_generator import HandbookGenerator
import json

# Load environment variables
load_dotenv()

# Initialize components
pdf_processor = PDFProcessor()
handbook_generator = HandbookGenerator()

# Global state to store processed documents
processed_docs = []


def upload_pdf(files):
    """Process uploaded PDF files"""
    global processed_docs

    if not files:
        return "No files uploaded.", ""

    results = []
    for file in files:
        try:
            # Extract text from PDF
            text = pdf_processor.extract_text_from_pdf(file.name)

            # Store in vector database
            pdf_processor.add_to_vectordb(text, file.name)

            processed_docs.append({
                'filename': os.path.basename(file.name),
                'text': text[:500] + "..." if len(text) > 500 else text
            })

            results.append(f"✓ Processed: {os.path.basename(file.name)} ({len(text)} characters)")
        except Exception as e:
            results.append(f"✗ Error with {os.path.basename(file.name)}: {str(e)}")

    summary = "\n".join(results)
    docs_list = "\n\n".join([f"**{doc['filename']}**\n{doc['text']}" for doc in processed_docs])

    return summary, docs_list


def chat_with_context(message, history):
    """Chat with context from uploaded PDFs"""
    if not message:
        return history

    try:
        # Check if user is requesting handbook generation
        if any(keyword in message.lower() for keyword in
               ['handbook', 'generate', 'create document', 'write book', 'comprehensive guide']):
            # Extract topic from message
            topic = extract_topic(message)

            # Get relevant context
            context = pdf_processor.get_relevant_context(topic, k=10)

            yield history + [{"role": "user", "content": message}, {"role": "assistant", "content": "🔄 Generating your handbook... This may take 2-3 minutes for 20,000+ words..."}]

            handbook = handbook_generator.generate_handbook(topic, context)

            # Save to file
            filename = save_handbook(handbook, topic)

            response = f"✅ **Handbook Generated!**\n\nI've created a comprehensive handbook on '{topic}' with {len(handbook.split())} words.\n\n**Preview:**\n{handbook[:1000]}...\n\n[Full handbook saved to: {filename}]"

            yield history + [{"role": "user", "content": message}, {"role": "assistant", "content": response}]
        else:
            # Regular chat - get relevant context and respond
            context = pdf_processor.get_relevant_context(message, k=3)

            if not context:
                response = "I don't have any relevant information from the uploaded PDFs. Please upload some documents first!"
            else:
                response = handbook_generator.generate_response(message, context)

            yield history + [{"role": "user", "content": message}, {"role": "assistant", "content": response}]

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        yield history + [{"role": "user", "content": message}, {"role": "assistant", "content": error_msg}]


def extract_topic(message):
    """Extract the main topic from user message"""
    lower_msg = message.lower()

    if "handbook on" in lower_msg:
        topic = message.split("handbook on", 1)[1].strip()
    elif "about" in lower_msg:
        topic = message.split("about", 1)[1].strip()
    elif "on" in lower_msg:
        topic = message.split("on", 1)[1].strip()
    else:
        topic = message

    topic = topic.replace("?", "").replace(".", "").strip()
    return topic[:100]


def save_handbook(handbook_text, topic):
    """Save handbook to a file"""
    os.makedirs("handbooks", exist_ok=True)

    safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_topic = safe_topic.replace(" ", "_")[:50]

    filename = f"handbooks/{safe_topic}_handbook.md"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(handbook_text)

    return filename


def clear_database():
    """Clear all processed documents and reset database"""
    global processed_docs
    processed_docs = []
    pdf_processor.clear_vectordb()
    return "Database cleared!", ""


# Create Gradio interface
# FIX: theme moved to launch() to avoid Gradio 6 deprecation warning
with gr.Blocks(title="AI Handbook Generator") as demo:
    gr.Markdown("""
    # 📚 AI Handbook Generator

    Upload PDFs, chat about them, and generate comprehensive 20,000+ word handbooks!

    ## How to use:
    1. **Upload PDFs** - Add research papers, documentation, or any text-based PDFs
    2. **Chat** - Ask questions about the uploaded content
    3. **Generate Handbook** - Request a comprehensive handbook on any topic from your documents

    ### Example prompts for handbook generation:
    - "Create a handbook on Retrieval-Augmented Generation"
    - "Generate a comprehensive guide about AI safety"
    - "Write a handbook on machine learning techniques"
    """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📁 Document Upload")
            file_upload = gr.File(
                label="Upload PDF Files",
                file_count="multiple",
                file_types=[".pdf"]
            )
            upload_btn = gr.Button("Process PDFs", variant="primary")
            clear_btn = gr.Button("Clear Database", variant="stop")

            upload_status = gr.Textbox(
                label="Upload Status",
                lines=5,
                interactive=False
            )

            docs_display = gr.Markdown(
                label="Processed Documents",
                value="No documents uploaded yet."
            )

        with gr.Column(scale=2):
            gr.Markdown("### 💬 Chat & Generate")
            chatbot = gr.Chatbot(
                height=500,
                label="Conversation",
            )
            msg = gr.Textbox(
                label="Your Message",
                placeholder="Ask a question or request 'Create a handbook on [topic]'...",
                lines=2
            )

            with gr.Row():
                send_btn = gr.Button("Send", variant="primary")
                clear_chat = gr.Button("Clear Chat")

    gr.Markdown("""
    ---
    ### 💡 Tips:
    - Upload multiple related PDFs for richer handbooks
    - The more context provided, the better the handbook quality
    - Handbook generation takes 2-3 minutes for 20,000+ words
    - All handbooks are saved in the `handbooks/` folder
    """)

    # Event handlers
    upload_btn.click(
        upload_pdf,
        inputs=[file_upload],
        outputs=[upload_status, docs_display]
    )

    msg.submit(
        chat_with_context,
        inputs=[msg, chatbot],
        outputs=[chatbot]
    ).then(
        lambda: "",
        outputs=[msg]
    )

    send_btn.click(
        chat_with_context,
        inputs=[msg, chatbot],
        outputs=[chatbot]
    ).then(
        lambda: "",
        outputs=[msg]
    )

    clear_chat.click(
        lambda: None,
        outputs=[chatbot]
    )

    clear_btn.click(
        clear_database,
        outputs=[upload_status, docs_display]
    )

if __name__ == "__main__":
    print("🚀 Starting AI Handbook Generator...")
    print("📝 Make sure you have your GEMINI_API_KEY in .env file")
    print("🌐 Opening browser...")
    # FIX: theme moved here from gr.Blocks() to fix Gradio 6 deprecation warning
    demo.launch(share=False, theme=gr.themes.Soft())
