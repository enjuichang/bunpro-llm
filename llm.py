from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

###
# Add whatever llm client here