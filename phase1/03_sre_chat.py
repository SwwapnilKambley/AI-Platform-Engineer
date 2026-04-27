import os
import sys
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv


load_dotenv()
client = genai.Client()


def main():
    model = "gemini-2.5-flash"

    SRE_INSTRUCTION = """
    You are an elite GKE Site Reliability Engineer. 
    You are assisting a junior engineer in an interactive terminal session.
    Keep your answers highly technical, concise, and actionable. 
    """

    print("--- Initializing Stateful SRE Agent (Streaming Mode) ---")

    chat = client.chats.create(
        model= model,
        config=types.GenerateContentConfig(
            system_instruction=SRE_INSTRUCTION,
            temperature=0.2
        )
    )

    # 3. File Ingestion
    log_file = Path("utils/gke-crash.log")
    if not log_file.exists():
        print(f"❌ Error: Could not find {log_file} in the current directory.")
        return

    print(f"📂 Ingesting {log_file.name} into Agent memory...")
    with open(log_file, "r") as file:
        log_content = file.read()

    # --- THE FINOPS PRE-FLIGHT CHECK ---
    print("Running token capacity check...")

    token_info = client.models.count_tokens(
        model=model, 
        contents=log_content
        )
    
    if token_info.total_tokens > 30000: # Hard limit threshold
        print(f"❌ BLOCKED: Log is {token_info.total_tokens} tokens. Truncate before ingestion.")
        return
        
    print(f"✅ Payload safe: {token_info.total_tokens} tokens.")


    # We silently send the file to the agent to establish the context
    initial_prompt = f"Analyze this newly ingested log file and give me a 1-sentence summary of the failure:\n\n{log_content}"
    
    try:
        print(f"\n[SRE Agent Initial Analysis]: ", end="", flush=True)
        # We use stream so it prints token-by-token like `kubectl logs -f`
        response = chat.send_message_stream(initial_prompt)
        for chunk in response:
            print(chunk.text, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"Failed to analyze log: {e}")
        return

    # 4. The Interactive Event Loop
    print("Agent Online. You can now ask follow-up questions about the log. Type 'exit' to end.\n")
    
    while True:
        try:
            user_input = input("DevOps@GKE-Cluster:~$ ")
            
            if user_input.lower() in ['exit', 'quit']:
                print("Closing session...")
                break
                
            if not user_input.strip():
                continue

            print("\n[SRE Agent]: ", end="", flush=True)
            
            # The agent remembers the file because of the `chat` object
            response = chat.send_message_stream(user_input)
            for chunk in response:
                print(chunk.text, end="", flush=True)
            print("\n")
            
        except KeyboardInterrupt:
            print("\nForce quitting...")
            sys.exit(0)
        except Exception as e:
            print(f"\n[Error]: {e}\n")

if __name__ == "__main__":
    main()
