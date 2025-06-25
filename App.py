import streamlit as st
import os
import random
from openai import OpenAI

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Quiz Data Example (You can expand this or load from a file) ---
quiz_data = {
    "English Language": [
        {
            "question": "Choose the correct synonym of 'Abundant'",
            "options": ["Rare", "Plentiful", "Insufficient", "Tiny"],
            "answer": "Plentiful",
            "explanation": "'Abundant' means available in large quantities, i.e., plentiful."
        },
        {
            "question": "Identify the part of speech of the word 'Quickly'",
            "options": ["Adjective", "Verb", "Noun", "Adverb"],
            "answer": "Adverb",
            "explanation": "'Quickly' describes how something is done, so it's an adverb."
        }
    ],
    "Reasoning Ability": [
        {
            "question": "If A = 1, B = 2, ..., what is the value of C + D + E?",
            "options": ["9", "10", "12", "15"],
            "answer": "12",
            "explanation": "C=3, D=4, E=5, so 3+4+5=12."
        }
    ],
    "Quantitative Aptitude": [
        {
            "question": "What is 25% of 160?",
            "options": ["30", "40", "50", "60"],
            "answer": "40",
            "explanation": "25% of 160 = (25/100) * 160 = 40."
        }
    ]
}

# --- UI Setup ---
st.set_page_config(page_title="Govt Exam AI Tutor", layout="centered")
st.title("🇮🇳 Govt Exam AI Tutor")
st.markdown("Practice and learn for SSC, Banking, Railways and more!")

# Sidebar for subject selection
st.sidebar.title("Navigation")
section = st.sidebar.radio("Choose Section", ["Chat with Tutor", "Take a Quiz"], key="section_selector")

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

    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = []
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "submitted_flags" not in st.session_state:
        st.session_state.submitted_flags = {}

    if st.button("Start Quiz"):
        st.session_state.quiz_started = True
        st.session_state.quiz_questions = random.sample(quiz_data[subject], min(3, len(quiz_data[subject])))
        st.session_state.quiz_answers = {}
        st.session_state.submitted_flags = {}

    if st.session_state.quiz_started:
        score = 0
        for i, q in enumerate(st.session_state.quiz_questions):
            st.write(f"**Q{i+1}: {q['question']}**")
            selected = st.radio("Choose one:", q['options'], key=f"q{i}_radio")
            if st.button("Submit Answer", key=f"submit{i}"):
                st.session_state.quiz_answers[f"q{i}"] = selected
                st.session_state.submitted_flags[f"q{i}"] = True
            if st.session_state.submitted_flags.get(f"q{i}", False):
                st.markdown(f"📝 *Answer submitted: {st.session_state.quiz_answers[f'q{i}']}*")

        # Display results
        if st.button("Show Final Score"):
            for i, q in enumerate(st.session_state.quiz_questions):
                selected = st.session_state.quiz_answers.get(f"q{i}", None)
                if selected:
                    if selected == q['answer']:
                        st.success(f"Q{i+1}: ✅ Correct")
                        score += 1
                    else:
                        st.error(f"Q{i+1}: ❌ Incorrect. Correct Answer: {q['answer']}")
                    st.info(q['explanation'])
            st.markdown("---")
            st.write(f"### ✅ Your Score: {score}/{len(st.session_state.quiz_questions)}")

st.markdown("---")
st.caption("Built for Indian aspirants by an AI tutor. Powered by OpenAI.")
