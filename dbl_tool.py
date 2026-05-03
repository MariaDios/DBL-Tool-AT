"""
DBL Tool AT — Digital Building Logbook Evaluation Tool for Austria
Master's Thesis — Maria Dioszegi, UAS Technikum Wien 2026
Run: python -m streamlit run dbl_tool_final.py
Requirements: pip install streamlit plotly pandas matplotlib
"""

import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="DBL Tool AT", page_icon="🏛️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
  html, body, [class*="css"] { font-family: 'Segoe UI', Arial, sans-serif; font-size: 16px !important; }
  .block-container { padding-top: 1.5rem; }
  p, li, label { color: #111111 !important; font-size: 15px !important; }
  .stDataFrame { font-size: 14px !important; }
  .stExpander label { font-size: 15px !important; font-weight: 600 !important; color: #111111 !important; }
  .stTextInput input { font-size: 15px !important; color: #111111 !important; }
  .stCaption { color: #333333 !important; font-size: 13px !important; }
  .hero {
    background: linear-gradient(135deg, #1a3a2a 0%, #2d5a40 100%);
    border-radius: 14px; padding: 2rem 2.5rem; margin-bottom: 1.5rem; color: white;
  }
  .hero h1 { color: white !important; font-size: 2rem; margin-bottom: 0.2rem; }
  .hero p  { color: #FFFFFF; font-size: 0.95rem; margin: 0; }
  .kpi-row { display: flex; gap: 12px; margin-bottom: 1.5rem; flex-wrap: wrap; }
  .kpi { background: #f8faf9; border: 1px solid #d8eed8; border-left: 4px solid #2d5a40;
         border-radius: 10px; padding: 0.9rem 1.2rem; flex: 1; min-width: 140px; }
  .kpi .label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: #222222; font-weight: 700; }
  .kpi .value { font-size: 1.7rem; font-weight: 700; color: #111111; }
  .kpi .sub   { font-size: 0.75rem; color: #333333; }
  .sys-card { background: white; border: 1.5px solid #ddeee4; border-radius: 10px; padding: 1.2rem; margin-bottom: 0.8rem; }
  .sys-card h4 { margin: 0 0 0.5rem 0; color: #111111; font-size: 16px !important; }
  .reco-box { background: #f0f8f3; border: 1px solid #b8ddc6; border-left: 5px solid #2d5a40;
              border-radius: 10px; padding: 1rem 1.3rem; margin-bottom: 0.6rem; }
  .reco-box h4 { margin: 0 0 0.3rem; color: #111111; font-size: 1rem; font-weight: 700; }
  .reco-box ul { margin: 0; padding-left: 1.2rem; color: #111111; font-size: 0.95rem; line-height: 1.8; }
  .sec-title { font-size: 1.3rem; font-weight: 700; color: #111111; border-bottom: 2px solid #2d5a40; padding-bottom: 0.3rem; margin-bottom: 1rem; }
  #MainMenu { visibility: hidden; } footer { visibility: hidden; }
  .stDataFrame td, .stDataFrame th, .stDataFrame tr { color: #000000 !important; font-size: 14px !important; }
  [data-testid="stDataFrame"] * { color: #000000 !important; }
  .dvn-scroller * { color: #000000 !important; }
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
    "🇧🇪 Belgium — Woningpas": {
        "color":"#87B40F","system":"Woningpas","status":"Fully operational — voluntary",
        "building_type":"Residential","website":"https://woningpas.vlaanderen.be/",
        "scores":{"Energy Performance Data":5,"Technical Documentation":4,"Renovation History":5,"Material Passport":2,"Waste & CDW Support":2,"Urban Mining Potential":1,"Legal Mandate":3,"Governance Clarity":5,"Privacy & Data Rights":4,"BIM Integration":2,"Open API / Data Exchange":4,"Cross-system Alignment":4,"Owner Access":5,"Professional Access":4,"Ease of Use":5,"Construction & Design Phase":3,"Operation & Renovation Phase":4,"End-of-Life Phase":1},
        "sources":{"Energy Performance Data":"Interoperable Europe Portal (2019)","Material Passport":"No material passport in official sources","Legal Mandate":"Flemish Decree — regional mandate","BIM Integration":"No BIM integration documented"},
    },
    "🇫🇷 France — CIL": {
        "color":"#005A96","system":"Carnet d'Information du Logement","status":"Mandatory since January 2023",
        "building_type":"Residential","website":"https://www.service-public.gouv.fr/particuliers/vosdroits/F36759?lang=en",
        "scores":{"Energy Performance Data":5,"Technical Documentation":4,"Renovation History":5,"Material Passport":2,"Waste & CDW Support":2,"Urban Mining Potential":1,"Legal Mandate":5,"Governance Clarity":4,"Privacy & Data Rights":4,"BIM Integration":2,"Open API / Data Exchange":2,"Cross-system Alignment":3,"Owner Access":5,"Professional Access":4,"Ease of Use":4,"Construction & Design Phase":3,"Operation & Renovation Phase":5,"End-of-Life Phase":1},
        "sources":{"Legal Mandate":"Loi Climat et Résilience (2021), Art. 167","Material Passport":"No material passport documented","Open API / Data Exchange":"No open API in French Government sources"},
    },
    "🇩🇪 Germany — iSFP": {
        "color":"#696969","system":"individueller Sanierungsfahrplan","status":"Fully operational — voluntary",
        "building_type":"Residential","website":"https://www.kfw.de/inlandsfoerderung/Privatpersonen/Bestehende-Immobilie/Energieeffizient-sanieren/Individueller-Sanierungsfahrplan/",
        "scores":{"Energy Performance Data":5,"Technical Documentation":3,"Renovation History":4,"Material Passport":2,"Waste & CDW Support":2,"Urban Mining Potential":1,"Legal Mandate":2,"Governance Clarity":4,"Privacy & Data Rights":4,"BIM Integration":1,"Open API / Data Exchange":1,"Cross-system Alignment":2,"Owner Access":5,"Professional Access":4,"Ease of Use":4,"Construction & Design Phase":1,"Operation & Renovation Phase":5,"End-of-Life Phase":1},
        "sources":{"Legal Mandate":"GEG (2020) — voluntary, linked to BEG funding (KfW, 2026)","BIM Integration":"No BIM — paper-based expert report (KfW, 2026)","Construction & Design Phase":"Renovation-only scope (KfW, 2026)"},
    },
    "🇳🇱 Netherlands — Madaster": {
        "color":"#E87744","system":"Madaster Platform","status":"Fully operational — voluntary (commercial)",
        "building_type":"All building types","website":"https://madaster.com/",
        "scores":{"Energy Performance Data":2,"Technical Documentation":4,"Renovation History":3,"Material Passport":5,"Waste & CDW Support":5,"Urban Mining Potential":5,"Legal Mandate":1,"Governance Clarity":3,"Privacy & Data Rights":4,"BIM Integration":5,"Open API / Data Exchange":5,"Cross-system Alignment":4,"Owner Access":3,"Professional Access":5,"Ease of Use":3,"Construction & Design Phase":5,"Operation & Renovation Phase":4,"End-of-Life Phase":5},
        "sources":{"Material Passport":"Madaster.com (2026): full material passport confirmed","Legal Mandate":"No mandate — commercial platform","BIM Integration":"Madaster.com (2026): BIM upload as primary input"},
    },
    "🇪🇺 EU — iBRoad": {
        "color":"#C8860A","system":"Individual Building Renovation Roadmap + Logbook","status":"Completed H2020 — tools published, piloted in 4 countries",
        "building_type":"Residential","website":"https://ibroad-project.eu/",
        "scores":{"Energy Performance Data":5,"Technical Documentation":3,"Renovation History":5,"Material Passport":1,"Waste & CDW Support":1,"Urban Mining Potential":1,"Legal Mandate":2,"Governance Clarity":3,"Privacy & Data Rights":3,"BIM Integration":2,"Open API / Data Exchange":2,"Cross-system Alignment":3,"Owner Access":5,"Professional Access":4,"Ease of Use":4,"Construction & Design Phase":1,"Operation & Renovation Phase":5,"End-of-Life Phase":1},
        "sources":{"Energy Performance Data":"CINEA (n.d.): energy audit core of the roadmap","Material Passport":"No material passport — energy focus only","Legal Mandate":"Voluntary H2020 — no legal basis","Construction & Design Phase":"Residential renovation focus only (CINEA, n.d.)"},
    },
    "🇪🇺 EU — openDBL": {
        "color":"#7B3FA0","system":"Open Digital Building Logbook Platform","status":"Ongoing Horizon Europe — pilots in Italy, Spain, Greece",
        "building_type":"All building types","website":"https://www.opendbl.eu/",
        "scores":{"Energy Performance Data":4,"Technical Documentation":5,"Renovation History":4,"Material Passport":3,"Waste & CDW Support":3,"Urban Mining Potential":3,"Legal Mandate":1,"Governance Clarity":3,"Privacy & Data Rights":4,"BIM Integration":5,"Open API / Data Exchange":5,"Cross-system Alignment":4,"Owner Access":3,"Professional Access":4,"Ease of Use":3,"Construction & Design Phase":4,"Operation & Renovation Phase":5,"End-of-Life Phase":3},
        "sources":{"BIM Integration":"openDBL.eu (2024): 3D scanning + BIM as core input","Open API / Data Exchange":"EDI (2023): openAPI is primary project objective","Legal Mandate":"EU research project — no legal mandate","Material Passport":"Material info in 3D model — not full passport yet"},
    },
}

if "criterion_notes" not in st.session_state:
    st.session_state.criterion_notes = {}

if "scores" not in st.session_state:
    st.session_state.scores = {k: dict(v["scores"]) for k,v in DEFAULT_SCORES.items()}
if "notes" not in st.session_state:
    st.session_state.notes = {k:{} for k in DEFAULT_SCORES}

def get_score(s,c): return st.session_state.scores[s].get(c, DEFAULT_SCORES[s]["scores"][c])
def dim_avg(s,d): crits=DIMENSIONS[d]; return round(sum(get_score(s,c) for c in crits)/len(crits),1)
def overall(s): return round(sum(get_score(s,c) for c in ALL_CRITERIA)/len(ALL_CRITERIA),1)

with st.sidebar:
    st.markdown("### 🏛️ DBL Tool AT")
    st.markdown('<p style="color:#111111;font-size:13px">Maria Dioszegi · UAS Technikum Wien 2026</p>', unsafe_allow_html=True)
    st.divider()
    st.markdown("**Select systems**")
    selected=[k for k in DEFAULT_SCORES if st.checkbox(k.split(" — ")[1],value=True,key=f"sel_{k}")]
    if not selected: selected=list(DEFAULT_SCORES.keys())[:1]
    st.divider()
    st.markdown("**Edit mode**")
    edit_mode=st.toggle("Enable score editing",value=False)
    st.markdown('<p style="color:#111111;font-size:13px">Adjust scores and add justification notes.</p>', unsafe_allow_html=True)

st.markdown("""
<div style="background:linear-gradient(135deg,#1a3a2a 0%,#2d5a40 100%);border-radius:14px;padding:2.5rem 3rem;margin-bottom:1.5rem">
  <div style="color:#FFFFFF;font-size:2.4rem;font-weight:800;margin-bottom:0.6rem;line-height:1.2;font-family:Segoe UI,Arial,sans-serif">DBL Tool AT &#8212; Digital Building Logbook Evaluation Tool for Austria</div>
  <div style="color:#FFFFFF;font-size:1.15rem;margin:0;font-weight:400;font-family:Segoe UI,Arial,sans-serif">Comparative analysis of 6 European DBL systems &nbsp;&middot;&nbsp; 6 dimensions &nbsp;&middot;&nbsp; 18 criteria &nbsp;&middot;&nbsp; Master&#39;s Thesis &nbsp;&middot;&nbsp; Maria Dioszegi &nbsp;&middot;&nbsp; UAS Technikum Wien 2026</div>
</div>
""", unsafe_allow_html=True)

top=max(selected,key=overall); avg=round(sum(overall(s) for s in selected)/len(selected),1)
st.markdown(f"""
<div class="kpi-row">
  <div class="kpi"><div class="label">Systems selected</div><div class="value">{len(selected)}</div><div class="sub">of 6 total</div></div>
  <div class="kpi"><div class="label">Dimensions</div><div class="value">6</div><div class="sub">18 criteria total</div></div>
  <div class="kpi"><div class="label">Top performer</div><div class="value">{overall(top)}</div><div class="sub">{top.split(' — ')[1]}</div></div>
  <div class="kpi"><div class="label">Average score</div><div class="value">{avg}</div><div class="sub">across selected systems</div></div>
</div>
""", unsafe_allow_html=True)

tabs=st.tabs(["📖 System Profiles","📊 Comparison Table","✏️ Edit Scores","🇦🇹 Recommendations for Austria"])

# Manual profile overrides in session state
if "profiles" not in st.session_state:
    st.session_state.profiles = {
        k: {
            "system": v["system"],
            "building_type": v["building_type"],

            "status": v["status"],
            "website": v["website"],
        } for k,v in DEFAULT_SCORES.items()
    }

with tabs[0]:
    st.markdown('<div class="sec-title">System Profiles</div>',unsafe_allow_html=True)
    st.markdown('<p style="color:#111111;font-size:13px">Profiles are pre-filled from document analysis. You can edit any field below.</p>', unsafe_allow_html=True)

    cols=st.columns(2)
    for i,key in enumerate(selected):
        ov=overall(key)
        with cols[i%2]:
            with st.expander(f"{key}  |  {ov}/5.0", expanded=True):
                p = st.session_state.profiles[key]
                p["system"]        = st.text_input("System name",       value=p["system"],        key=f"p_sys_{key}")
                p["building_type"] = st.text_input("Building type",      value=p["building_type"], key=f"p_bt_{key}")
                website_val = p.get("website", DEFAULT_SCORES[key]["website"])
                edit_key = f"edit_web_{key}"
                if edit_key not in st.session_state:
                    st.session_state[edit_key] = False
                col_link, col_btn = st.columns([5,1])
                with col_link:
                    st.markdown(f'<a href="{website_val}" target="_blank" style="display:block;background:#f0f2f6;border:1px solid #ddd;border-radius:6px;padding:9px 12px;color:#005A96;font-size:0.88rem;word-break:break-all;">{website_val}</a>', unsafe_allow_html=True)
                with col_btn:
                    if st.button("✏️", key=f"btn_web_{key}"):
                        st.session_state[edit_key] = not st.session_state[edit_key]
                if st.session_state[edit_key]:
                    new_url = st.text_input("Edit URL", value=website_val, key=f"p_web_{key}")
                    p["website"] = new_url
                else:
                    p["website"] = website_val
                p["status"]        = st.text_input("Status",             value=p["status"],        key=f"p_st_{key}")

    st.markdown('<div class="sec-title" style="margin-top:1.5rem">Overall Scores</div>',unsafe_allow_html=True)
    names=[k.split(" — ")[1] for k in selected]; ovs=[overall(k) for k in selected]
    colors=[DEFAULT_SCORES[k]["color"] for k in selected]
    fig=px.bar(x=names,y=ovs,color=names,color_discrete_sequence=colors,text=[f"{s:.1f}" for s in ovs],labels={"x":"","y":"Avg Score (1–5)"})
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False,yaxis=dict(range=[0,5.8],gridcolor="#e8f0eb"),plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",height=300,margin=dict(l=20,r=20,t=10,b=20))
    st.plotly_chart(fig,use_container_width=True)

    st.markdown('<div class="sec-title">Dimension Averages</div>',unsafe_allow_html=True)
    dim_rows=[{"Dimension":dim,**{k.split(" — ")[1]:dim_avg(k,dim) for k in selected}} for dim in DIMENSIONS]
    df_dim=pd.DataFrame(dim_rows).set_index("Dimension")
    st.dataframe(df_dim.style.background_gradient(cmap="Greens",vmin=1,vmax=5).format("{:.1f}"),use_container_width=True)

with tabs[1]:
    st.markdown('<div class="sec-title">Criterion-level Comparison</div>',unsafe_allow_html=True)
    st.markdown('<p style="color:#111111;font-size:13px"><b>Green</b> = 4-5 (strong) | <b>Yellow</b> = 3 (moderate) | <b>Red</b> = 1-2 (weak or absent)</p>', unsafe_allow_html=True)
    rows=[]
    for dim,crits in DIMENSIONS.items():
        for c in crits:
            row={"Dimension":dim,"Criterion":c}
            for k in selected: row[k.split(" — ")[1]]=get_score(k,c)
            rows.append(row)
    df=pd.DataFrame(rows); ccols=[k.split(" — ")[1] for k in selected]
    def cc(val): return "background-color:#d4edda;color:#1a5c2a;font-weight:600" if val>=4 else ("background-color:#FFE500;color:#3a3000" if val>=3 else "background-color:#f8d7da;color:#7a1c24")
    st.dataframe(df.style.applymap(cc,subset=ccols),use_container_width=True,height=750)

with tabs[2]:
    st.markdown('<div class="sec-title">Edit Scores & Add Justification Notes</div>',unsafe_allow_html=True)
    if not edit_mode:
        st.info("Enable 'Edit mode' in the sidebar to adjust scores and add notes.")
    else:
        
        for key in selected:
            s=DEFAULT_SCORES[key]
            with st.expander(f"✏️ {key}  |  Overall: {overall(key)}/5.0"):
                for dim,crits in DIMENSIONS.items():
                    st.markdown(f"**{dim}**")
                    for c in crits:
                        c1,c2,c3=st.columns([3,2,3])
                        with c1:
                            st.markdown(f'<p style="color:#111111;font-size:14px;font-weight:500;margin:8px 0 0">{c}</p>', unsafe_allow_html=True)
                        with c2:
                            nv=st.slider(c,1,5,value=st.session_state.scores[key].get(c,s["scores"][c]),key=f"sl_{key}_{c}",label_visibility="collapsed")
                            st.session_state.scores[key][c]=nv
                        with c3:
                            nt=st.text_input(c,value=st.session_state.notes[key].get(c,""),key=f"nt_{key}_{c}",label_visibility="collapsed",placeholder="Your note...")
                            st.session_state.notes[key][c]=nt
                    st.divider()
        if st.button("↩ Reset all to defaults"):
            st.session_state.scores={k:dict(v["scores"]) for k,v in DEFAULT_SCORES.items()}
            st.session_state.notes={k:{} for k in DEFAULT_SCORES}
            st.success("Reset to source-based defaults.")

with tabs[3]:
    st.markdown('<div class="sec-title">Minimum Requirements for Austria</div>',unsafe_allow_html=True)
    col_exp, col_pdf = st.columns([4,1])
    with col_exp:
        st.markdown('<p style="color:#111111;font-size:13px">Click any row to expand. Add notes. To save as PDF: Ctrl+P in browser → Save as PDF.</p>', unsafe_allow_html=True)
    with col_pdf:
        if st.button("🖨️ Print / Save PDF"):
            st.info("Press Ctrl+P in your browser, then choose 'Save as PDF'.")

    da={dim:{k:dim_avg(k,dim) for k in selected} for dim in DIMENSIONS}
    def best(dim): b=max(da[dim],key=da[dim].get); return b.split(" — ")[1],round(da[dim][b],1)
    def avgd(dim): return round(sum(da[dim].values())/len(da[dim]),1)
    def crit_avg(c): return round(sum(get_score(k,c) for k in selected)/len(selected),1)
    def best_for_crit(c):
        b=max(selected, key=lambda k: get_score(k,c))
        return b.split(" — ")[1], get_score(b,c)

    CRITERIA_DATA = {
        "Energy Performance Data":      {"adopt":"EPC data integration",                "why":"Records energy consumption, heating systems, insulation materials, and EPC ratings. Documented in CIL (France) as mandatory content and in iBRoad as the core of the renovation roadmap (CINEA, n.d.; French Government, n.d.)."},
        "Technical Documentation":      {"adopt":"BIM-based technical documentation",   "why":"Building plans, 3D models, and technical specifications stored digitally. Implemented in openDBL through BIM upload and 3D scanning as primary data input (openDBL.eu, 2024)."},
        "Renovation History":           {"adopt":"Mandatory renovation records",         "why":"Chronological record of all renovation works — insulation, windows, heating upgrades. Required by CIL (France) to be transferred to the buyer at point of sale (French Government, n.d.)."},
        "Material Passport":            {"adopt":"Material passport",                    "why":"Registration and tracking of all building materials and components across the full lifecycle. Implemented by Madaster with component-level documentation and residual value calculation (Madaster, 2026)."},
        "Waste & CDW Support":          {"adopt":"CDW tracking and circularity reporting","why":"Tracking of materials to support construction and demolition waste management and circularity reporting. Provided by Madaster through EU Taxonomy compliance and embodied carbon calculation (Madaster, 2026)."},
        "Urban Mining Potential":       {"adopt":"Urban mining data",                    "why":"Calculation of residual material value and recycling potential at building and city scale. Uniquely implemented by Madaster — no other reviewed system provides this functionality (Madaster, 2026)."},
        "Legal Mandate":                {"adopt":"National legal mandate",               "why":"Legally binding obligation to create and maintain a building information file. Established in France through Loi Climat et Resilience (2021), Art. 167 — the only mandatory national DBL instrument in Europe (French Government, n.d.)."},
        "Governance Clarity":           {"adopt":"Single responsible authority",         "why":"Single public authority responsible for ownership and maintenance of the DBL. Implemented by the Flemish Government (VEKA) as the sole managing body of Woningpas (Interoperable Europe Portal, 2019)."},
        "Privacy & Data Rights":        {"adopt":"Owner-controlled data access",         "why":"Building owners control who can access and share their logbook data. Designed in Woningpas as a shareable digital file — owners grant access to professionals or prospective buyers (Interoperable Europe Portal, 2019)."},
        "BIM Integration":              {"adopt":"BIM file integration",                 "why":"Upload of BIM models as primary data input using open IFC standards. Implemented by Madaster and openDBL — reduces manual data entry and enables 3D building data management (Madaster, 2026; openDBL.eu, 2024)."},
        "Open API / Data Exchange":     {"adopt":"Open API to national registries",      "why":"Open interfaces for data exchange with national and EU registries. Developed by openDBL as its primary technical objective — connecting to EPC registries, BIM tools, and municipal databases (openDBL.eu, 2024)."},
        "Cross-system Alignment":       {"adopt":"EU Semantic Data Model alignment",     "why":"Data structure aligned with EPBD requirements and EU frameworks. Defined in the EU Technical Study (2023) Linked Data architecture, designed to connect rather than replace existing national databases (Ecorys et al., 2023)."},
        "Owner Access":                 {"adopt":"Simple owner interface",               "why":"Simple digital file accessible and shareable by building owners without technical expertise. Implemented in Woningpas as a single centralised file and in CIL as a document transferred at point of sale (Interoperable Europe Portal, 2019)."},
        "Professional Access":          {"adopt":"Full professional dashboard",          "why":"Full analytical access for architects, energy auditors, facility managers, and municipalities. Provided by Madaster through detailed professional dashboards with circularity and carbon analytics (Madaster, 2026)."},
        "Ease of Use":                  {"adopt":"Guided non-expert data entry",         "why":"Guided data entry accessible to non-expert users with pre-populated fields. Designed in Woningpas through automatic aggregation of publicly available data, minimising manual input from owners (Interoperable Europe Portal, 2019)."},
        "Construction & Design Phase":  {"adopt":"Documentation from building permit",   "why":"Documentation starting at permit stage through BIM upload or design drawings. Implemented by Madaster from construction phase and by openDBL through 3D scanning of new buildings (Madaster, 2026; openDBL.eu, 2024)."},
        "Operation & Renovation Phase": {"adopt":"Renovation linked to subsidies",       "why":"Step-by-step renovation documentation linked to public funding schemes. Implemented by iSFP linked directly to KfW subsidies and by iBRoad as a long-term renovation roadmap for homeowners (KfW, 2026; CINEA, n.d.)."},
        "End-of-Life Phase":            {"adopt":"End-of-life material data",            "why":"Material recovery, demolition planning, and residual material value at building end of life. Uniquely implemented by Madaster as the only reviewed system covering the full lifecycle including demolition (Madaster, 2026)."},
    }

    for dim, crits in DIMENSIONS.items():
        bs, bsc = best(dim)
        st.markdown(f"""
        <div style="background:#f0f8f3;border-left:4px solid #2d5a40;border-radius:0 8px 8px 0;
        padding:0.5rem 1rem;margin:1rem 0 0.3rem;font-weight:600;color:#1a3a2a;font-size:0.95rem">
        {dim}
        </div>
        """, unsafe_allow_html=True)

        for c in crits:
            bs_c, sc_c = best_for_crit(c)
            data = CRITERIA_DATA.get(c, {"adopt":"—","why":"—"})
            label = f"**{c}** — Adopt: {data['adopt']}"
            with st.expander(label):
                st.markdown(f"**Best practice:** {bs_c} — {sc_c}/5.0")
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


