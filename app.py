import streamlit as st
import pandas as pd
import numpy as np
import json, os
from datetime import datetime

# ---------- Page & Style ----------
st.set_page_config(page_title="Question Bank", page_icon="🧠", layout="wide")

CUSTOM_CSS = """
<style>
.block-container {padding-top: 2rem; padding-bottom: 3rem;}
h1.title {font-weight: 800; letter-spacing:-0.02em;}
.card {
  background: #ffffff;
  border-radius: 18px;
  border: 1px solid rgba(17,24,39,0.06);
  box-shadow: 0 2px 12px rgba(2,6,23,0.05);
  padding: 1.25rem 1.25rem;
}
.card-dim {background: #f8fafc;}
.chip {
  display:inline-block; padding: 0.2rem 0.6rem; border-radius: 999px;
  font-size: 0.78rem; font-weight:600; background:#eef2ff; color:#3730a3; margin-right: .3rem;
  border: 1px solid rgba(59, 130, 246, 0.25);
}
.stButton>button {
  border-radius: 12px !important;
  padding: .6rem 1rem !important;
  font-weight: 600 !important;
  border: 1px solid rgba(17,24,39,.06) !important;
  box-shadow: 0 1px 6px rgba(2,6,23,.05) !important;
}
.stRadio [role='radiogroup'] label {padding:.35rem .55rem; border-radius:10px;}
.stRadio [role='radiogroup'] label:hover {background:#f3f4f6;}
[data-testid="stProgressBar"] + div p {font-weight:600;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- Constants ----------
REQUIRED = ["Question","A","B","C","D","E","Correct","Explanation","Reference","Category","Difficulty"]
PROGRESS_FILE = "progress.json"

# ---------- Helpers ----------
def load_dataframe(file):
    if file is None:
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

    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}")
        return None

    df["Correct"] = df["Correct"].astype(str).str.strip().str.upper()
    for c in ["Question","A","B","C","D","E","Explanation","Reference","Category","Difficulty"]:
        df[c] = df[c].astype(str).fillna("").str.strip()
    return df

def init_state():
    ss = st.session_state
    ss.setdefault("df", None)
    ss.setdefault("indices", [])
    ss.setdefault("i", 0)
    ss.setdefault("answers", {})     # idx -> {choice,is_correct,timestamp}
    ss.setdefault("flags", set())
    ss.setdefault("favs", set())
    ss.setdefault("show_expl", False)
    ss.setdefault("review_mode", False)
    ss.setdefault("filters", {"Category": [], "Difficulty": []})
    ss.setdefault("shuffle", True)

def apply_filters(df):
    filt = st.session_state.filters
    mask = pd.Series([True]*len(df))
    for key in ["Category","Difficulty"]:
        vals = filt.get(key) or []
        if vals:
            mask &= df[key].isin(vals)
    return df[mask].reset_index(drop=True)

def rebuild_indices():
    df = st.session_state.df
    sub = apply_filters(df)
    idxs = list(range(len(sub)))
    if st.session_state.shuffle:
        np.random.default_rng().shuffle(idxs)
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
    except Exception:
        pass

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

# ---------- Sidebar ----------
init_state()
st.sidebar.title("⚙️ Controls")

uploaded = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv","xlsx","xls"], help="Headers must match the sample.")
if st.sidebar.button("Load / Reload", type="primary", use_container_width=True):
    st.session_state.df = load_dataframe(uploaded)
    if st.session_state.df is not None:
        rebuild_indices()
        persist_progress()

if st.session_state.df is None:
    st.session_state.df = load_dataframe(uploaded)
    if st.session_state.df is not None and not st.session_state.indices:
        load_progress()
        rebuild_indices()

if st.session_state.df is not None:
    df = st.session_state.df
    cats = sorted(df["Category"].dropna().unique().tolist())
    diffs = sorted(df["Difficulty"].dropna().unique().tolist())

    with st.sidebar.expander("Filters", expanded=True):
        st.session_state.filters["Category"] = st.multiselect("Category", cats, default=st.session_state.filters.get("Category", []))
        st.session_state.filters["Difficulty"] = st.multiselect("Difficulty", diffs, default=st.session_state.filters.get("Difficulty", []))
        st.session_state.shuffle = st.toggle("Shuffle questions", value=st.session_state.shuffle)

        c1, c2 = st.columns(2)
        if c1.button("Apply", use_container_width=True):
            rebuild_indices(); persist_progress()
        if c2.button("Reset", use_container_width=True):
            rebuild_indices(); st.session_state.flags=set(); st.session_state.favs=set(); persist_progress()

    st.sidebar.markdown("---")
    st.session_state.review_mode = st.sidebar.toggle("📖 Review Mode (no grading)", value=st.session_state.review_mode)

    # Export
    if st.sidebar.button("⬇️ Export results CSV", use_container_width=True):
        if st.session_state.answers:
            sub = apply_filters(df)
            rows = []
            for idx in st.session_state.answers:
                if idx < len(sub):
                    rec = st.session_state.answers[idx]
                    rows.append({
                        "QuestionIndex": idx,
                        "Question": sub.loc[idx, "Question"],
                        "YourChoice": rec.get("choice",""),
                        "Correct": sub.loc[idx, "Correct"],
                        "IsCorrect": rec.get("is_correct",""),
                        "Timestamp": rec.get("timestamp",""),
                        "Category": sub.loc[idx, "Category"],
                        "Difficulty": sub.loc[idx, "Difficulty"],
                    })
            if rows:
                out = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
                st.sidebar.download_button("Download results.csv", out, "results.csv", "text/csv", use_container_width=True)
        else:
            st.sidebar.info("No answers to export yet.")

# ---------- Main ----------
st.markdown("<h1 class='title'>🧠 Question Bank</h1>", unsafe_allow_html=True)
st.caption("Clean UI • Explanations • Filters • Progress • Flags/Favorites")

if st.session_state.df is None or len(st.session_state.indices) == 0:
    st.info("Upload or load questions to begin. Required columns: " + ", ".join(REQUIRED))
    st.stop()

df = st.session_state.df
sub = apply_filters(df)
if len(sub) == 0:
    st.warning("No questions match the current filters.")
    st.stop()

st.session_state.i = int(np.clip(st.session_state.i, 0, len(st.session_state.indices)-1))
local_idx = st.session_state.indices[st.session_state.i]
q = sub.loc[local_idx]

# Header row: progress + chips
answered = len(st.session_state.answers); total = len(st.session_state.indices)
pct = int((answered/total)*100) if total else 0
st.progress(min(pct/100, 1.0), text=f"Progress: {answered}/{total} answered • {pct}%")

chip_row = []
if q["Category"]:
    chip_row.append(f"<span class='chip'>Category: {q['Category']}</span>")
if q["Difficulty"]:
    chip_row.append(f"<span class='chip'>Difficulty: {q['Difficulty']}</span>")
st.markdown(" ".join(chip_row), unsafe_allow_html=True)

# Question card
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown(f"### Q{st.session_state.i+1}")
st.markdown(f"**{q['Question']}**")

choices = {"A": q["A"], "B": q["B"], "C": q["C"], "D": q["D"], "E": q["E"]}

c_top = st.columns([1,1,6])
flagged = local_idx in st.session_state.flags
faved = local_idx in st.session_state.favs
if c_top[0].button(("🚩 Unflag" if flagged else "🚩 Flag"), use_container_width=True):
    if flagged: st.session_state.flags.remove(local_idx)
    else: st.session_state.flags.add(local_idx); persist_progress()
if c_top[1].button(("⭐ Unfavorite" if faved else "⭐ Favorite"), use_container_width=True):
    if faved: st.session_state.favs.remove(local_idx)
    else: st.session_state.favs.add(local_idx); persist_progress()

# Answer UI
if st.session_state.review_mode:
    st.info("Review Mode is ON — answers are not recorded.")
    letter = None
else:
    default_letter = st.session_state.answers.get(local_idx, {}).get("choice")
    options = [f"{k}. {v}" for k,v in choices.items()]
    start_index = list(choices.keys()).index(default_letter) if default_letter in choices else 0
    pick = st.radio("Choose one:", options, index=start_index)
    letter = pick.split(".")[0]

# Actions
col = st.columns([1,1,1,6])
if col[0].button("✅ Submit", disabled=st.session_state.review_mode, use_container_width=True):
    is_correct = (letter == q["Correct"])
    st.session_state.answers[local_idx] = {"choice": letter, "is_correct": bool(is_correct), "timestamp": datetime.now().isoformat()}
    st.session_state.show_expl = True
    if is_correct: st.success("Correct ✅")
    else: st.error(f"Incorrect ❌  •  Correct answer: **{q['Correct']}**")
    persist_progress()
if col[1].button("👁 Show explanation", use_container_width=True):
    st.session_state.show_expl = True
if col[2].button("🙈 Hide explanation", use_container_width=True):
    st.session_state.show_expl = False

# Explanation card
if st.session_state.show_expl or st.session_state.review_mode:
    st.markdown("<div class='card card-dim'>", unsafe_allow_html=True)
    st.markdown("**Explanation**")
    st.write(q["Explanation"])
    if q["Reference"].lower().startswith(("http://","https://")):
        st.markdown(f"[Reference]({q['Reference']})")
    st.markdown("</div>", unsafe_allow_html=True)

# Navigation
nav = st.columns([1,1,6])
if nav[0].button("⬅️ Previous", disabled=st.session_state.i==0, use_container_width=True):
    st.session_state.i = max(0, st.session_state.i-1); st.session_state.show_expl=False
if nav[1].button("Next ➡️", disabled=st.session_state.i>=len(st.session_state.indices)-1, use_container_width=True):
    st.session_state.i = min(len(st.session_state.indices)-1, st.session_state.i+1); st.session_state.show_expl=False

st.markdown("</div>", unsafe_allow_html=True)  # close question card

# Performance by category
with st.expander("📊 Performance by Category"):
    if st.session_state.answers:
        rows = []
        for idx, rec in st.session_state.answers.items():
            if idx < len(sub):
                rows.append((sub.loc[idx, "Category"], 1 if rec.get("is_correct") else 0))
        if rows:
            perf = pd.DataFrame(rows, columns=["Category","Correct"]).groupby("Category").agg(Attempts=("Correct","count"), Correct=("Correct","sum"))
            perf["Accuracy"] = (perf["Correct"] / perf["Attempts"] * 100).round(1)
            st.dataframe(perf, use_container_width=True)
    else:
        st.write("No graded attempts yet.")

st.caption("Tip: Use the sidebar to filter topics, toggle shuffle, and export results. Progress autosaves locally.")
