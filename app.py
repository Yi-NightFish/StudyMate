"""Streamlit interface for AI StudyMate."""

import json

import streamlit as st

from studymate.ai_engine import (
    StudyMateError,
    generate_flashcards,
    generate_quiz,
    summarize_notes,
)
from studymate.database import (
    delete_session,
    get_session,
    list_sessions,
    save_session,
)

st.set_page_config(
    page_title="AI StudyMate",
    page_icon="📚",
    layout="wide",
)

st.title("📚 AI StudyMate")
st.caption("Turn your study notes into summaries, flashcards, and quizzes.")

with st.sidebar:
    st.header("About")
    st.write(
        "An AI-assisted revision tool built with Python, Streamlit, "
        "Gemini, and SQLite."
    )
    st.divider()

    try:
        configured = bool(st.secrets.get("GEMINI_API_KEY", ""))
    except Exception:
        configured = False

    import os

    configured = configured or bool(os.getenv("GEMINI_API_KEY"))

    if configured:
        st.success("AI mode configured")
    else:
        st.info("Demo mode — no API key detected")

    st.caption("Do not enter passwords or sensitive personal information.")


def show_mode(result: dict) -> None:
    """Display whether a result came from the AI or demo engine."""
    if result.get("mode") == "AI":
        st.caption("Generated using Gemini AI.")
    else:
        st.info(
            "Demo mode: results use simple text-based examples, "
            "not actual AI-generated content."
        )


def save_result(
    title: str,
    session_type: str,
    result: dict,
) -> None:
    """Persist a result and report success or failure."""
    try:
        session_id = save_session(title, session_type, result)
        st.success(f"Saved to study history (ID: {session_id}).")
    except Exception:
        st.error("Could not save this session. Check database permissions.")


def render_summary(result: dict) -> None:
    """Render a generated summary."""
    show_mode(result)

    st.subheader("Summary")
    st.write(result["summary"])

    st.subheader("Key points")
    for point in result.get("key_points", []):
        st.markdown(f"- {point}")

    concepts = result.get("concepts", [])
    if concepts:
        st.subheader("Important concepts")
        st.write(", ".join(concepts))

    st.download_button(
        "Download summary",
        data=json.dumps(result, indent=2, ensure_ascii=False),
        file_name="studymate_summary.json",
        mime="application/json",
        key="download_summary",
    )


def render_flashcards(result: dict, key_prefix: str) -> None:
    """Render flashcards with interactive answers."""
    show_mode(result)

    for index, card in enumerate(result["flashcards"]):
        with st.container(border=True):
            st.markdown(f"**Card {index + 1}**")
            st.write(card["question"])

            with st.expander("Reveal answer"):
                st.write(card["answer"])

    st.download_button(
        "Download flashcards",
        data=json.dumps(result, indent=2, ensure_ascii=False),
        file_name="studymate_flashcards.json",
        mime="application/json",
        key=f"{key_prefix}_download",
    )


def render_quiz(result: dict, key_prefix: str) -> None:
    """Render a quiz and score the user's selected answers."""
    show_mode(result)

    questions = result["questions"]
    answers = []

    with st.form(f"{key_prefix}_quiz_form"):
        for index, question in enumerate(questions):
            st.markdown(f"**Question {index + 1}.** {question['question']}")

            options = question["options"]
            selection = st.radio(
                "Choose an answer",
                options,
                index=None,
                key=f"{key_prefix}_answer_{index}",
                label_visibility="collapsed",
            )
            answers.append(selection)

        submitted = st.form_submit_button("Submit quiz")

    if submitted:
        score = sum(
            selected == question["answer"]
            for selected, question in zip(answers, questions)
        )

        st.subheader(f"Your score: {score}/{len(questions)}")
        st.progress(score / len(questions))

        for index, (selected, question) in enumerate(
            zip(answers, questions)
        ):
            correct = selected == question["answer"]

            if correct:
                st.success(f"Question {index + 1}: Correct")
            else:
                st.error(
                    f"Question {index + 1}: Incorrect or unanswered. "
                    f"Answer: {question['answer']}"
                )

            st.caption(question["explanation"])


summary_tab, flashcards_tab, quiz_tab, history_tab = st.tabs(
    ["📝 Summarize", "🗂️ Flashcards", "✅ Quiz", "🕘 History"]
)

with summary_tab:
    st.subheader("Summarize your notes")

    summary_notes = st.text_area(
        "Paste your notes",
        height=220,
        placeholder="Paste your class notes here...",
        key="summary_notes",
    )

    if st.button("Generate summary", type="primary"):
        try:
            with st.spinner("Preparing your summary..."):
                result = summarize_notes(summary_notes)

            st.session_state["latest_summary"] = result
            st.session_state["latest_summary_source"] = summary_notes
        except (ValueError, StudyMateError) as exc:
            st.error(str(exc))

    if "latest_summary" in st.session_state:
        result = st.session_state["latest_summary"]
        render_summary(result)

        if st.button("Save summary", key="save_summary"):
            save_result("Study notes summary", "summary", result)

with flashcards_tab:
    st.subheader("Create revision flashcards")

    flashcard_notes = st.text_area(
        "Paste your notes",
        height=220,
        placeholder="Enter notes to turn into flashcards...",
        key="flashcard_notes",
    )

    flashcard_count = st.slider(
        "Number of flashcards",
        min_value=1,
        max_value=10,
        value=5,
        key="flashcard_count",
    )

    if st.button("Generate flashcards", type="primary"):
        try:
            with st.spinner("Creating flashcards..."):
                result = generate_flashcards(
                    flashcard_notes, flashcard_count
                )

            st.session_state["latest_flashcards"] = result
        except (ValueError, StudyMateError) as exc:
            st.error(str(exc))

    if "latest_flashcards" in st.session_state:
        result = st.session_state["latest_flashcards"]
        render_flashcards(result, "flashcards")

        if st.button("Save flashcards", key="save_flashcards"):
            save_result("Revision flashcards", "flashcards", result)

with quiz_tab:
    st.subheader("Test your knowledge")

    quiz_notes = st.text_area(
        "Paste your notes",
        height=220,
        placeholder="Enter notes to create a multiple-choice quiz...",
        key="quiz_notes",
    )

    quiz_count = st.slider(
        "Number of questions",
        min_value=1,
        max_value=10,
        value=5,
        key="quiz_count",
    )

    if st.button("Generate quiz", type="primary"):
        try:
            with st.spinner("Building your quiz..."):
                result = generate_quiz(quiz_notes, quiz_count)

            st.session_state["latest_quiz"] = result
        except (ValueError, StudyMateError) as exc:
            st.error(str(exc))

    if "latest_quiz" in st.session_state:
        result = st.session_state["latest_quiz"]
        render_quiz(result, "active_quiz")

        if st.button("Save quiz", key="save_quiz"):
            save_result("Practice quiz", "quiz", result)

with history_tab:
    st.subheader("Saved study sessions")

    try:
        sessions = list_sessions()
    except Exception:
        sessions = []
        st.error("Could not load study history.")

    if not sessions:
        st.info("No saved sessions yet. Generate and save some study material.")
    else:
        session_options = {
            f"#{item['id']} · {item['title']} "
            f"({item['session_type']}) · {item['created_at']}": item["id"]
            for item in sessions
        }

        selected_label = st.selectbox(
            "Choose a saved session",
            list(session_options.keys()),
        )
        selected_id = session_options[selected_label]

        session = get_session(selected_id)

        if session:
            st.markdown(f"**{session['title']}**")
            st.caption(
                f"Type: {session['session_type']} · "
                f"Saved: {session['created_at']}"
            )

            content = session["content"]
            session_type = session["session_type"]

            if session_type == "summary":
                render_summary(content)
            elif session_type == "flashcards":
                render_flashcards(content, f"history_{selected_id}")
            elif session_type == "quiz":
                render_quiz(content, f"history_{selected_id}")
            else:
                st.json(content)

            st.download_button(
                "Export saved session",
                data=json.dumps(content, indent=2, ensure_ascii=False),
                file_name=f"studymate_session_{selected_id}.json",
                mime="application/json",
                key=f"export_{selected_id}",
            )

            confirm_delete = st.checkbox(
                "I want to delete this saved session",
                key=f"confirm_delete_{selected_id}",
            )

            if st.button(
                "Delete session",
                disabled=not confirm_delete,
                key=f"delete_{selected_id}",
            ):
                if delete_session(selected_id):
                    st.success("Session deleted.")
                    st.rerun()
                else:
                    st.warning("The session was already removed.")

st.divider()
st.caption(
    "AI StudyMate · Built with Python · "
    "Always verify important information against your course materials."
)