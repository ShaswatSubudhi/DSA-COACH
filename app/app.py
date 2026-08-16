import sys
import streamlit as st

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.coach.coach import (ask_coach,generate_practice_problem,evaluate_practice_answer)
from src.coach.learning_path import (get_topics,get_next_topic,mark_completed,load_progress,load_progress_data,mark_video_completed)
from src.youtube.youtube_search import search_youtube
from src.vision.image_question import extract_question
from src.voice.speech_to_text import speech_to_text


def display_coach_response(response):
    st.markdown("### 🤖 DP Coach")
    st.markdown(response["answer"])
    sources = response.get("sources",[])
    if sources:
        with st.expander("📚 Sources used"):
            for source in sources:
                st.write(f"📄 **{source['source']}** "f"— Page {source['page']} "f"— Score: {source['score']:.3f}")


st.set_page_config(page_title="DP Coach",page_icon="🧠",layout="wide")

if "completed_topics" not in st.session_state:
    st.session_state.completed_topics = load_progress()
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = "dp_basics"
if "selected_video" not in st.session_state:
    st.session_state.selected_video = None
if "videos" not in st.session_state:
    st.session_state.videos = []
if "selected_video_index" not in st.session_state:
    st.session_state.selected_video_index = 0
if "completed_videos" not in st.session_state:
    progress_data = load_progress_data()
    st.session_state.completed_videos = (progress_data.get("completed_videos",[]))
if "camera_open" not in st.session_state:
    st.session_state.camera_open = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "practice_problem" not in st.session_state:
    st.session_state.practice_problem = None
if "practice_sources" not in st.session_state:
    st.session_state.practice_sources = []

if "practice_answer" not in st.session_state:
    st.session_state.practice_answer = None

st.title("🧠 DP Coach")
st.caption("Your personal Dynamic Programming learning assistant")
topics = get_topics()
current_topic = next((topic for topic in topics if topic["id"] == st.session_state.selected_topic),topics[0])
st.header(f"📚 {current_topic['name']}")
completed_count = len(st.session_state.completed_topics)
total_topics = len(topics)
progress = (completed_count / total_topics if total_topics > 0 else 0)
st.progress(progress,text=f"Learning Progress: {completed_count}/{total_topics} topics")
video_column, roadmap_column = st.columns([3, 1])

with video_column:
    st.subheader("🎥 Learning Video")
    if st.session_state.selected_video:
        video = st.session_state.selected_video
        current_index = st.session_state.selected_video_index
        total_videos = len(st.session_state.videos)
        st.caption(f"Video {current_index + 1} of {total_videos}")
        if video["embed_url"]:
            st.iframe(video["embed_url"],height=500)
        else:
            st.info("Demo video selected. Real YouTube playback " "will appear when the YouTube API is connected.")
        st.markdown(f"### {video['title']}")
        st.caption(
            f"{video['channel']} • "
            f"{video['duration']} • "
            f"{video['views']}"
        )
        video_id = video["video_id"]
        if video_id in st.session_state.completed_videos:
            st.success("☑ Video completed")
        else:
            if st.button("☑ Mark Video as Completed", key=f"player_complete_{video_id}",use_container_width=True):
                st.session_state.completed_videos = (mark_video_completed(video_id))
                st.rerun()
        previous_col, next_col = st.columns(2)
        with previous_col:
            if current_index > 0:
                if st.button("⬅️ Previous Video",key="previous_video",use_container_width=True):
                    previous_video = (st.session_state.videos[current_index - 1])
                    st.session_state.selected_video = (previous_video)
                    st.session_state.selected_video_index = (current_index - 1)
                    st.rerun()
        with next_col:
            if current_index + 1 < total_videos:
                if st.button("Next Video ➡️",key="next_video",use_container_width=True):
                    next_video = (st.session_state.videos[current_index + 1])
                    st.session_state.selected_video = (next_video)
                    st.session_state.selected_video_index = (current_index + 1)
                    st.rerun()
            else:
                st.success("🎉 You've reached the last video!")
    else:
        st.info("Select a video from the list below.")

with roadmap_column:
    st.subheader("📚 Learning Path")
    for topic in topics:
        completed = (topic["id"] in st.session_state.completed_topics)
        if completed:
            label = f"☑ {topic['name']}"
        elif topic["id"] == current_topic["id"]:
            label = f"▶ {topic['name']}"
        else:
            label = f"☐ {topic['name']}"
        if st.button(label,key=f"topic_{topic['id']}",use_container_width=True):
            st.session_state.selected_topic = topic["id"]
            st.session_state.selected_video = None
            st.session_state.selected_video_index = 0
            with st.spinner(f"Finding videos for {topic['name']}..."):
                st.session_state.videos = search_youtube(topic["name"],max_results=10)
            st.rerun()
st.divider()

complete_column, next_column = st.columns(2)
with complete_column:
    if current_topic["id"] not in st.session_state.completed_topics:
        if st.button("☑ Mark Topic as Completed",use_container_width=True):
            st.session_state.completed_topics = mark_completed(st.session_state.completed_topics,current_topic["id"])
            next_topic = get_next_topic(st.session_state.completed_topics)
            if next_topic:
                st.session_state.selected_topic = (next_topic["id"])
                st.session_state.selected_video = None
                st.session_state.selected_video_index = 0
                with st.spinner(f"Finding videos for {next_topic['name']}..."):
                    st.session_state.videos = search_youtube(next_topic["name"],max_results=10)
            st.rerun()
    else:
        st.success("✅ Topic completed!")
with next_column:
    next_topic = get_next_topic(st.session_state.completed_topics)
    if next_topic:
        st.info(f"➡️ Next to learn: **{next_topic['name']}**")
    else:
        st.success("🎉 Congratulations! You completed the entire DP roadmap!")
st.divider()

st.subheader(f"🎥 Videos about {current_topic['name']}")
search_col, button_col = st.columns([5, 1])
with search_col:
    youtube_query = st.text_input("Search YouTube",value=current_topic["name"],label_visibility="collapsed",placeholder="Search for a DP topic...")
with button_col:
    search_clicked = st.button("🔎 Search",use_container_width=True)
if search_clicked:
    with st.spinner("Searching videos..."):
        st.session_state.videos = search_youtube(youtube_query,max_results=10)
if st.session_state.videos:
    for video in st.session_state.videos:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(video["thumbnail"],use_container_width=True)
        with col2:
            st.markdown(f"### {video['title']}")
            st.write(f"**{video['channel']}**")
            st.caption(f"{video['duration']} • {video['views']}")
            if st.button("▶ Watch",key=f"watch_{video['video_id']}"):
                st.session_state.selected_video = video
                st.session_state.selected_video_index = (st.session_state.videos.index(video))
                st.rerun()
            video_completed = (video["video_id"] in st.session_state.completed_videos)
        if st.checkbox("☑ Completed", value=video_completed, key=f"completed_{video['video_id']}"):
            if video["video_id"] not in st.session_state.completed_videos:
                st.session_state.completed_videos = (mark_video_completed(video["video_id"]))
st.divider()

st.header("🤖 DP Coach")

if st.session_state.chat_history:
    for message in st.session_state.chat_history:
        if message["role"] == "student":
            with st.chat_message("user"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["content"])
                sources = message.get("sources",[])
                if sources:
                    with st.expander("📚 Sources used"):
                        for source in sources:
                            st.write(f"📄 **{source['source']}** "f"— Page {source['page']} "f"— Score: "f"{source['score']:.3f}")

if st.button("🗑️ Clear Conversation",key="clear_chat"):
    st.session_state.chat_history = []
    st.rerun()

input_tab, photo_tab, voice_tab = st.tabs(["⌨️ Ask Question","📷 Ask From Photo","🎙️ Voice"])

with input_tab:
    mode = st.selectbox(
        "Choose mode",
        [
            "Learn",
            "Hint",
            "Solution",
            "Practice"
        ]
    )
    if mode != "Practice":
        question = st.text_area("Ask your DP Coach",placeholder=("Example: Explain memoization ""or How do I solve 0/1 Knapsack?"),height=100)
        if st.button("💬 Ask Coach",key="text_coach",use_container_width=True):
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                mode_map = {"Learn": "learn","Hint": "hint","Solution": "solution"}
                with st.spinner("DP Coach is thinking..."):
                    answer = ask_coach(question,mode_map[mode],current_topic["name"],st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "student","content": question})
                st.session_state.chat_history.append({"role": "coach","content": answer["answer"],"sources": answer["sources"]})
                st.rerun()
    else:
        st.subheader("📝 DP Practice")
        difficulty = st.selectbox("Choose Difficulty",
                                    [
                                        "Easy",
                                        "Medium",
                                        "Hard"
                                    ],index=1,key="practice_difficulty")
        answer_type = st.radio("What do you want to submit?",["Explanation","Code"],horizontal=True,key="practice_answer_type")
        if st.button("🎲 Generate Practice Problem",use_container_width=True):
            with st.spinner("Creating a practice problem..."):
                practice = generate_practice_problem(current_topic["name"],difficulty)
            st.session_state.practice_problem = (practice["problem"])
            st.session_state.practice_sources = (practice["sources"])
            st.session_state.practice_answer = None
            st.rerun()
        if st.session_state.practice_problem:
            problem = st.session_state.practice_problem
            st.divider()
            st.markdown(f"### 📝 {problem['title']}")
            st.markdown(problem["problem"])
            st.markdown("#### 📥 Input Format")
            st.code(problem["input_format"])
            st.markdown("#### 📤 Output Format")
            st.code(problem["output_format"])
            st.markdown("#### 📌 Constraints")
            st.code(problem["constraints"])
            st.markdown("#### 💡 Example")
            example = problem["example"]
            st.markdown("**Input:**")
            st.code(example["input"])
            st.markdown("**Output:**")
            st.code(example["output"])
            st.markdown("**Explanation:**")
            st.write(example["explanation"])
            st.divider()
            if answer_type == "Code":
                student_answer = st.text_area("💻 Your Code",placeholder=("Write your solution code here..."),height=300,key="practice_student_answer")
            else:
                student_answer = st.text_area("✍️ Your Explanation",placeholder=("Explain your approach, ""DP state, recurrence, and complexity..."),height=250,key="practice_student_answer")
            if st.button("🚀 Submit Answer",key="submit_practice",use_container_width=True):
                if not student_answer.strip():
                    st.warning("Please write your answer first.")
                else:
                    with st.spinner("Evaluating your answer..."):
                        problem = st.session_state.practice_problem
                        evaluation = evaluate_practice_answer(current_topic["name"],problem,student_answer,answer_type)
                    st.session_state.practice_answer = (evaluation)
                    st.rerun()
        if st.session_state.practice_answer:
            st.divider()
            st.markdown("### 🤖 Coach Feedback")
            st.markdown(st.session_state.practice_answer["answer"])
            sources = (st.session_state.practice_answer.get("sources",[]))
            if sources:
                with st.expander("📚 Sources used"):
                    for source in sources:
                        st.write(
                            f"📄 **{source['source']}** "
                            f"— Page {source['page']} "
                            f"— Score: "
                            f"{source['score']:.3f}"
                        )

with photo_tab:
    st.write("Upload a question or take a photo of one.")
    camera_col, upload_col = st.columns(2)
    with camera_col:
        if not st.session_state.camera_open:
            if st.button("📷 Open Camera",use_container_width=True):
                st.session_state.camera_open = True
                st.rerun()
        else:
            if st.button("✖ Close Camera",use_container_width=True):
                st.session_state.camera_open = False
                st.rerun()
    with upload_col:
        uploaded_image = st.file_uploader("📁 Upload Image",type=["jpg", "jpeg", "png"])
    image = None
    if st.session_state.camera_open:
        image = st.camera_input("📷 Take a picture")
    selected_image = image or uploaded_image
    if selected_image:
        st.image(selected_image,caption="Question image",use_container_width=True)
        if st.button("🔍 Understand & Ask Coach",key="photo_coach",use_container_width=True):
            with st.spinner("Reading the question..."):
                image_bytes = (selected_image.getvalue())
                mime_type = (selected_image.type)
                extracted_question = (extract_question(image_bytes,mime_type))
            st.markdown("### 📝 Question detected")
            st.write(extracted_question)
            with st.spinner("Finding relevant DP material..."):
                answer = ask_coach(extracted_question,"learn",current_topic["name"],st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "student","content": extracted_question})
                st.session_state.chat_history.append({"role": "coach","content": answer["answer"],"sources": answer["sources"]})
                st.rerun()

with voice_tab:
    st.write("Record your question and let the DP Coach understand it.")
    audio = st.audio_input("🎙️ Record your question")
    if audio:
        if st.button("🔊 Convert & Ask Coach",key="voice_coach",use_container_width=True):
            with st.spinner("Understanding your question..."):
                audio_bytes = audio.getvalue()
                mime_type = audio.type
                question = speech_to_text(audio_bytes,mime_type)
            st.markdown("### 📝 Question detected")
            st.write(question)
            with st.spinner("DP Coach is thinking..."):
                answer = ask_coach(question,"learn",current_topic["name"],st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "student","content": question})
                st.session_state.chat_history.append({"role": "coach","content": answer["answer"],"sources": answer["sources"]})
                st.rerun()