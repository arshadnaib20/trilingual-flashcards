# Trilingual Flashcards

A small vocabulary trainer for the three languages I use every day:
**Bengali (বাংলা), English, and Chinese (中文).**

Built with **Python (Flask)** and **SQLite**, with a plain HTML/CSS/JavaScript frontend.
It is my way of combining Python with web development in one small, runnable project.

## Features

- Flashcards with randomized directions: English → Bengali, Bengali → Chinese,
  Chinese → English, and every other combination of the three languages
- Type-in answers with instant feedback
- Progress stats: answered, correct, accuracy
- Add your own words from the page — the deck grows with you
- Starts with 24 common everyday words

## Run it

```bash
pip install -r requirements.txt
python app.py
```

Then open <http://127.0.0.1:5000>.

The database file (`flashcards.db`) is created automatically on first run.

## Project layout

```
app.py              Flask routes and SQLite setup
seed_data.py        The starter deck (24 words)
templates/index.html  Page structure
static/style.css    Styling
static/app.js       Flashcard logic
```

## Notes

- This is a learning project: the starter deck is intentionally small and
  everyday, and the app is designed to be simple enough to read end to end.
