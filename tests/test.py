import pytest

from studymate import ai_engine


def test_empty_notes_are_rejected():
    with pytest.raises(ValueError):
        ai_engine.summarize_notes("   ")


def test_oversized_notes_are_rejected():
    with pytest.raises(ValueError):
        ai_engine.summarize_notes("x" * 20001)


def test_summary_demo_mode(monkeypatch):
    monkeypatch.setattr(ai_engine, "_generate_json", lambda prompt: None)

    result = ai_engine.summarize_notes(
        "Python is a programming language. "
        "It supports multiple programming paradigms."
    )

    assert result["mode"] == "Demo"
    assert result["summary"]
    assert len(result["key_points"]) >= 1


def test_flashcards_demo_mode(monkeypatch):
    monkeypatch.setattr(ai_engine, "_generate_json", lambda prompt: None)

    result = ai_engine.generate_flashcards(
        "Python is popular. Python supports automation.",
        count=2,
    )

    assert result["mode"] == "Demo"
    assert len(result["flashcards"]) == 2
    assert all(
        card["question"] and card["answer"]
        for card in result["flashcards"]
    )


def test_quiz_demo_mode(monkeypatch):
    monkeypatch.setattr(ai_engine, "_generate_json", lambda prompt: None)

    result = ai_engine.generate_quiz(
        "Python supports automation. Python has many libraries.",
        count=2,
    )

    assert result["mode"] == "Demo"
    assert len(result["questions"]) == 2

    for question in result["questions"]:
        assert len(question["options"]) == 4
        assert question["answer"] in question["options"]


def test_quiz_rejects_invalid_ai_options(monkeypatch):
    monkeypatch.setattr(
        ai_engine,
        "_generate_json",
        lambda prompt: {
            "questions": [
                {
                    "question": "Which is correct?",
                    "options": ["A", "B", "C", "D"],
                    "answer": "E",
                    "explanation": "Test explanation",
                }
            ]
        },
    )

    with pytest.raises(ai_engine.StudyMateError):
        ai_engine.generate_quiz("Example notes", count=1)


def test_flashcard_count_is_limited(monkeypatch):
    monkeypatch.setattr(ai_engine, "_generate_json", lambda prompt: None)

    result = ai_engine.generate_flashcards(
        "One fact. Two facts.",
        count=100,
    )

    assert len(result["flashcards"]) <= 10