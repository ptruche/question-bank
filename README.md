# Local TrueLearn‑Style Question Bank (Streamlit)

## Quick Start
1. **Install Python 3.10+** and create a virtual environment (recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```
4. Load your own questions via the sidebar **Upload**. A starter `questions_sample.csv` is included.

## CSV/Excel Format (required columns)
`Question, A, B, C, D, E, Correct, Explanation, Reference, Category, Difficulty`

- **Correct** must be a single letter `A`–`E`.
- **Reference** can be a PubMed URL or any link.
- Extra columns are ignored.

## Features
- One‑question‑per‑page UI with **Submit → Explanation → Next** flow
- **Filters** by Category and Difficulty; **Shuffle**; **Flag** and **Favorite**
- **Review mode** (see questions + explanations without answering)
- **Progress tracking** with per‑topic accuracy
- **Export results** to CSV and auto‑save `progress.json` locally
