import google.generativeai as genai
import os
import json

# Load environment variables
from dotenv import load_dotenv

load_dotenv()


class GeminiAPI:
    def __init__(self) -> None:
        # prepare the large language model
        GEMINI_API_KEY = os.environ.get("GOOGLE_CLOUD_API_KEY")

        # Initialize the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)

        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]
        self.prompt = """
You will be analyzing a snippet of speech to determine if it contains any microaggressions or derogatory/discriminatory behavior toward women or minorities. Microaggressions are subtle, often unintentional statements or actions that express a prejudiced attitude toward a member of a marginalized group. Derogatory or discriminatory behavior includes language or actions that insult, criticize, or express negative prejudicial attitudes based on gender, race, ethnicity, sexual orientation, or other minority status.

Carefully examine the speech for any language or behavior that could be considered a microaggression or that is derogatory or discriminatory toward women or minorities. Look for subtle insults, negative stereotyping, prejudiced assumptions, and language that demeans, excludes or nullifies the thoughts, feelings or experiences of these groups.

Write your reasoning and justification for your classification inside <reasoning> tags. Cite specific examples from the speech.

Finally, output your classification of whether the speech contains microaggressions or derogatory/discriminatory behavior in the following JSON format:

{
    isBad": true/false
}

Replace true/false with either true if the speech does contain microaggressions or derogatory/discriminatory behavior, or false if it does not.
"""
        self.model = genai.GenerativeModel(
            # "gemini-1.5-pro-latest",
            "gemini-1.5-flash",
            safety_settings=self.safety_settings,
            generation_config=genai.GenerationConfig(
                max_output_tokens=8000,
                temperature=0, # 1.0 is max for gemini 1.0, 2.0 is max for gemini 1.5
                stop_sequences=["}"]
            ),
            system_instruction=""
        )
    
    # basic function to generate questions from a prompt and return text
    def generate(self, prompt: str):
        chat_session = self.model.start_chat()
        response = chat_session.send_message(f"Here is the speech snippet to analyze:\n\n{prompt}")
        # add in a } to the end of the response to ensure the JSON is valid
        response += "}"

        return response
