import os
from google import genai
from google.genai import types
from dotenv import load_dotenv


load_dotenv()

client = genai.Client()

def main():
    model_id = "gemini-2.5-flash"
    
    # SYSTEM INSTRUCTIONS
    SRE_INSTRUCTION = """
    You are a strict GKE Site Reliability Engineer.
    Analyze the provided error log.
    You must respond in strict JSON format with exactly three keys:
    - "ROOT CAUSE" : A brief , technical explanation.
    - "SEVERITY" : Choose only 'Low', 'Medium', 'High' or 'Critical'
    - "RECOMMENDATION" : A specific kubectl command or actionable step.
    """

    # A simulated messy Kubernetes error log
    log_data = 'E0427 10:23:45.123456 12345 main.go:123] Pod "backend-api-5c99" Failed to pull image "gcr.io/my-project/api:v1.2": rpc error: code = NotFound desc = failed to pull and unpack image'

    print("---- STEP 1: Pre-flight Quota Check ---")
    try:
        token_info = client.models.count_tokens(
            model=model_id,
            contents=log_data
        )
        print(f"Estimated tokens to be consumed (Payload only): {token_info.total_tokens}\n")
    except Exception as e:
        print(f"Token count failed: {e}")
        return

    print("--- Step 2: Executing SRE Agent ---")
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=log_data,
            config=types.GenerateContentConfig(
                system_instruction=SRE_INSTRUCTION,
                temperature=0.1, # Low temperature = Deterministic, robotic responses
                response_mime_type="application/json" # Forces the API to validate JSON output
            )
        )
        print("AGENT ANALYSIS (Structured Data):")
        print(response.text)
        print("\n" + "*"*40)
        

        # FinOps / Billing 
        usage = response.usage_metadata
        print("--- POST FLIGHT BILLING ---")
        print(f"Input Tokens (Prompt):     {usage.prompt_token_count}")
        print(f"Output Tokens (Generated): {usage.candidates_token_count}")
        print(f"Total Tokens Billed:       {usage.total_token_count}")
        print("="*40)


    except Exception as e:
        print(f"Agent execution failed: {e}")




if __name__ == "__main__":
    main()