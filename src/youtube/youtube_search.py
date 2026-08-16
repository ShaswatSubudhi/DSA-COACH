import os
from dotenv import load_dotenv
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

MOCK_VIDEOS = [
    {
        "video_id": "dQw4w9WgXcQ",
        "title": "Dynamic Programming Explained",
        "description": "Introduction to Dynamic Programming concepts.",
        "channel": "DP Learning",
        "published_at": "2026-01-01",
        "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "duration": "15:32",
        "views": "1.2M views"
    },
    {
        "video_id": "dQw4w9WgXcQ",
        "title": "0/1 Knapsack Dynamic Programming",
        "description": "Learn the 0/1 Knapsack DP pattern.",
        "channel": "Algorithm Academy",
        "published_at": "2026-02-10",
        "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "duration": "21:14",
        "views": "850K views"
    },
    {
        "video_id": "dQw4w9WgXcQ",
        "title": "DP Patterns You Must Know",
        "description": "Important Dynamic Programming patterns for coding interviews.",
        "channel": "Coding Mentor",
        "published_at": "2026-03-15",
        "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "duration": "18:45",
        "views": "620K views"
    }
]

def search_youtube(topic, max_results=10):
    if not YOUTUBE_API_KEY:
        print("YouTube API key not found.")
        print("Using mock videos for development.")
        return MOCK_VIDEOS[:max_results]
    from googleapiclient.discovery import build
    youtube = build("youtube","v3",developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(part="snippet",q=topic,type="video",maxResults=max_results,order="relevance",videoEmbeddable="true",videoDefinition="high",relevanceLanguage="en",regionCode="IN")
    response = request.execute()
    videos = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        videos.append({
            "video_id": video_id,
            "title": snippet["title"],
            "description": snippet["description"],
            "channel": snippet["channelTitle"],
            "published_at": snippet["publishedAt"],
            "thumbnail": snippet["thumbnails"]["high"]["url"],
            "youtube_url": (f"https://www.youtube.com/watch?v={video_id}"),
            "embed_url": (f"https://www.youtube.com/embed/{video_id}"),
            "duration": "Unknown",
            "views": "Unknown"
        })
    return videos

def get_video_details(video_ids):
    if not YOUTUBE_API_KEY:
        return {}
    from googleapiclient.discovery import build
    youtube = build("youtube","v3",developerKey=YOUTUBE_API_KEY)
    request = youtube.videos().list(part="contentDetails,statistics",id=",".join(video_ids))
    response = request.execute()
    details = {}
    for item in response.get("items", []):
        video_id = item["id"]
        duration = item["contentDetails"]["duration"]
        views = item["statistics"].get("viewCount","0")
        details[video_id] = {"duration": duration,"views": views}
    return details

if __name__ == "__main__":
    topic = input("Enter DP topic: ")
    videos = search_youtube(topic)
    print("\nVideos:\n")
    for i, video in enumerate(videos, 1):
        print("--------------------------------")
        print(f"{i}. {video['title']}")
        print(f"Channel: {video['channel']}")
        print(f"Duration: {video['duration']}")
        print(f"Views: {video['views']}")
        print(f"URL: {video['youtube_url']}")