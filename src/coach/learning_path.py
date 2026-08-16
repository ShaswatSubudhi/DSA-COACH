import json
from pathlib import Path

PROGRESS_FILE = Path("data/progress.json")

TOPICS = [
    {
        "id": "dp_basics",
        "name": "Dynamic Programming Basics",
        "description": "Understand what Dynamic Programming is."
    },
    {
        "id": "recursion",
        "name": "Recursion",
        "description": "Understand recursion and recursive problem solving."
    },
    {
        "id": "overlapping_subproblems",
        "name": "Overlapping Subproblems",
        "description": "Understand why repeated subproblems occur."
    },
    {
        "id": "memoization",
        "name": "Memoization",
        "description": "Learn the top-down DP approach."
    },
    {
        "id": "tabulation",
        "name": "Tabulation",
        "description": "Learn the bottom-up DP approach."
    },
    {
        "id": "0_1_knapsack",
        "name": "0/1 Knapsack",
        "description": "Learn the classic 0/1 Knapsack pattern."
    },
    {
        "id": "unbounded_knapsack",
        "name": "Unbounded Knapsack",
        "description": "Learn the unbounded selection pattern."
    },
    {
        "id": "coin_change",
        "name": "Coin Change",
        "description": "Solve counting and minimum coin problems."
    },
    {
        "id": "lcs",
        "name": "Longest Common Subsequence",
        "description": "Learn the LCS DP pattern."
    },
    {
        "id": "lis",
        "name": "Longest Increasing Subsequence",
        "description": "Learn the LIS pattern."
    },
    {
        "id": "matrix_chain",
        "name": "Matrix Chain Multiplication",
        "description": "Learn interval DP."
    }
]


def get_topics():
    return TOPICS

def get_topic(topic_id):
    for topic in TOPICS:
        if topic["id"] == topic_id:
            return topic
    return None

def load_progress_data():
    if not PROGRESS_FILE.exists():
        return {"completed_topics": [],"completed_videos": []}
    try:
        with open(PROGRESS_FILE,"r",encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {"completed_topics": [],"completed_videos": []}

def load_progress():
    if not PROGRESS_FILE.exists():
        return []
    try:
        with open(PROGRESS_FILE,"r",encoding="utf-8") as file:
            data = json.load(file)
            return data.get("completed_topics",[])
    except (json.JSONDecodeError, OSError):
        return []


def save_progress(completed_topics):
    PROGRESS_FILE.parent.mkdir(parents=True,exist_ok=True)
    with open(PROGRESS_FILE,"w",encoding="utf-8") as file:
        json.dump({"completed_topics": completed_topics},file,indent=4)

def get_completed_videos():
    progress = load_progress_data()
    return progress.get("completed_videos", [])


def mark_video_completed(video_id):
    data = load_progress_data()
    completed_videos = data.get("completed_videos",[])
    if video_id not in completed_videos:
        completed_videos.append(video_id)
        data["completed_videos"] = completed_videos
        PROGRESS_FILE.parent.mkdir(parents=True,exist_ok=True)
        with open(PROGRESS_FILE,"w",encoding="utf-8") as file:
            json.dump(data,file,indent=4)
    return completed_videos

def get_next_topic(completed_topics):
    for topic in TOPICS:
        if topic["id"] not in completed_topics:
            return topic
    return None


def mark_completed(completed_topics,topic_id):
    if topic_id not in completed_topics:
        completed_topics.append(topic_id)
        save_progress(completed_topics)
    return completed_topics


if __name__ == "__main__":
    completed = load_progress()
    print("Completed topics:")
    for topic_id in completed:
        topic = get_topic(topic_id)
        if topic:
            print("✓", topic["name"])
    next_topic = get_next_topic(completed)
    print("\nNext topic:")
    if next_topic:
        print("→",next_topic["name"])
    else:
        print("🎉 All topics completed!")