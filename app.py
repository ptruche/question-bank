import streamlit as st
import pandas as pd
import numpy as np
import os, json
from datetime import datetime
from typing import List

# =========================
# OFFICIAL CATEGORY LIST (ordered)
# =========================
CATEGORIES_MASTER = [
"Bronchoscopy",
"Chest Wall Deformities: Pectus Excavatum/Carinatum, Marfan’s and Poland’s Syndromes",
"Chylothorax",
"Congenital Diaphragmatic Hernia",
"Cystic Diseases of the Lung",
"Cystic Fibrosis",
"Cystic Pulmonary Airway Malformation",
"Empyema",
"Esophageal Atresia and Tracheoesophageal Fistula",
"Esophageal Perforation",
"Esophageal Replacement",
"Esophageal Stenosis, Webs, Diverticuli",
"Esophageal Stricture: Caustic Ingestion and Other Causes",
"Esophagoscopy",
"Eventration of the Diaphragm",
"Gastroesophageal Reflux/Barrett's Esophagus",
"Laryngomalacia",
"Lobar Emphysema",
"Mediastinal Cysts, Masses",
"Patent Ductus Arteriosus",
"Pneumothorax",
"Prenatal Anomalies and Therapy",
"Pulmonary Abscess",
"Pulmonary Hypoplasia/Hypertension",
"Pulmonary Sequestration",
"Subacute Bacterial Endocarditis Prophylaxis",
"Tracheobronchial Foreign Bodies",
"Tracheomalacia",
"Vascular Ring and Pulmonary Artery Sling",
"Abdominal Pain",
"Alimentary Tract Duplications",
"Appendicitis",
"Ascites: Chylous",
"Biliary Atresia",
"Choledochal Cysts",
"Cloacal Exstrophy/Bladder Exstrophy",
"Duodenal Atresia/Stenosis/Webs/Annular Pancreas",
"Gallbladder Disease, Gallstones",
"Gastric Volvulus",
"Gastrointestinal Bleeding",
"Gastroschisis",
"Hepatic Infections: Hepatitis, Abscess, Cysts",
"Hirschsprung Disease",
"Hypertrophic Pyloric Stenosis",
"Inflammatory Bowel Disease",
"Inguinal Hernia",
"Intestinal Atresia",
"Intussusception",
"Malrotation",
"Meconium Ileus/Peritonitis/Plug",
"Mesenteric and Omental Cysts",
"Necrotizing Enterocolitis",
"Neonatal Gastric Perforation",
"Neonatal Obstruction",
"Omphalocele",
"Omphalomesenteric Duct Remnants, Urachus, and Meckel's",
"Peptic Ulcer Disease",
"Polyps",
"Portal Hypertension",
"Umbilical Hernia and Other Umbilical Disorders",
"Adrenal Cortical Tumors, Pheochromocytoma",
"Anal Pathology: Fissures, Abscesses, Fistulae, Pilonidal, Prolapse",
"Anorectal Malformation",
"Arterial Diseases and Vasculitis",
"Branchial Cleft, Arch Anomalies",
"Breast Disorders",
"Circumcision and Abnormalities of the Urethra, Penis, Scrotum",
"Disorders of Sexual Development",
"Endocrine Diseases",
"Lymphadenopathy, Atypical Mycobacteria",
"Neurological: Shunt Complications, Dermal Sinuses",
"Ovarian Torsion, Cysts, and Tumors",
"Renal Diseases: Nephrotic Syndrome, DI, Renal Vein Thrombosis,\nChronic Failure, Prune Belly Syndrome",
"Thyroglossal Duct Cyst/Sinus",
"Thyroid Nodules",
"Torsions: Appendix Testes, Testicular",
"Torticollis",
"Undescended Testicle (Cryptorchidism)",
"Vaginal Atresia, Hydrometrocolpos",
"Vascular Anomalies",
"Abdominal Trauma",
"Acute Renal Failure",
"ARDS",
"Burns: Resuscitation, Airway, Electrical, Nutrition, Wound, Sepsis",
"Cardiovascular Trauma: Tamponade, Contusion, Arch Disruption, Peripheral Vascular\nInjuries",
"Coagulation",
"Extracorporeal Life Support",
"Fluids and Electrolytes",
"Hematologic Diseases: Spherocytosis, Sickle Cell, ITP, HSP",
"Lung Physiology, Pathophysiology, Ventilators, Pneumonia",
"Musculoskeletal Trauma: Pelvis, Long Bone",
"Neonatal Physiology and Pathophysiology: Transition from Fetal Circulation,\nCardiovascular Monitoring, Shock",
"Neurosurgical Trauma",
"Nonaccidental Injuries: Diagnosis, Evaluation, Legal Issues",
"Nutrition",
"Obesity",
"Pediatric Anesthesia and Pain Management",
"Short Bowel Syndrome/Intestinal Failure",
"Soft Tissue Trauma: Tetanus, Bites, Wound Infection, Crush Injuries",
"Thoracic Trauma",
"Transplantation",
"Trauma: Initial Assessment and Resuscitation",
"Abdominal Mass in the Newborn",
"Adrenal Cancer",
"Benign Liver Tumors: Hepatic Mesenchymal Hamartoma/Adenoma/FNH",
"Bone Tumors: Osteogenic Sarcoma, Ewing Sarcoma",
"Chemo/Radiation Therapy, Immunotherapy Concepts, Genetics",
"Dermoid/Epidermoid Cysts, Soft Tissue Nodules",
"Gastrointestinal Tumors",
"Lung and Chest Wall Tumors",
"Lymphoma/Leukemia",
"Malignant Liver Tumors: Hepatoblastoma/Hepatocellular Carcinoma",
"Mesoblastic Nephroma",
"Neuroblastoma",
"Nevi, Melanoma",
"Ovarian and Adrexal Problems",
"Rhabdomyosarcoma",
"Splenic Diseases",
"Teratoma",
"Testicular Tumors",
"Wilms Tumor, Renal Cell Carcinoma, and Hemihypertrophy"
]

# =========================
# PAGE & THEME
# =========================
st.set_page_config(page_title="Question Bank", page_icon="🧠", layout="wide")
CUSTOM_CSS = """
<style>
.block-container {padding-top: 2rem; padding-bottom: 3rem;}
h1.title {font-weight: 800; letter-spacing:-0.02em;}
.card {
  background: #ffffff; border-radius: 18px;
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
  border-radius: 12px !important; padding: .6rem 1rem !important; font-weight: 600 !important;
  border: 1px solid rgba(17,24,39,.06) !important; box-shadow: 0 1px 6px rgba(2,6,23,.05) !important;
}
.stRadio [role='radiogroup'] label {padding:.35rem .55rem; border-radius:10px;}
.stRadio [role='radiogroup'] label:hover {background:#f3f4f6;}
[data-testid="stProgressBar"] + div p {font-weight:600;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

REQUIRED = ["Question","A","B","C","D","E","Correct","Explanation","Reference","Category","Difficulty"]
PROGRESS_FILE = "progress.json"
DATA_DIR = "data"

# =========================
# HELPERS
# =========================
def _normalize_cat(s: str) -> str:
    return (
        str(s).replace("’", "'")
              .replace("–", "-")
              .replace("\u00A0", " ")
              .strip()
    )

@st.cache_data(show_spinner=False)
def list_data_files(data_dir: str) -> List[str]:
    if not os.path.isdir(data_dir):
        return []
    names = []
    for f in os.listdir(data_dir):
        if f.startswith("."): 
            continue
        if f.lower().endswith((".csv", ".xlsx", ".xls")):
            names.append(f)
    return sorted(names)

@st.cache_data(show_spinner=False)
def load_one(path: str) -> pd.DataFrame:
    p = os.path.join(DATA_DIR, path)
    if path.lower().endswith((".xlsx",".xls")):
        df = pd.read_excel(p)
    else:
        df = pd.read_csv(p)
    # validate/clean
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"{path}: missing columns {missing}")
    df["Correct"] = df["Correct"].astype(str).str.strip().str.upper()
    for c in ["Question","A","B","C","D","E","Explanation","Reference","Category","Difficulty"]:
        df[c] = df[c].astype(str).fillna("").str.strip()
    df["Category"] = df["Category"].apply(_normalize_cat)
    df["__sourcefile__"] = path
    return df

@st.cache_data(show_spinner=False)
def load_many(selected_files: List[str]) -> pd.DataFrame:
    frames = [load_one(f) for f in selected_files]
    if not frames:
        return pd.DataFrame(columns=REQUIRED)
    return pd.concat(frames, axis=0, ignore_index=True)

def init_state():
    ss = st.session_state
    ss.setdefault("df", None)
    ss.setdefault("indices", [])
    ss.setdefault("i", 0)
    ss.setdefault("answers", {})
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

# =========================
# SIDEBAR (no upload)
# =========================
init_state()
st.sidebar.title("📚 Repository Controls")

files = list_data_files(DATA_DIR)
if not files:
    st.sidebar.error("No files found in the 'data/' folder.\nAdd CSV/XLSX files with the required headers.")
    st.stop()

st.sidebar.caption("These sets live in your repo → data/")
combine_all = st.sidebar.toggle("Use ALL question sets", value=True)
if combine_all:
    selected_files = files
else:
    selected_files = st.sidebar.multiselect("Choose sets", files, default=files[:1])

# Load/refresh button
if st.sidebar.button("Load Repository Questions", type="primary", use_container_width=True):
    st.session_state.df = load_many(selected_files)
    if not st.session_state.df.empty:
        # Warn about non-standard categories
        unknown = sorted(set(st.session_state.df["Category"].dropna()) - set(CATEGORIES_MASTER))
        if unknown:
            st.warning(f"Unrecognized categories in repository data (check spelling/casing): {unknown}")
        rebuild_indices(); persist_progress()

# auto-load first time
if st.session_state.df is None:
    st.session_state.df = load_many(selected_files)
    if not st.session_state.df.empty and not st.session_state.indices:
        unknown = sorted(set(st.session_state.df["Category"].dropna()) - set(CATEGORIES_MASTER))
        if unknown:
            st.warning(f"Unrecognized categories in repository data (check spelling/casing): {unknown}")
        load_progress(); rebuild_indices()

if st.session_state.df is not None and not st.session_state.df.empty:
    df = st.session_state.df

    # Build filters (categories in MASTER order, but only those present in the current selection)
    present = set(df["Category"].dropna().unique().tolist())
    cats = [c for c in CATEGORIES_MASTER if c in present]
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

    # Export (still allowed—exports user results only)
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
                        "__SourceFile__": sub.loc[idx, "__sourcefile__"] if "__sourcefile__" in sub.columns else ""
                    })
            if rows:
                out = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
                st.sidebar.download_button("Download results.csv", out, "results.csv", "text/csv", use_container_width=True)
        else:
            st.sidebar.info("No answers to export yet.")

# =========================
# MAIN UI
# =========================
st.markdown("<h1 class='title'>🧠 Question Bank (Repository)</h1>", unsafe_allow_html=True)
st.caption("Read-only repository from your GitHub `data/` folder • Official categories • Filters • Progress • Flags/Favorites")

if st.session_state.df is None or st.session_state.df.empty:
    st.info("No questions loaded. Add files to `data/` and click **Load Repository Questions**.")
    st.stop()

df = st.session_state.df
sub = apply_filters(df)
if len(sub) == 0:
    st.warning("No questions match the current filters.")
    st.stop()

st.session_state.i = int(np.clip(st.session_state.i, 0, len(st.session_state.indices)-1))
local_idx = st.session_state.indices[st.session_state.i]
q = sub.loc[local_idx]

# Progress
answered = len(st.session_state.answers); total = len(st.session_state.indices)
pct = int((answered/total)*100) if total else 0
st.progress(min(pct/100, 1.0), text=f"Progress: {answered}/{total} answered • {pct}%")

# Chips
chips = []
if q["Category"]: chips.append(f"<span class='chip'>Category: {q['Category']}</span>")
if q["Difficulty"]: chips.append(f"<span class='chip'>Difficulty: {q['Difficulty']}</span>")
if "__sourcefile__" in q and q["__sourcefile__"]: chips.append(f"<span class='chip'>Set: {q['__sourcefile__']}</span>")
st.markdown(" ".join(chips), unsafe_allow_html=True)

# Question card
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown(f"### Q{st.session_state.i+1}")
st.markdown(f"**{q['Question']}**")

choices = {"A": q["A"], "B": q["B"], "C": q["C"], "D": q["D"], "E": q["E"]}

# Flag/Favorite
c_top = st.columns([1,1,6])
flagged = local_idx in st.session_state.flags
faved = local_idx in st.session_state.favs
if c_top[0].button(("🚩 Unflag" if flagged else "🚩 Flag"), use_container_width=True):
    if flagged: st.session_state.flags.remove(local_idx)
    else: st.session_state.flags.add(local_idx); persist_progress()
if c_top[1].button(("⭐ Unfavorite" if faved else "⭐ Favorite"), use_container_width=True):
    if faved: st.session_state.favs.remove(local_idx)
    else: st.session_state.favs.add(local_idx); persist_progress()

# Answer input
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

# Explanation
if st.session_state.show_expl or st.session_state.review_mode:
    st.markdown("<div class='card card-dim'>", unsafe_allow_html=True)
    st.markdown("**Explanation**")
    st.write(q["Explanation"])
    if str(q["Reference"]).lower().startswith(("http://","https://")):
        st.markdown(f"[Reference]({q['Reference']})")
    st.markdown("</div>", unsafe_allow_html=True)

# Navigation
nav = st.columns([1,1,6])
if nav[0].button("⬅️ Previous", disabled=st.session_state.i==0, use_container_width=True):
    st.session_state.i = max(0, st.session_state.i-1); st.session_state.show_expl=False
if nav[1].button("Next ➡️", disabled=st.session_state.i>=len(st.session_state.indices)-1, use_container_width=True):
    st.session_state.i = min(len(st.session_state.indices)-1, st.session_state.i+1); st.session_state.show_expl=False

st.markdown("</div>", unsafe_allow_html=True)

# Performance view
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

st.caption("Read-only repository mode • Add/update question sets in data/ and reload here.")
