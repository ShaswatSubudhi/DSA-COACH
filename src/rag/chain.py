import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from retriever import search
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.3,google_api_key=GOOGLE_API_KEY)

def ask_coach(question):
    results = search(question, top_k=5)
    context = ""
    for match in results["matches"]:
        context += f"""
                    Source: {match['metadata']['source']}
                    Page: {match['metadata']['page']}
                    {match['metadata']['text']}
                    -------------------------
                """
    prompt = f"""
                You are a Dynamic Programming Coach.
                Your job is to teach Dynamic Programming clearly to a student.
                Use the provided context to answer the student's question.
                Rules:
                1. Prefer information from the provided context.
                2. Explain concepts in simple language.
                3. Do not blindly copy the context.
                4. If the context does not contain enough information, clearly say so.
                5. When useful, give a small example.
                6. For coding questions, explain the logic before giving code.
                CONTEXT:
                {context}
                STUDENT QUESTION:
                {question}
            """
    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    question = input("Ask your DP Coach: ")
    answer = ask_coach(question)
    print("\nDP COACH:\n")
    print(answer)