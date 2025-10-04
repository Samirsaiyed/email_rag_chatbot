"""
Test Llama with conversational API.
"""
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

def test_llama_chat():
    """Test Llama with chat API."""
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    
    if not token:
        print("ERROR: Token not found")
        return
    
    print(f"Token: {token[:10]}...")
    
    try:
        print("\nTesting Llama 3.2 with chat API...")
        client = InferenceClient(token=token)
        
        messages = [
            {"role": "user", "content": "What is 2+2? Answer briefly."}
        ]
        
        response = client.chat_completion(
            messages=messages,
            model="meta-llama/Llama-3.2-3B-Instruct",
            max_tokens=50,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content
        print(f"SUCCESS! Response: {answer}")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_llama_chat()