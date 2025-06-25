import streamlit as st
import os
import random
import json
import time
from openai import OpenAI
import math
from datetime import datetime, timedelta
import pytz

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Load Quiz Data from JSON File ---
@st.cache_data
def load_quiz_data():
    with open("quiz_questions.json", "r") as f:
        return json.load(f)

quiz_data = load_quiz_data()

# --- Load Shortcut Tips from JSON File ---
@st.cache_data
def load_tips():
    with open("shortcut_tips.json", "r") as f:
        return json.load(f)

shortcut_notes = load_tips()

# --- Load Cross Multiplication Pool ---
@st.cache_data
def load_cross_pool():
    with open("cross_questions_pool.json", "r") as f:
        return json.load(f)

cross_pool = load_cross_pool()

# --- Daily 5:30 PM IST Refresh Logic ---
ist = pytz.timezone("Asia/Kolkata")
now_ist = datetime.now(ist)
today_str = now_ist.strftime("%Y-%m-%d")
cutoff_time = ist.localize(datetime.strptime(today_str + " 17:30:00", "%Y-%m-%d %H:%M:%S"))

if "last_refresh_date" not in st.session_state:
    st.session_state.last_refresh_date = ""

if (now_ist >= cutoff_time and st.session_state.last_refresh_date != today_str) or "daily_cm_questions" not in st.session_state:
    st.session_state.daily_cm_questions = random.sample(cross_pool, 10)
    st.session_state.last_refresh_date = today_str

cross_multiplication_questions = st.session_state.daily_cm_questions

# --- UI Setup ---
st.set_page_config(page_title="Govt Exam AI Tutor", layout="centered")
st.title("🇮🇳 Govt Exam AI Tutor")
st.markdown("Practice and learn for SSC, Banking, Railways and more!")

# Sidebar for section navigation
sections = ["Chat with Tutor", "Take a Quiz", "Shortcut Tips", "Cross Multiplication Practice"]
query_section = st.query_params.get("section", [sections[0]])

if query_section not in sections:
    query_section = sections[0]

if "section_selector" not in st.session_state:
    st.session_state.section_selector = query_section

section = st.sidebar.radio("Choose Section", sections, index=sections.index(st.session_state.section_selector), key="section_selector")

if st.query_params.get("section", [None])[0] != section:
    st.query_params["section"] = section

# --- Chat with AI Tutor ---
if section == "Chat with Tutor":
    st.subheader("Ask your doubts")
    user_question = st.text_input("Enter your question")

    if st.button("Get Answer") and user_question:
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert Indian exam tutor. Explain clearly in simple English with examples if needed."},
                        {"role": "user", "content": user_question}
                    ]
                )
                answer = response.choices[0].message.content
                st.success(answer)
            except Exception as e:
                st.error("⚠️ Error from OpenAI: " + str(e))

# --- Quiz Section ---
elif section == "Take a Quiz":
    st.subheader("Mini Quiz")
    subject = st.selectbox("Choose a subject", list(quiz_data.keys()))
    total_questions = quiz_data[subject]

    if f"{subject}_page" not in st.session_state:
        st.session_state[f"{subject}_page"] = 1

    page = st.session_state[f"{subject}_page"]
    total_pages = math.ceil(len(total_questions) / 5)

    start_index = (page - 1) * 5
    end_index = start_index + 5
    questions = total_questions[start_index:end_index]

    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "submitted_flags" not in st.session_state:
        st.session_state.submitted_flags = {}

    score = 0
    for i, q in enumerate(questions):
        q_index = start_index + i
        st.write(f"**Q{q_index+1}: {q['question']}**")
        selected = st.radio("Choose one:", q['options'], key=f"q{q_index}_radio")
        if st.button("Submit Answer", key=f"submit{q_index}"):
            st.session_state.quiz_answers[f"q{q_index}"] = selected
            st.session_state.submitted_flags[f"q{q_index}"] = True
        if st.session_state.submitted_flags.get(f"q{q_index}", False):
            st.markdown(f"📜 *Answer submitted: {st.session_state.quiz_answers[f'q{q_index}']}*")

    if st.button("Show Score for This Page"):
        all_answered = True
        for i, q in enumerate(questions):
            q_index = start_index + i
            if f"q{q_index}" not in st.session_state.quiz_answers:
                st.error(f"⚠️ Q{q_index+1} is unanswered. Please answer all questions before viewing score.")
                all_answered = False
        if all_answered:
            for i, q in enumerate(questions):
                q_index = start_index + i
                selected = st.session_state.quiz_answers.get(f"q{q_index}", None)
                if selected:
                    if selected == q['answer']:
                        st.success(f"Q{q_index+1}: ✅ Correct")
                        score += 1
                    else:
                        st.error(f"Q{q_index+1}: ❌ Incorrect. Correct Answer: {q['answer']}")
                    st.info(q['explanation'])
            st.markdown("---")
            st.write(f"### ✅ Your Score: {score}/{len(questions)}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Previous Page") and page > 1:
            st.session_state[f"{subject}_page"] -= 1
            st.rerun()
    with col2:
        if st.button("Next Page ➡") and page < total_pages:
            st.session_state[f"{subject}_page"] += 1
            st.rerun()

# --- Shortcut Tips Section ---
elif section == "Shortcut Tips":
    st.subheader("Shortcut Tricks and Concepts")
    selected_subject = st.selectbox("Choose subject to view tips", list(shortcut_notes.keys()), key="tip_subject")
    for i, tip in enumerate(shortcut_notes[selected_subject], 1):
        st.markdown(f"**Tip {i}:** {tip}")

# --- Cross Multiplication Practice Section ---
elif section == "Cross Multiplication Practice":
    st.subheader("🕟 Advanced Cross Multiplication Problems")
    st.markdown("These are tough but solvable with cancellation. Take 2–3 minutes each.")

    if "cm_answers" not in st.session_state:
        st.session_state.cm_answers = {}
    if "cm_submitted" not in st.session_state:
        st.session_state.cm_submitted = {}
    if "cm_start_times" not in st.session_state:
        st.session_state.cm_start_times = {}
    if "cm_elapsed" not in st.session_state:
        st.session_state.cm_elapsed = {}
    if "cm_show_answer" not in st.session_state:
        st.session_state.cm_show_answer = {}

    for idx, q in enumerate(cross_multiplication_questions, 1):
        st.markdown(f"**Q{idx}:** `{q['expression']}`")

        user_input = st.text_input(f"Your answer for Q{idx}", key=f"cm_input_{idx}")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"Start Q{idx}"):
                st.session_state.cm_start_times[idx] = time.time()
                st.success("Timer started!")

        with col2:
            if st.button(f"Submit Q{idx}"):
                if idx in st.session_state.cm_start_times:
                    end_time = time.time()
                    st.session_state.cm_elapsed[idx] = round(end_time - st.session_state.cm_start_times[idx], 2)
                    st.session_state.cm_answers[idx] = user_input
                    st.session_state.cm_submitted[idx] = True
                else:
                    st.error("Please start the timer before submitting.")

        with col3:
            if st.button(f"Show Answer Q{idx}"):
                st.session_state.cm_show_answer[idx] = True

        if st.session_state.cm_submitted.get(idx):
            elapsed = st.session_state.cm_elapsed.get(idx, 0)
            if user_input == q['answer']:
                st.success(f"✅ Correct! (⏱️ {elapsed} sec)")
            else:
                st.warning("❌ Submitted. You can view the correct answer.")
                st.info(f"⏱️ Time taken: {elapsed} sec")

        if st.session_state.cm_show_answer.get(idx):
            st.info(f"📘 Correct Answer: {q['answer']}")

st.markdown("---")
st.caption("Built for Indian aspirants by an AI tutor. Powered by OpenAI.")
