Drift Lab (drift-lab)
This is a lightweight Flask-based web application for visualizing and diagnosing AI prompt drift, with a specific focus on demonstrating "context collapse." It's designed as a strategic tool to make abstract AI reliability risks tangible for a business or product audience.

The application allows a user to input a prompt and simulates a multi-step conversation where each AI response is fed back as the context for the next step, intentionally creating a "stateless" environment. It then uses multiple instruments to measure and explain the resulting drift.

Features
Drift Simulation: Runs a multi-step simulation to demonstrate how an AI's purpose can drift over time without proper context management.

Dual-Metric Scoring: Measures both Prompt Fidelity (thematic relevance) and Language Complexity (creative entropy) to provide a nuanced view of drift.

Constraint Violation Penalty: Automatically detects and penalizes the score when a response violates a negative constraint (e.g., "don't mention X").

AI-Powered Analysis: Uses a second AI call to act as an analyst, summarizing the simulation's results in a clear, easy-to-understand format.

Visual Instrumentation: Includes a "Drift Gauge" to provide an at-a-glance visualization of the final drift state.

History Tracking: Saves every run to a SQLite database for later review and analysis.

Technologies Used
Python 3.10+

Flask

OpenAI API

Scikit-learn (for Cosine Similarity & TF-IDF)

NumPy / SciPy (for Entropy Calculation)

SQLite

HTML/CSS/JavaScript

Run the App
Create a virtual environment and install dependencies:

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

You will also need to set your OpenAI API key as an environment variable. You can do this by creating a .env file in the root of the project with the following content:

OPENAI_API_KEY='your-api-key-here'

Finally, run the application:

python app.py

Project Structure
drift-lab/
|
├── app.py                  # Main Flask application
├── openai_utils.py         # Functions for OpenAI calls & scoring
├── db.py                   # Database initialization and helpers
├── prompt_templates.py     # Default prompt examples
├── requirements.txt        # Python dependencies
├── database.db             # SQLite database file
├── README.md               # This file
|
├── static/                 # CSS/JS files (if any)
|
└── templates/              # HTML templates
    ├── index.html
    ├── history.html
    └── prompt_detail.html
