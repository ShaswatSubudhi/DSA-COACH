import os
import json

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from src.rag.retriever import search
from src.coach.prompts import (COACH_SYSTEM_PROMPT,LEARN_PROMPT,HINT_PROMPT,SOLUTION_PROMPT,PRACTICE_PROMPT,PRACTICE_GENERATE_PROMPT,PRACTICE_EVALUATE_PROMPT)
load_dotenv()


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.3,google_api_key=os.getenv("GOOGLE_API_KEY"))


def get_context(question, top_k=5):
    results = search(question, top_k)
    context = ""
    sources = []
    for match in results["matches"]:
        metadata = match["metadata"]
        source = metadata.get("source","Unknown")
        page = metadata.get("page","Unknown")
        text = metadata.get("text","")
        context += f"""Source: {source}
                       Page: {page} {text}
                       -------------------------
                    """
        sources.append({"source": source,"page": page,"score": match.get("score", 0)})
    return context, sources


def ask_coach(question, mode="learn", topic=None,chat_history=None):
    if topic:
        question_with_topic = f"""Current DP topic: {topic} Student question: {question}"""
    else:
        question_with_topic = question

    context, sources = get_context(question_with_topic)

    if chat_history:
        history_text = "\n".join(f"{message['role']}: {message['content']}" for message in chat_history)
        contextual_question = f""" Previous conversation: {history_text} Current DP topic: {topic} Student's new question: {question} """
    elif topic:
        contextual_question = f"""Current DP topic: {topic} Student question:{question}"""
    else:
        contextual_question = question

    if mode == "learn":
        prompt = LEARN_PROMPT.format(question=contextual_question,context=context)
    elif mode == "hint":
        prompt = HINT_PROMPT.format(question=contextual_question,context=context)
    elif mode == "solution":
        prompt = SOLUTION_PROMPT.format(question=contextual_question,context=context)
    elif mode == "practice":
        prompt = PRACTICE_PROMPT.format(question=contextual_question,context=context)
    else:
        raise ValueError("Invalid mode. Use learn, hint, solution, or practice.")
    
    final_prompt = f"""{COACH_SYSTEM_PROMPT}{prompt}"""
    response = llm.invoke(final_prompt)
    return {"answer": response.content,"sources": sources}

def generate_practice_problem(topic,difficulty="Medium"):
    retrieval_query = f"""
                        Dynamic Programming
                        Topic: {topic}
                        Difficulty: {difficulty}
                        Focus on {topic} concepts, algorithms, examples and practice problems.
                    """
    context, sources = get_context(retrieval_query,top_k=5)
    prompt = PRACTICE_GENERATE_PROMPT.format(topic=topic,context=context,difficulty=difficulty)
    response = llm.invoke(prompt)
    try:
        problem_data = json.loads(response.content)
    except json.JSONDecodeError:
        cleaned = response.content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        problem_data = json.loads(cleaned.strip())
    return {"problem": problem_data,"sources": sources}

def evaluate_practice_answer(topic,problem,student_answer,answer_type="Explanation"):
    context, sources = get_context(f"{topic} {problem['title']} {problem['problem']}",top_k=5)
    prompt = PRACTICE_EVALUATE_PROMPT.format(
                                                    topic=topic,
                                                    problem=problem["problem"],
                                                    input_format=problem["input_format"],
                                                    output_format=problem["output_format"],
                                                    constraints=problem["constraints"],
                                                    example_input=problem["example"]["input"],
                                                    example_output=problem["example"]["output"],
                                                    student_answer=student_answer,
                                                    answer_type=answer_type,
                                                    context=context
                                                )
    final_prompt = f"""{COACH_SYSTEM_PROMPT} {prompt}"""
    response = llm.invoke(final_prompt)
    return {"answer": response.content, "sources": sources}

if __name__ == "__main__":
    print("===== DP COACH =====")
    question = input("\nAsk your question: ")
    print("\nChoose mode:")
    print("1. Learn")
    print("2. Hint")
    print("3. Solution")
    print("4. Practice")
    choice = input("\nEnter choice: ")
    modes = {
        "1": "learn",
        "2": "hint",
        "3": "solution",
        "4": "practice"
    }
    mode = modes.get(choice,"learn")
    answer = ask_coach(question,mode)
    print("\n===== DP COACH =====\n")
    print(answer["answer"])
    print("\nSources:")
    for source in answer["sources"]:
        print(f"- {source['source']} " f"(Page {source['page']})")