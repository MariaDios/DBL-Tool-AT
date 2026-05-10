"""
DBL Tool AT — Digital Building Logbook Evaluation Tool for Austria
Master's Thesis — Maria Dioszegi, UAS Technikum Wien 2026
Run: python -m streamlit run dbl_tool_final.py
Requirements: pip install streamlit plotly pandas
"""

import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="DBL Tool AT", page_icon=None, layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
  html, body, [class*="css"] { font-family: 'Segoe UI', Arial, sans-serif; font-size: 16px !important; }
  .block-container { padding-top: 1.5rem; }
  p, li, label { color: #111111 !important; font-size: 15px !important; }
  .stDataFrame { font-size: 14px !important; }
  .stExpander label { font-size: 15px !important; font-weight: 600 !important; color: #111111 !important; }
  .stTextInput input { font-size: 15px !important; color: #111111 !important; }
  .crit-label { font-size: 16px !important; font-weight: 600 !important; color: #111111 !important; margin: 10px 0 4px 0; }
  .dim-header { font-size: 1.15rem !important; font-weight: 700 !important; color: #1a3a2a !important;
                background: #f0f8f3; border-left: 4px solid #2d5a40; padding: 0.5rem 1rem;
                border-radius: 0 6px 6px 0; margin: 1.2rem 0 0.6rem 0; }
  .kpi-row { display: flex; gap: 12px; margin-bottom: 1.5rem; flex-wrap: wrap; }
  .kpi { background: #f8faf9; border: 1px solid #d8eed8; border-left: 4px solid #2d5a40;
         border-radius: 10px; padding: 0.9rem 1.2rem; flex: 1; min-width: 140px; }
  .kpi .label { font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em; color: #222222; font-weight: 700; }
  .kpi .value { font-size: 2.1rem; font-weight: 800; color: #111111; }
  .kpi .sub   { font-size: 0.82rem; color: #555555; margin-top: 3px; }
  .sec-title { font-size: 1.3rem; font-weight: 700; color: #111111; border-bottom: 2px solid #2d5a40;
               padding-bottom: 0.3rem; margin-bottom: 1rem; }
  .dim-desc { font-size: 13px; color: #444444; font-style: italic; margin-bottom: 0.8rem; }
  #MainMenu { visibility: hidden; } footer { visibility: hidden; }
  .stDataFrame td, .stDataFrame th { color: #000000 !important; font-size: 14px !important; }
  [data-testid="stDataFrame"] * { color: #000000 !important; }
</style>
""", unsafe_allow_html=True)

DIMENSIONS = {
    "Data Categories & Content Scope": ["Energy Performance Data","Technical Documentation","Renovation History"],
    "Circularity-related Information":  ["Material Passport","Waste & CDW Support","Urban Mining Potential"],
    "Governance Model":                 ["Legal Mandate","Governance Clarity","Privacy & Data Rights"],
    "Interoperability":                 ["BIM Integration","Open API / Data Exchange","Cross-system Alignment"],
    "Usability":                        ["Owner Access","Professional Access","Ease of Use"],
    "Lifecycle Coverage":               ["Construction & Design Phase","Operation & Renovation Phase","End-of-Life Phase"],
}

ALL_CRITERIA = [c for cl in DIMENSIONS.values() for c in cl]

DEFAULT_SCORES = {
    "Belgium — Woningpas": {
        "color":"#87B40F","system":"Woningpas","status":"Fully operational — voluntary",
        "building_type":"Residential","website":"https://woningpas.vlaanderen.be/",
        "scores":{"Energy Performance Data":1,"Technical Documentation":2,"Renovation History":1,"Material Passport":4,"Waste & CDW Support":4,"Urban Mining Potential":5,"Legal Mandate":3,"Governance Clarity":1,"Privacy & Data Rights":2,"BIM Integration":4,"Open API / Data Exchange":2,"Cross-system Alignment":2,"Owner Access":1,"Professional Access":2,"Ease of Use":1,"Construction & Design Phase":3,"Operation & Renovation Phase":2,"End-of-Life Phase":5},
    },
    "France — CIL": {
        "color":"#005A96","system":"Carnet d'Information du Logement","status":"Mandatory since January 2023",
        "building_type":"Residential","website":"https://www.service-public.gouv.fr/particuliers/vosdroits/F36759?lang=en",
        "scores":{"Energy Performance Data":1,"Technical Documentation":2,"Renovation History":1,"Material Passport":4,"Waste & CDW Support":4,"Urban Mining Potential":5,"Legal Mandate":1,"Governance Clarity":2,"Privacy & Data Rights":2,"BIM Integration":4,"Open API / Data Exchange":4,"Cross-system Alignment":3,"Owner Access":1,"Professional Access":2,"Ease of Use":2,"Construction & Design Phase":3,"Operation & Renovation Phase":1,"End-of-Life Phase":5},
    },
    "Germany — iSFP": {
        "color":"#696969","system":"individueller Sanierungsfahrplan","status":"Fully operational — voluntary",
        "building_type":"Residential","website":"https://www.kfw.de/inlandsfoerderung/Privatpersonen/Bestehende-Immobilie/Energieeffizient-sanieren/Individueller-Sanierungsfahrplan/",
        "scores":{"Energy Performance Data":1,"Technical Documentation":3,"Renovation History":2,"Material Passport":4,"Waste & CDW Support":4,"Urban Mining Potential":5,"Legal Mandate":4,"Governance Clarity":2,"Privacy & Data Rights":2,"BIM Integration":5,"Open API / Data Exchange":5,"Cross-system Alignment":4,"Owner Access":1,"Professional Access":2,"Ease of Use":2,"Construction & Design Phase":5,"Operation & Renovation Phase":1,"End-of-Life Phase":5},
    },
    "Netherlands — Madaster": {
        "color":"#E87744","system":"Madaster Platform","status":"Fully operational — voluntary (commercial)",
        "building_type":"All building types","website":"https://madaster.com/",
        "scores":{"Energy Performance Data":4,"Technical Documentation":2,"Renovation History":3,"Material Passport":1,"Waste & CDW Support":1,"Urban Mining Potential":1,"Legal Mandate":5,"Governance Clarity":3,"Privacy & Data Rights":2,"BIM Integration":1,"Open API / Data Exchange":1,"Cross-system Alignment":2,"Owner Access":3,"Professional Access":1,"Ease of Use":3,"Construction & Design Phase":1,"Operation & Renovation Phase":2,"End-of-Life Phase":1},
    },
    "EU — iBRoad": {
        "color":"#C8860A","system":"Individual Building Renovation Roadmap + Logbook","status":"Completed H2020 — tools published, piloted in 4 countries",
        "building_type":"Residential","website":"https://ibroad-project.eu/",
        "scores":{"Energy Performance Data":1,"Technical Documentation":3,"Renovation History":1,"Material Passport":5,"Waste & CDW Support":5,"Urban Mining Potential":5,"Legal Mandate":4,"Governance Clarity":3,"Privacy & Data Rights":3,"BIM Integration":4,"Open API / Data Exchange":4,"Cross-system Alignment":3,"Owner Access":1,"Professional Access":2,"Ease of Use":2,"Construction & Design Phase":5,"Operation & Renovation Phase":1,"End-of-Life Phase":5},
    },
    "EU — openDBL": {
        "color":"#7B3FA0","system":"Open Digital Building Logbook Platform","status":"Ongoing Horizon Europe — pilots in Italy, Spain, Greece",
        "building_type":"All building types","website":"https://www.opendbl.eu/",
        "scores":{"Energy Performance Data":2,"Technical Documentation":1,"Renovation History":2,"Material Passport":3,"Waste & CDW Support":3,"Urban Mining Potential":3,"Legal Mandate":5,"Governance Clarity":3,"Privacy & Data Rights":2,"BIM Integration":1,"Open API / Data Exchange":1,"Cross-system Alignment":2,"Owner Access":3,"Professional Access":2,"Ease of Use":3,"Construction & Design Phase":2,"Operation & Renovation Phase":1,"End-of-Life Phase":3},
    },
}

# Session state
if "criterion_notes" not in st.session_state:
    st.session_state.criterion_notes = {}
if "edit_notes" not in st.session_state:
    st.session_state.edit_notes = {k: {c: "" for c in ALL_CRITERIA} for k in DEFAULT_SCORES}
if "scores" not in st.session_state:
    st.session_state.scores = {k: dict(v["scores"]) for k,v in DEFAULT_SCORES.items()}
if "edit_buffer" not in st.session_state:
    st.session_state.edit_buffer = {k: dict(v["scores"]) for k,v in DEFAULT_SCORES.items()}
if "profiles" not in st.session_state:
    st.session_state.profiles = {
        k: {"system": v["system"], "building_type": v["building_type"], "status": v["status"], "website": v["website"]}
        for k,v in DEFAULT_SCORES.items()
    }

def get_score(s,c): return st.session_state.scores[s].get(c, DEFAULT_SCORES[s]["scores"][c])
def dim_avg(s,d): crits=DIMENSIONS[d]; return round(sum(get_score(s,c) for c in crits)/len(crits),1)
def overall(s): return round(sum(get_score(s,c) for c in ALL_CRITERIA)/len(ALL_CRITERIA),1)
# 1 = best, 5 = worst → top performer has LOWEST score
def top_performer(sel): return min(sel, key=overall)
def best_for_crit(c, sel): return min(sel, key=lambda k: get_score(k,c))

# Sidebar
with st.sidebar:
    st.markdown("### DBL Tool AT")
    st.markdown('<p style="color:#555555;font-size:12px">Maria Dioszegi · UAS Technikum Wien 2026</p>', unsafe_allow_html=True)
    st.divider()
    st.markdown("**Select systems**")
    selected = [k for k in DEFAULT_SCORES if st.checkbox(k, value=True, key=f"sel_{k}")]
    if not selected:
        selected = list(DEFAULT_SCORES.keys())[:1]

# Header
st.markdown("""
<div style="background:linear-gradient(135deg,#1a3a2a 0%,#2d5a40 100%);border-radius:14px;padding:2rem 2.5rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:2rem">
  <div style="flex-shrink:0">
    <svg width="68" height="68" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="72" height="72" rx="14" fill="rgba(255,255,255,0.12)"/>
      <rect x="14" y="30" width="44" height="30" rx="3" fill="none" stroke="white" stroke-width="2.5"/>
      <polyline points="10,32 36,14 62,32" fill="none" stroke="white" stroke-width="2.5" stroke-linejoin="round"/>
      <rect x="28" y="42" width="8" height="10" rx="1.5" fill="white" opacity="0.9"/>
      <rect x="40" y="38" width="10" height="7" rx="1.5" fill="none" stroke="white" stroke-width="2" opacity="0.9"/>
      <line x1="22" y1="38" x2="22" y2="45" stroke="white" stroke-width="2" opacity="0.6"/>
      <line x1="19" y1="41" x2="25" y2="41" stroke="white" stroke-width="2" opacity="0.6"/>
    </svg>
  </div>
  <div>
    <div style="color:#FFFFFF;font-size:1.85rem;font-weight:800;line-height:1.25;font-family:Segoe UI,Arial,sans-serif">DBL Tool AT &mdash; Digital Building Logbook Evaluation Tool for Austria</div>
  </div>
</div>
""", unsafe_allow_html=True)

# KPI row — top performer = lowest score (1=best), worst = highest score
top = top_performer(selected)
worst = max(selected, key=overall)
st.markdown(f"""
<div class="kpi-row">
  <div class="kpi"><div class="label">Systems selected</div><div class="value">{len(selected)}</div><div class="sub">of 6 total</div></div>
  <div class="kpi"><div class="label">Dimensions</div><div class="value">6</div><div class="sub">18 criteria total</div></div>
  <div class="kpi" style="border-left-color:#2d5a40"><div class="label">Top performer</div><div class="value" style="color:#2d5a40">{overall(top)}</div><div class="sub">{top} &nbsp;·&nbsp; lowest score = strongest</div></div>
  <div class="kpi" style="border-left-color:#b03030"><div class="label">Worst performer</div><div class="value" style="color:#b03030">{overall(worst)}</div><div class="sub">{worst} &nbsp;·&nbsp; highest score = most gaps</div></div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["System Profiles", "Edit Scores", "Comparison Table", "Recommendations for Austria"])

# ── Tab 0: System Profiles ────────────────────────────────────────────────────
with tabs[0]:
    st.markdown('<div class="sec-title">System Profiles</div>', unsafe_allow_html=True)
    st.markdown('<p class="dim-desc">Click a system to expand. Score of 1 = criterion fully met, 5 = absent. Lower overall score = stronger system.</p>', unsafe_allow_html=True)

    cols = st.columns(2)
    for i, key in enumerate(selected):
        ov = overall(key)
        with cols[i % 2]:
            with st.expander(f"{key}  |  Overall score: {ov} / 5.0", expanded=False):
                p = st.session_state.profiles[key]
                p["system"]        = st.text_input("System name",   value=p["system"],        key=f"p_sys_{key}")
                p["building_type"] = st.text_input("Building type",  value=p["building_type"], key=f"p_bt_{key}")
                p["status"]        = st.text_input("Status",         value=p["status"],        key=f"p_st_{key}")
                website_val = p.get("website", DEFAULT_SCORES[key]["website"])
                edit_key = f"edit_web_{key}"
                if edit_key not in st.session_state:
                    st.session_state[edit_key] = False
                col_link, col_btn = st.columns([5,1])
                with col_link:
                    st.markdown(f'<a href="{website_val}" target="_blank" style="display:block;background:#f0f2f6;border:1px solid #ddd;border-radius:6px;padding:9px 12px;color:#005A96;font-size:0.88rem;word-break:break-all;">{website_val}</a>', unsafe_allow_html=True)
                with col_btn:
                    if st.button("Edit", key=f"btn_web_{key}"):
                        st.session_state[edit_key] = not st.session_state[edit_key]
                if st.session_state[edit_key]:
                    new_url = st.text_input("Edit URL", value=website_val, key=f"p_web_{key}")
                    p["website"] = new_url
                else:
                    p["website"] = website_val

    st.markdown('<div class="sec-title" style="margin-top:1.5rem">Overall Scores</div>', unsafe_allow_html=True)
    st.markdown('<p class="dim-desc">Arithmetic mean across all 18 criteria. Lower score = stronger implementation. Score of 1 = criterion fully met, 5 = absent.</p>', unsafe_allow_html=True)
    names  = list(selected)
    ovs    = [overall(k) for k in selected]
    colors = [DEFAULT_SCORES[k]["color"] for k in selected]
    fig = px.bar(x=names, y=ovs, color=names, color_discrete_sequence=colors,
                 text=[f"{s:.1f}" for s in ovs], labels={"x":"","y":"Average Score (1–5)"})
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, yaxis=dict(range=[0,5.8], gridcolor="#e8f0eb"),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      height=320, margin=dict(l=20,r=20,t=10,b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="sec-title">Dimension Averages</div>', unsafe_allow_html=True)
    st.markdown('<p class="dim-desc">Average score per dimension. Each dimension groups three equally weighted criteria. Lower score = stronger implementation. Dark green = score closer to 1 (strong), light = closer to 5 (weak or absent).</p>', unsafe_allow_html=True)
    dim_rows = [{"Dimension": dim, **{k: dim_avg(k, dim) for k in selected}} for dim in DIMENSIONS]
    df_dim = pd.DataFrame(dim_rows).set_index("Dimension")
    st.dataframe(df_dim.style.background_gradient(cmap="Greens_r", vmin=1, vmax=5).format("{:.1f}"), use_container_width=True)

# ── Tab 1: Edit Scores ────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown('<div class="sec-title">Edit Scores</div>', unsafe_allow_html=True)
    st.markdown('<p class="dim-desc">Expand a system, adjust scores and add notes. Click <b>Save all scores</b> when finished. The page does not update until you save.</p>', unsafe_allow_html=True)

    with st.form("edit_scores_form"):
        for key in selected:
            with st.expander(f"{key}  |  Current overall: {overall(key)} / 5.0", expanded=False):
                for dim, crits in DIMENSIONS.items():
                    st.markdown(f'<div class="dim-header">{dim}</div>', unsafe_allow_html=True)
                    for c in crits:
                        c1, c2, c3 = st.columns([2, 2, 3])
                        with c1:
                            st.markdown(f'<p class="crit-label">{c}</p>', unsafe_allow_html=True)
                        with c2:
                            current = st.session_state.edit_buffer[key].get(c, DEFAULT_SCORES[key]["scores"][c])
                            nv = st.slider(c, 1, 5, value=current, key=f"buf_{key}_{c}", label_visibility="collapsed")
                            st.session_state.edit_buffer[key][c] = nv
                        with c3:
                            note_val = st.session_state.edit_notes[key].get(c, "")
                            nt = st.text_input(f"note_{key}_{c}", value=note_val,
                                               placeholder="Add justification note...",
                                               key=f"enote_{key}_{c}",
                                               label_visibility="collapsed")
                            st.session_state.edit_notes[key][c] = nt

        col_save, col_reset = st.columns([2,1])
        with col_save:
            submitted = st.form_submit_button("Save all scores", use_container_width=True, type="primary")
        with col_reset:
            reset = st.form_submit_button("Reset to defaults", use_container_width=True)

    if submitted:
        for key in selected:
            for c in ALL_CRITERIA:
                st.session_state.scores[key][c] = st.session_state.edit_buffer[key][c]
        st.success("Scores saved successfully.")
    if reset:
        st.session_state.scores = {k: dict(v["scores"]) for k,v in DEFAULT_SCORES.items()}
        st.session_state.edit_buffer = {k: dict(v["scores"]) for k,v in DEFAULT_SCORES.items()}
        st.session_state.edit_notes = {k: {c: "" for c in ALL_CRITERIA} for k in DEFAULT_SCORES}
        st.success("Reset to source-based defaults.")

# ── Tab 2: Comparison Table ───────────────────────────────────────────────────
with tabs[2]:
    st.markdown('<div class="sec-title">Criterion-level Comparison</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#111111;font-size:13px"><b>Green</b> = 1–2 (strong) &nbsp;|&nbsp; <b>Orange</b> = 3 (moderate) &nbsp;|&nbsp; <b>Red</b> = 4–5 (weak or absent)</p>', unsafe_allow_html=True)
    rows = []
    for dim, crits in DIMENSIONS.items():
        for c in crits:
            row = {"Dimension": dim, "Criterion": c}
            for k in selected:
                row[k] = get_score(k, c)
            rows.append(row)
    df = pd.DataFrame(rows)
    ccols = list(selected)
    def cc(val):
        if val <= 2: return "background-color:#d4edda;color:#1a5c2a;font-weight:600"
        elif val == 3: return "background-color:#FFD6A0;color:#7A3B00"
        else: return "background-color:#f8d7da;color:#7a1c24"
    st.dataframe(df.style.map(cc, subset=ccols), use_container_width=True, height=750)

# ── Tab 3: Recommendations ────────────────────────────────────────────────────
with tabs[3]:
    st.markdown('<div class="sec-title">Minimum Requirements for Austria</div>', unsafe_allow_html=True)
    st.markdown('<p class="dim-desc">Each requirement is derived from the best-scoring (lowest score = strongest) approach identified across the six systems. Click a criterion to expand and add notes. To save as PDF: Ctrl+P → Save as PDF.</p>', unsafe_allow_html=True)

    CRITERIA_DATA = {
        "Energy Performance Data":      {"adopt":"EPC data integration","why":"Records energy consumption, heating systems, insulation materials, and EPC ratings. Documented in CIL (France) as mandatory content and in iBRoad as the core of the renovation roadmap (CINEA, n.d.; French Government, n.d.)."},
        "Technical Documentation":      {"adopt":"BIM-based technical documentation","why":"Building plans, 3D models, and technical specifications stored digitally. Implemented in openDBL through BIM upload and 3D scanning as primary data input (openDBL.eu, 2024)."},
        "Renovation History":           {"adopt":"Mandatory renovation records","why":"Chronological record of all renovation works — insulation, windows, heating upgrades. Required by CIL (France) to be transferred to the buyer at point of sale (French Government, n.d.)."},
        "Material Passport":            {"adopt":"Material passport","why":"Registration and tracking of all building materials and components across the full lifecycle. Implemented by Madaster with component-level documentation and residual value calculation (Madaster, 2026)."},
        "Waste & CDW Support":          {"adopt":"CDW tracking and circularity reporting","why":"Tracking of materials to support construction and demolition waste management. Provided by Madaster through EU Taxonomy compliance and embodied carbon calculation (Madaster, 2026)."},
        "Urban Mining Potential":       {"adopt":"Urban mining data","why":"Calculation of residual material value and recycling potential at building and city scale. Uniquely implemented by Madaster — no other reviewed system provides this functionality (Madaster, 2026)."},
        "Legal Mandate":                {"adopt":"National legal mandate","why":"Legally binding obligation to create and maintain a building information file. Established in France through Loi Climat et Resilience (2021), Art. 167 — the only mandatory national DBL instrument in Europe (French Government, n.d.)."},
        "Governance Clarity":           {"adopt":"Single responsible authority","why":"Single public authority responsible for ownership and maintenance of the DBL. Implemented by the Flemish Government (VEKA) as the sole managing body of Woningpas (Interoperable Europe Portal, 2019)."},
        "Privacy & Data Rights":        {"adopt":"Owner-controlled data access","why":"Building owners control who can access and share their logbook data. Designed in Woningpas as a shareable digital file — owners grant access to professionals or prospective buyers (Interoperable Europe Portal, 2019)."},
        "BIM Integration":              {"adopt":"BIM file integration","why":"Upload of BIM models as primary data input using open IFC standards. Implemented by Madaster and openDBL — reduces manual data entry and enables 3D building data management (Madaster, 2026; openDBL.eu, 2024)."},
        "Open API / Data Exchange":     {"adopt":"Open API to national registries","why":"Open interfaces for data exchange with national and EU registries. Developed by openDBL as its primary technical objective (openDBL.eu, 2024)."},
        "Cross-system Alignment":       {"adopt":"EU Semantic Data Model alignment","why":"Data structure aligned with EPBD requirements and EU frameworks. Defined in the EU Technical Study (2023) Linked Data architecture (Ecorys et al., 2023)."},
        "Owner Access":                 {"adopt":"Simple owner interface","why":"Simple digital file accessible and shareable by building owners without technical expertise. Implemented in Woningpas and CIL (Interoperable Europe Portal, 2019)."},
        "Professional Access":          {"adopt":"Full professional dashboard","why":"Full analytical access for architects, energy auditors, facility managers, and municipalities. Provided by Madaster through detailed professional dashboards (Madaster, 2026)."},
        "Ease of Use":                  {"adopt":"Guided non-expert data entry","why":"Guided data entry accessible to non-expert users with pre-populated fields. Designed in Woningpas through automatic aggregation of publicly available data (Interoperable Europe Portal, 2019)."},
        "Construction & Design Phase":  {"adopt":"Documentation from building permit","why":"Documentation starting at permit stage through BIM upload or design drawings. Implemented by Madaster and openDBL (Madaster, 2026; openDBL.eu, 2024)."},
        "Operation & Renovation Phase": {"adopt":"Renovation linked to subsidies","why":"Step-by-step renovation documentation linked to public funding schemes. Implemented by iSFP linked to KfW subsidies and by iBRoad as a long-term renovation roadmap (KfW, 2026; CINEA, n.d.)."},
        "End-of-Life Phase":            {"adopt":"End-of-life material data","why":"Material recovery, demolition planning, and residual material value at building end of life. Uniquely implemented by Madaster as the only reviewed system covering the full lifecycle (Madaster, 2026)."},
    }

    for dim, crits in DIMENSIONS.items():
        st.markdown(f'<div class="dim-header">{dim}</div>', unsafe_allow_html=True)
        for c in crits:
            bs_c = best_for_crit(c, selected)
            sc_c = get_score(bs_c, c)
            data = CRITERIA_DATA.get(c, {"adopt":"—","why":"—"})
            with st.expander(f"{c} — Adopt: {data['adopt']}"):
                st.markdown(f'<p class="crit-label">Best practice: {bs_c} — score {sc_c} / 5.0</p>', unsafe_allow_html=True)
                st.markdown(f"_{data['why']}_")
                note_key = f"note_crit_{c}"
                st.session_state.criterion_notes[note_key] = st.text_area(
                    "Note",
                    value=st.session_state.criterion_notes.get(note_key, ""),
                    key=f"ta_{note_key}",
                    placeholder="Add your note here...",
                    height=80,
                    label_visibility="collapsed"
                )
