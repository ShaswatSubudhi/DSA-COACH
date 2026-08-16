import os
import base64

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.1,google_api_key=os.getenv("GOOGLE_API_KEY"))
def speech_to_text(audio_bytes,mime_type="audio/wav"):
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": """
                            Convert the following audio into text.
                            Return ONLY the spoken text.
                            Do not explain it.
                            Do not answer the question.
                            Do not add anything else.
                        """
            },
            {
                "type": "media",
                "mime_type": mime_type,
                "data": audio_base64
            }
        ]
    )

    response = llm.invoke([message])
    return response.content