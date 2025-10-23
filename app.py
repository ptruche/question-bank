import streamlit as st
import pandas as pd
import numpy as np
import os, sys, json
from datetime import datetime

# ----------------------------
# BASIC PAGE
# ----------------------------
st.set_page_config(page_title="Question Bank (Safe Mode)", page_icon="🧪", layout="wide")
st.title("🧪 Question Bank — Safe Mode (CSV only)")

# ----------------------------
# DIAGNOSTICS PANEL
# ----------------------------
st.sidebar.header("🔍 Diagnostics")

# Python & packages
st.sidebar.write("**Python**:", sys.version)
try:
    st.sidebar.write("**pandas**:", pd.__version__)
except Exception as e:
    st.sidebar.error(f"pandas import failed: {e}")
try:
    import numpy as _np
    st.sidebar.write("**numpy**:", _np.__version__)
except Exception as e:
    st.sidebar.error(f"numpy import failed: {e}")

# Repo structure / data
DATA_DIR = "data"
st.sidebar.write("**Working dir**:", os.getcwd())
st.sidebar.write("**Repo files**:", sorted(os.listdir("."))[:50])
st.sidebar.write("**data/ exists**:", os.path.isdir(DATA_DIR))

csv_files = []
if os.path.isdir(DATA_DIR):
    csv_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".csv") and not f.startswith(".")]
    st.sidebar.write("**CSV files in data/**:", csv_files)

if not os.path.isdir(DATA_DIR) or not csv_files:
    st.error("No CSV files found in `data/`. Add at least one CSV with headers: "
             "Question,A,B,C,D,E,Correct,Explanation,Reference,Category,Difficulty")
    st.stop()

# ----------------------------
# CSV-ONLY LOADER (NO CACHING IN SAFE MODE)
# ----------------------------
REQUIRED = ["Question","A","B","C","D","E","Correct","Explanation","Reference","Category","Difficulty"]

def load_csv_strict(path: str) -> pd.DataFrame:
    """
    Robust CSV loader:
      - UTF-8-sig first (handles BOM), fallback to UTF-8 then Latin-1
      - dtype=str to keep text choices intact
      - no NA coercion so 'NA' is not turned into NaN
    """
    last_err = None
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            df = pd.read_csv(
                path,
                encoding=enc,
                dtype=str,
                keep_default_na=False,
                na_filter=False,
                low_memory=False
            )
            # Strip weird BOM from first column name if present
            df.columns = [c.replace("\ufeff", "").strip() for c in df.columns]
            return df
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Failed to read CSV '{path}': {last_err}")

def validate_and_clean(df: pd.DataFrame, fname: str) -> pd.DataFrame:
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"{fname}: missing columns {missing}. Required: {REQUIRED}")

    # Normalize/clean minimal set so app won’t hang on bad types
    df["Correct"] = df["Correct"].astype(str).str.strip().str.upper()
    for c in ["Question","A","B","C","D","E","Explanation","Reference","Category","Difficulty"]:
        df[c] = df[c].astype(str).str.strip()
    df["__sourcefile__"] = fname
    return df

# ----------------------------
# PICK WHAT TO LOAD
# ----------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Repository Controls")
use_all = st.sidebar.toggle("Use ALL CSV sets", value=True)
if use_all:
    selected = csv_files
else:
    selected = st.sidebar.multiselect("Choose CSV set(s)", csv_files, default=csv_files[:1])

if not selected:
    st.warning("Select at least one CSV set on the left.")
    st.stop()

# ----------------------------
# LOAD WITH ERROR VISIBILITY
# ----------------------------
frames = []
errors = []
with st.spinner("Loading CSV question sets..."):
    for fname in selected:
        path = os.path.join(DATA_DIR, fname)
        try:
            df = load_csv_strict(path)
            df = validate_and_clean(df, fname)
            frames.append(df)
        except Exception as e:
            errors.append((fname, str(e)))

if errors:
    st.error("Some files failed to load. See details below.")
    for fname, msg in errors:
        st.code(f"{fname}: {msg}")
if not frames:
    st.error("No valid CSV loaded. Fix the errors above.")
    st.stop()

df = pd.concat(frames, ignore_index=True)

# ----------------------------
# QUICK PREVIEW
# ----------------------------
st.success(f"Loaded {len(df)} questions from {len(frames)} file(s): {', '.join([f['__sourcefile__'].iloc[0] for f in frames]) if isinstance(frames[0], pd.DataFrame) else ''}")
st.caption("Preview of the first 5 rows:")
st.dataframe(df.head(5), use_container_width=True)

# ----------------------------
# SIMPLE QUIZ LOOP (SAFE MODE)
# ----------------------------
st.markdown("---")
st.subheader("Quiz (Safe Mode)")
if "i" not in st.session_state: st.session_state.i = 0
if "indices" not in st.session_state:
    st.session_state.indices = list(range(len(df)))
    np.random.default_rng().shuffle(st.session_state.indices)

if st.session_state.i >= len(st.session_state.indices):
    st.session_state.i = 0

idx = st.session_state.indices[st.session_state.i]
q = df.loc[idx]

st.write(f"**Q{st.session_state.i+1}.** {q['Question']}")
choices = {"A": q["A"], "B": q["B"], "C": q["C"], "D": q["D"], "E": q["E"]}
opt = st.radio("Choose one:", [f"{k}. {v}" for k,v in choices.items()], index=0)
picked = opt.split(".")[0]

c1, c2, c3 = st.columns([1,1,6])
if c1.button("✅ Submit"):
    if picked == q["Correct"]:
        st.success(f"Correct. Answer: {q['Correct']}")
    else:
        st.error(f"Incorrect. Correct answer: {q['Correct']}")
    st.info("**Explanation**")
    st.write(q["Explanation"])
    if str(q["Reference"]).lower().startswith(("http://","https://")):
        st.markdown(f"[Reference]({q['Reference']})")

if c2.button("Next ➡️"):
    st.session_state.i = (st.session_state.i + 1) % len(st.session_state.indices)
    st.experimental_rerun()
