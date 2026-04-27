import os
from google import genai
from dotenv import load_dotenv



load_dotenv()

client = genai.Client()

def main():
    print("Initializing connection to Google AI ...\n")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Hello Gemini, are you ready to help me with my AI-Platform_Enginnering Journey ?"
        )
        print("Connection Sucessful ! RECEIVED RESPONSE : ")
        print("_" * 50)
        print(response.text)
        print("_" * 50)

    except Exception as e:
        print("Connection Failed. Check your API key or Network.")
        print(f"Error detaisl: {e}")

if __name__ == "__main__":
    main()
