
import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

st.set_page_config(page_title="Question Bank (Local)", page_icon="❓", layout="wide")

REQUIRED_COLS = ["Question","A","B","C","D","E","Correct","Explanation","Reference","Category","Difficulty"]
PROGRESS_FILE = "progress.json"

# ---------- Helpers ----------
def load_dataframe(file):
    if file is None:
        # try bundled sample
        sample_path = os.path.join(os.path.dirname(__file__), "questions_sample.csv")
        if os.path.exists(sample_path):
            df = pd.read_csv(sample_path)
        else:
            return None
    else:
        name = getattr(file, "name", "")
        if name.lower().endswith((".xlsx",".xls")):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file)
    # ensure required columns
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}")
        return None
    # coerce Correct to uppercase single letter
    df["Correct"] = df["Correct"].astype(str).str.strip().str.upper()
    df["Correct"] = df["Correct"].str.replace("CHOICE ", "", case=False)
    # strip whitespace
    for c in ["Question","A","B","C","D","E","Explanation","Reference","Category","Difficulty"]:
        df[c] = df[c].astype(str).fillna("").str.strip()
    return df

def init_state():
    if "df" not in st.session_state:
        st.session_state.df = None
    if "indices" not in st.session_state:
        st.session_state.indices = []
    if "i" not in st.session_state:
        st.session_state.i = 0
    if "answers" not in st.session_state:
        st.session_state.answers = {}  # q_idx -> {"choice": "A"-"E", "is_correct": bool, "timestamp": str}
    if "flags" not in st.session_state:
        st.session_state.flags = set()
    if "favs" not in st.session_state:
        st.session_state.favs = set()
    if "show_expl" not in st.session_state:
        st.session_state.show_expl = False
    if "review_mode" not in st.session_state:
        st.session_state.review_mode = False
    if "filters" not in st.session_state:
        st.session_state.filters = {"Category": [], "Difficulty": []}
    if "shuffle" not in st.session_state:
        st.session_state.shuffle = True

def apply_filters(df):
    filt = st.session_state.filters
    mask = pd.Series([True]*len(df))
    for key in ["Category","Difficulty"]:
        vals = filt.get(key) or []
        if len(vals) > 0:
            mask &= df[key].isin(vals)
    return df[mask].reset_index(drop=True)

def rebuild_indices():
    df = st.session_state.df
    sub = apply_filters(df)
    idxs = list(range(len(sub)))
    if st.session_state.shuffle:
        rng = np.random.default_rng()
        rng.shuffle(idxs)
    st.session_state.indices = idxs
    st.session_state.i = 0
    st.session_state.answers = {}
    st.session_state.show_expl = False

def persist_progress():
    try:
        payload = {
            "timestamp": datetime.now().isoformat(),
            "answers": st.session_state.answers,
            "flags": list(st.session_state.flags),
            "favs": list(st.session_state.favs),
            "filters": st.session_state.filters,
            "shuffle": st.session_state.shuffle,
        }
        with open(PROGRESS_FILE, "w") as f:
            json.dump(payload, f, indent=2)
    except Exception as e:
        st.sidebar.warning(f"Could not save progress: {e}")

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                data = json.load(f)
            st.session_state.answers = {int(k): v for k, v in data.get("answers", {}).items()}
            st.session_state.flags = set(data.get("flags", []))
            st.session_state.favs = set(data.get("favs", []))
            st.session_state.filters = data.get("filters", {"Category": [], "Difficulty": []})
            st.session_state.shuffle = data.get("shuffle", True)
        except Exception:
            pass

# ---------- UI: Sidebar ----------
init_state()
st.sidebar.title("⚙️ Controls")
uploaded = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv","xlsx","xls"])
st.sidebar.caption("If nothing uploaded, a bundled sample will load.")

if st.sidebar.button("Load / Reload"):
    st.session_state.df = load_dataframe(uploaded)
    if st.session_state.df is not None:
        rebuild_indices()
        persist_progress()

if st.session_state.df is None:
    # initial auto-load
    st.session_state.df = load_dataframe(uploaded)
    if st.session_state.df is not None and not st.session_state.indices:
        load_progress()
        rebuild_indices()

if st.session_state.df is not None:
    df = st.session_state.df
    # Filters
    cats = sorted(list(df["Category"].dropna().unique()))
    diffs = sorted(list(df["Difficulty"].dropna().unique()))
    st.session_state.filters["Category"] = st.sidebar.multiselect("Filter by Category", cats, default=st.session_state.filters.get("Category", []))
    st.session_state.filters["Difficulty"] = st.sidebar.multiselect("Filter by Difficulty", diffs, default=st.session_state.filters.get("Difficulty", []))
    st.session_state.shuffle = st.sidebar.checkbox("Shuffle questions", value=st.session_state.shuffle)

    colA, colB = st.sidebar.columns(2)
    if colA.button("Apply filters"):
        rebuild_indices()
        persist_progress()
    if colB.button("Reset session"):
        rebuild_indices()
        st.session_state.flags = set()
        st.session_state.favs = set()
        persist_progress()

    st.sidebar.markdown("---")
    st.session_state.review_mode = st.sidebar.toggle("Review Mode (no answering)", value=st.session_state.review_mode, help="Read Q&A with explanations without recording answers.")

    # Export
    if st.sidebar.button("Export results CSV"):
        if st.session_state.answers:
            # Build results DataFrame
            sub = apply_filters(df)
            rows = []
            for j, idx in enumerate(st.session_state.indices):
                if idx in st.session_state.answers:
                    rec = st.session_state.answers[idx]
                    row = {
                        "QuestionIndex": idx,
                        "Question": sub.loc[idx, "Question"] if idx < len(sub) else "",
                        "YourChoice": rec.get("choice",""),
                        "Correct": sub.loc[idx, "Correct"] if idx < len(sub) else "",
                        "IsCorrect": rec.get("is_correct",""),
                        "Timestamp": rec.get("timestamp",""),
                        "Category": sub.loc[idx, "Category"] if idx < len(sub) else "",
                        "Difficulty": sub.loc[idx, "Difficulty"] if idx < len(sub) else "",
                    }
                    rows.append(row)
            if rows:
                out = pd.DataFrame(rows)
                st.sidebar.download_button("Download results.csv", out.to_csv(index=False).encode("utf-8"), file_name="results.csv", mime="text/csv")
        else:
            st.sidebar.info("No answers to export yet.")

# ---------- Main Content ----------
st.title("❓ Local TrueLearn‑Style Question Bank")
st.caption("Upload your CSV/Excel in the sidebar or use the bundled sample.")

if st.session_state.df is None or len(st.session_state.indices) == 0:
    st.info("Load questions to begin. Required columns: " + ", ".join(REQUIRED_COLS))
    st.stop()

df = st.session_state.df
sub = apply_filters(df)

# if filters remove all
if len(sub) == 0:
    st.warning("No questions match the current filters.")
    st.stop()

# Keep indices bounded
st.session_state.i = int(np.clip(st.session_state.i, 0, len(st.session_state.indices) - 1))
current_local_idx = st.session_state.indices[st.session_state.i]

# Display progress summary
answered = len(st.session_state.answers)
total = len(st.session_state.indices)
pct = (answered / total * 100) if total else 0
st.progress(min(pct/100, 1.0), text=f"Progress: {answered}/{total} answered ({pct:.0f}%)")

# Per-topic accuracy
with st.expander("📊 Performance by Category", expanded=False):
    if st.session_state.answers:
        # Map answers back to categories
        records = []
        for idx, rec in st.session_state.answers.items():
            if idx < len(sub):
                cat = sub.loc[idx, "Category"]
                records.append((cat, 1 if rec.get("is_correct") else 0))
        if records:
            perf = pd.DataFrame(records, columns=["Category","Correct"]).groupby("Category").agg(Attempts=("Correct","count"), Correct=("Correct","sum"))
            perf["Accuracy"] = (perf["Correct"] / perf["Attempts"] * 100).round(1)
            st.dataframe(perf)
        else:
            st.write("No graded attempts yet.")
    else:
        st.write("No answers yet.")

# Current question card
q = sub.loc[current_local_idx]

st.markdown(f"### Q{st.session_state.i+1}: {q['Question']}")
choices = {"A": q["A"], "B": q["B"], "C": q["C"], "D": q["D"], "E": q["E"]}

# flag/favorite row
ff1, ff2, ff3 = st.columns([1,1,6])
flagged = current_local_idx in st.session_state.flags
faved = current_local_idx in st.session_state.favs
if ff1.button("🚩 Flag" + (" ✓" if flagged else "")):
    if flagged: st.session_state.flags.remove(current_local_idx)
    else: st.session_state.flags.add(current_local_idx)
    persist_progress()
if ff2.button("⭐ Favorite" + (" ✓" if faved else "")):
    if faved: st.session_state.favs.remove(current_local_idx)
    else: st.session_state.favs.add(current_local_idx)
    persist_progress()

# Choice UI
if st.session_state.review_mode:
    st.info("Review Mode is ON — answers are not recorded.")
else:
    default_choice = None
    if current_local_idx in st.session_state.answers:
        default_choice = st.session_state.answers[current_local_idx]["choice"]
    user_choice = st.radio("Choose one:", [f"{k}. {v}" for k,v in choices.items()], index=list(choices.keys()).index(default_choice) if default_choice else 0, key=f"choice_{current_local_idx}")
    # Parse selected letter
    letter = user_choice.split(".")[0]

# Submit / Explanation logic
cols = st.columns([1,1,1,6])
with cols[0]:
    if st.button("Submit", disabled=st.session_state.review_mode):
        is_correct = (letter == q["Correct"])
        st.session_state.answers[current_local_idx] = {
            "choice": letter,
            "is_correct": bool(is_correct),
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.show_expl = True
        if is_correct:
            st.success("✅ Correct")
        else:
            st.error(f"❌ Incorrect. Correct answer: **{q['Correct']}**")
        persist_progress()
with cols[1]:
    if st.button("Show explanation"):
        st.session_state.show_expl = True
with cols[2]:
    if st.button("Hide explanation"):
        st.session_state.show_expl = False

# Explanation
if st.session_state.show_expl or st.session_state.review_mode:
    st.markdown("**Explanation**")
    st.info(q["Explanation"])
    if q["Reference"] and str(q["Reference"]).lower().startswith(("http://","https://")):
        st.markdown(f"[Reference]({q['Reference']})")

# Navigation
nav1, nav2, nav3 = st.columns([1,1,6])
with nav1:
    if st.button("⬅️ Previous", disabled=st.session_state.i == 0):
        st.session_state.i = max(0, st.session_state.i - 1)
        st.session_state.show_expl = False
with nav2:
    if st.button("Next ➡️", disabled=st.session_state.i >= len(st.session_state.indices) - 1):
        st.session_state.i = min(len(st.session_state.indices) - 1, st.session_state.i + 1)
        st.session_state.show_expl = False

# Footer tips
st.markdown("---")
st.caption("Tip: Use the sidebar to filter by Category/Difficulty, toggle shuffle, and export results. Progress autosaves to 'progress.json' in this folder.")
