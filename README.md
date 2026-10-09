StudyMate 

An AI-powered study assistant built with Python that transforms study notes into summaries, revision flashcards, and multiple-choice quizzes.

Overview

StudyMate helps students revise more efficiently by converting their notes into interactive study materials. It uses Google's Gemini API for AI-generated content and SQLite for local study history.

A demo mode is also included so users can explore the core interface without configuring an API key.

Features
AI Summarization: Generate concise summaries, key points, and important concepts.
Flashcard Generation: Convert notes into question-and-answer cards.
Quiz Generation: Create multiple-choice questions and check answers.
Score Tracking: Calculate quiz scores and display explanations.
Study History: Save, retrieve, export, and delete generated sessions.
JSON Export: Download study materials for reuse.
Demo Mode: Explore basic functionality without an AI API key.
Automated Tests: Validate input handling and generated quiz structure.

Tech Stack
Python
Streamlit
Google Gemini API (google-genai)
SQLite
Pytest
Git and GitHub
Project Structure
ai-studymate/
├── app.py
├── studymate/
│   ├── __init__.py
│   ├── ai_engine.py
│   └── database.py
├── tests/
│   └── test.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md

Requirements
Python 3.10 or newer
pip
An internet connection for AI generation
A Gemini API key for AI-powered features
Installation
1. Clone the repository
git clone https://github.com/Yi-NightFish/studymate.git
cd studymate

2. Create a virtual environment

Windows:

py -m venv .venv
.venv\Scripts\activate


macOS / Linux:

python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

4. Configure the API key (optional)

Copy .env to .env and add your Gemini API key:

GEMINI_API_KEY=your_actual_api_key
GEMINI_MODEL=gemini-2.5-flash


Obtain an API key through Google AI Studio.

Keep your real API key private. Never commit .env to GitHub.

Without an API key, the app uses demo mode. Demo outputs are illustrative and should not be treated as genuine AI-generated answers.

5. Run the application
streamlit run app.py


Streamlit will display a local URL, usually http://localhost:8501.

Run Tests
pytest -q


The tests use demo-mode behavior and do not require a real Gemini API key.

How to Use
Open StudyMate in your browser.
Paste study notes into the Summarize, Flashcards, or Quiz tab.
Generate the desired study material.
Review the summary, reveal flashcard answers, or submit the quiz.
Save useful results to your local study history.
Export saved materials as JSON when needed.
Architecture
app.py handles the Streamlit interface and session state.
studymate/ai_engine.py validates input and generates study materials using Gemini or demo-mode logic.
studymate/database.py manages SQLite persistence.
tests/test.py tests core generation and validation behavior.
Limitations
Demo mode uses simple text-based examples; it does not provide actual AI reasoning.
AI output can contain mistakes. Verify important information against trusted course materials.
Study history is stored locally and is not synchronized between devices.
The initial version does not include user accounts or multi-user data isolation.
AI features depend on API availability, model access, usage limits, and applicable costs.

Future Improvements
PDF and DOCX note uploads
User authentication and cloud-based storage
Spaced-repetition scheduling
More question types and difficulty levels
Subject-specific study templates
Docker support and continuous integration
Improved UI design and accessibility
More comprehensive integration tests
Security
API keys should be stored outside source code.
Uploaded or pasted notes should be treated as untrusted input.
Do not submit passwords, confidential documents, or sensitive personal data.
Review and verify AI-generated educational content.

Author
Tan Wan Yi
GitHub: https://github.com/Yi-NightFish

Built as a Python and AI portfolio project to explore generative AI integration, input validation, database persistence, and automated testing.