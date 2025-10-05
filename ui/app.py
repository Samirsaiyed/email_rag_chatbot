"""
Gradio UI for Email RAG Chatbot.
"""
import gradio as gr
import requests
from typing import List, Tuple
import json

API_URL = "http://localhost:8000/api/v1"

# Global session state
current_session = {"session_id": None, "thread_id": None}


def start_session(thread_id: str) -> str:
    """Start a new session."""
    try:
        response = requests.post(
            f"{API_URL}/start_session",
            json={"thread_id": thread_id}
        )
        response.raise_for_status()
        data = response.json()
        
        current_session["session_id"] = data["session_id"]
        current_session["thread_id"] = thread_id
        
        return f"✓ Session started for thread {thread_id}\nSession ID: {data['session_id']}"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"


def chat(message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
    """Process chat message."""
    
    if not current_session["session_id"]:
        return history + [(message, "⚠️ Please start a session first by selecting a thread.")], ""
    
    try:
        # Call API
        response = requests.post(
            f"{API_URL}/ask",
            json={
                "session_id": current_session["session_id"],
                "question": message,
                "top_k": 5
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Format answer with metadata
        answer = data["answer"]
        
        # Add debug info (optional)
        debug_info = f"\n\n---\n**Rewritten Query:** {data['rewritten_query']}\n"
        debug_info += f"**Retrieved:** {len(data['retrieved_chunks'])} chunks\n"
        debug_info += f"**Citations:** {len(data['citations'])} sources"
        
        full_answer = answer + debug_info
        
        # Update history
        history.append((message, full_answer))
        
        return history, ""
    
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        history.append((message, error_msg))
        return history, ""


def reset_session() -> Tuple[List, str]:
    """Reset the current session."""
    if current_session["session_id"]:
        try:
            requests.post(
                f"{API_URL}/reset_session",
                params={"session_id": current_session["session_id"]}
            )
            return [], "✓ Session memory cleared"
        except:
            pass
    
    return [], "ℹ️ No active session"


# Build UI
with gr.Blocks(title="Email RAG Chatbot", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown("# 📧 Email RAG Chatbot")
    gr.Markdown("Search and chat about email threads with AI-powered retrieval")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🎯 Session Control")
            
            thread_selector = gr.Dropdown(
                choices=[
                    "T-58ae003b (PIRA Global Oil - with attachments)",
                    "T-3df8a268 (Axia Energy)",
                    "T-8b62a250 (El Paso Electric)",
                    "T-b7936ec5 (Enron Metals)",
                    "T-a5f23567 (PG&E)",
                    "T-46082fd4",
                    "T-fbceeaf4",
                    "T-c797fbf2",
                    "T-95f11b58",
                    "T-9af80adb",
                    "T-a7b53a59",
                    "T-f22ca434"
                ],
                label="Select Email Thread",
                value="T-58ae003b (PIRA Global Oil - with attachments)"
            )
            
            start_btn = gr.Button("🚀 Start Session", variant="primary")
            session_status = gr.Textbox(
                label="Session Status",
                interactive=False,
                lines=3
            )
            
            reset_btn = gr.Button("🔄 Reset Memory")
            
            gr.Markdown("### 💡 Sample Questions")
            gr.Markdown("""
            - What is the budget amount?
            - Who needs to finalize the contract?
            - What are the technical specifications?
            - Compare the draft with final version
            - When is the delivery date?
            """)
        
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Chat")
            
            chatbot = gr.Chatbot(
                height=500,
                show_label=False,
                avatar_images=("👤", "🤖")
            )
            
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Ask a question about the email thread...",
                    show_label=False,
                    scale=4
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)
    
    # Event handlers
    def extract_thread_id(selection: str) -> str:
        """Extract thread ID from dropdown selection."""
        return selection.split(" ")[0]
    
    start_btn.click(
        fn=lambda x: start_session(extract_thread_id(x)),
        inputs=[thread_selector],
        outputs=[session_status]
    )
    
    send_btn.click(
        fn=chat,
        inputs=[msg_input, chatbot],
        outputs=[chatbot, msg_input]
    )
    
    msg_input.submit(
        fn=chat,
        inputs=[msg_input, chatbot],
        outputs=[chatbot, msg_input]
    )
    
    reset_btn.click(
        fn=reset_session,
        outputs=[chatbot, session_status]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )