import os
import base64

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.2,google_api_key=os.getenv("GOOGLE_API_KEY"))

def extract_question(image_bytes, mime_type="image/jpeg"):
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": """
                            Look at this image carefully.
                            Identify the DSA or Dynamic Programming question.
                            Extract:
                            1. Complete problem statement
                            2. Input information
                            3. Output information
                            4. Constraints
                            5. Any code visible in the image
                            Do NOT solve the problem.
                            Return the extracted question clearly.
                        """
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}
            }
        ]
    )
    response = llm.invoke([message])
    return response.content