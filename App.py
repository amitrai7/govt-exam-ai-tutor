import streamlit as st
import os
import random
import json
from openai import OpenAI

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Load Quiz Data from JSON File ---
@st.cache_data
def load_quiz_data():
    with open("quiz_questions", "r") as f:
        return json.load(f)

quiz_data = load_quiz_data()

# --- Shortcut Notes Data ---
shortcut_notes = {
    "English Language": "**Tip:** Learn root words. For example, 'bene' means good → beneficial, benevolent.",
    "Reasoning Ability": "**Tip:** Practice blood relation and direction problems using diagrams to avoid confusion.",
    "Quantitative Aptitude": "**Tip:** Use the formula A = (P × R × T)/100 for simple interest. Learn tables till 20 by heart."
}

# --- UI Setup ---
st.set_page_config(page_title="Govt Exam AI Tutor", layout="centered")
st.title("🇮🇳 Govt Exam AI Tutor")
st.markdown("Practice and learn for SSC, Banking, Railways and more!")

# Sidebar for subject selection
st.sidebar.title("Navigation")
section = st.sidebar.radio("Choose Section", ["Chat with Tutor", "Take a Quiz", "Shortcut Tips"], key="section_selector")

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
    total_pages = len(total_questions) // 5

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
            st.markdown(f"📝 *Answer submitted: {st.session_state.quiz_answers[f'q{q_index}']}*")

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
    st.markdown(shortcut_notes[selected_subject])

st.markdown("---")
st.caption("Built for Indian aspirants by an AI tutor. Powered by OpenAI.")
