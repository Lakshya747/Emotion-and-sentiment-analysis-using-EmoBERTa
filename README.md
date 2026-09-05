# Multi-Theoretical Emotion & Sentiment Analysis using EmoBERTa

An advanced Natural Language Processing system that evaluates text across two foundational psychological frameworks: **Paul Ekman's 6 Basic Emotions** and **Robert Plutchik's Wheel of Emotion**, while computing net sentiment valence and aggregate consensus metrics.

---

## Features

- **Transformer Backbone**: Powered by `tae898/emoberta-large`, fine-tuned for emotion detection.
- **Dual Psychological Frameworks**:
  - **Paul Ekman's 6 Basic Emotions**: Joy, Sadness, Anger, Fear, Disgust, and Surprise.
  - **Robert Plutchik's Wheel of Emotion**: 8 primary emotions including derived higher-order states (**Trust** and **Anticipation**).
- **Valence-Based Sentiment**: Quantifies net positive vs. negative emotional density.
- **Grouped Movie Reviews Dataset**: 23 blockbuster films with multi-perspective reviews, enabling individual scoring and **Audience Emotional Consensus** calculation.
- **Forgiving Fuzzy Search**: Typo-tolerant search supporting character aliases (e.g., *"Batman"* for *The Dark Knight*) and partial matches.
- **GPU Accelerated**: Runs locally with CUDA acceleration on NVIDIA RTX GPUs.

---

## Project Structure

```
emotion_analysis/
├── app.py                       # Main interactive CLI application
├── emotion_analyzer.py          # Core inference engine (EmoBERTa + Ekman/Plutchik mapping)
├── movies_reviews_dataset.json  # 23 films with authentic critic/audience reviews
├── reviews_app.py               # Standalone runner for Rotten Tomatoes reviews
├── tmdb_analyzer.py             # TMDb dataset runner
├── generate_pdf_report.py       # Script to compile formal 2-page briefing PDF
├── Emotion_AI_Project_Report.pdf# Compiled 2-page executive report
├── REPORT.md                    # Detailed technical markdown report
├── requirements.txt             # Python dependencies
└── .gitignore                   # Ignored files (virtualenv, caches)
```

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Lakshya747/<repo-name>.git
   cd <repo-name>
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### 1. Interactive Menu Application
Launch the terminal interface:
```bash
python app.py
```

Menu options:
- **Option 1**: Randomly select a movie and analyze all its reviews + consensus.
- **Option 2**: Search for any movie by title, character, or director.
- **Option 3**: Add and analyze a custom movie review in real time.
- **Option 4**: Exit.

### 2. Standalone Python Usage
```python
from emotion_analyzer import EmotionAnalyzer

analyzer = EmotionAnalyzer()
result = analyzer.predict("A towering, breathtaking masterpiece of modern cinema.")
print(result)
```

---

## Executive Report
A formal 2-page project briefing suitable for academic presentation is included:
- PDF version: `Emotion_AI_Project_Report.pdf`
- Markdown version: `REPORT.md`
- To re-compile the PDF: `python generate_pdf_report.py`
