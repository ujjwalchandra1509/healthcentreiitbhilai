import os
from datetime import date, datetime

import streamlit as st
from dotenv import load_dotenv
from google import genai

from database import action, setup
from gemma_agent import get_action, reply


load_dotenv()
setup()
st.set_page_config(
    page_title="CampusCare | Student health",
    page_icon="✳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
    :root { --ink:#17323a; --muted:#687d81; --teal:#167d78; --teal-dark:#0d5d5b; --coral:#e58b6d; --paper:#f4f8f6; --surface:#ffffff; --line:#dce9e5; --shadow:0 14px 34px rgba(26,67,69,.08); }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
    .stApp { background:#f4f8f6; position:relative; }
    .stApp:before { content:''; position:fixed; inset:0; z-index:-1; pointer-events:none; background:radial-gradient(circle at 84% 8%, rgba(229,139,109,.16), transparent 28%), radial-gradient(circle at 12% 22%, rgba(22,125,120,.12), transparent 30%); background-attachment:fixed; }
    [data-testid="stSidebar"] { background:rgba(255,255,255,.82); border-right:1px solid var(--line); }
    [data-testid="stSidebar"] > div:first-child { padding-top:2rem; }
    .block-container { max-width:1180px; padding:2.4rem 2.8rem 4rem; }
    h1,h2,h3,h4 { color:var(--ink); font-family:'Manrope',sans-serif; letter-spacing:-.035em; }
    h1 { font-size:clamp(2.3rem,4vw,4rem); line-height:1.06; }
    h2 { font-size:1.55rem; margin-top:1.6rem; }
    p, label, .stCaption { color:var(--muted); }
    .brand { font:800 1.28rem 'Manrope',sans-serif; color:var(--ink); letter-spacing:-.045em; }
    .brand-mark { display:inline-grid; place-items:center; width:30px; height:30px; border-radius:9px; background:var(--teal); color:white; margin-right:8px; font-size:1rem; }
    .side-note { color:var(--muted); font-size:.82rem; line-height:1.55; padding:1rem .15rem; }
    .topline { display:flex; justify-content:space-between; align-items:center; margin:0 0 1.8rem; color:var(--muted); font-size:.84rem; }
    .status { display:flex; align-items:center; gap:.55rem; border-left:3px solid var(--teal); padding:.45rem .75rem; background:rgba(255,255,255,.62); color:var(--ink); font-size:.78rem; font-weight:600; }
    .live { height:8px; width:8px; border-radius:50%; background:#33a68b; box-shadow:0 0 0 4px rgba(51,166,139,.12); }
    .hero { background:linear-gradient(118deg,#d9f0e8 0%,#eff8f4 54%,#fff0e6 100%); border:1px solid #cfe6df; border-radius:22px; padding:2.45rem 2.8rem; position:relative; overflow:hidden; margin-bottom:1.25rem; box-shadow:var(--shadow); animation:appear .45s ease-out both; }
    .hero:after { content:'+'; position:absolute; right:5%; top:-55px; font-size:17rem; font-weight:300; color:rgba(22,125,120,.08); line-height:1; }
    .eyebrow { text-transform:uppercase; letter-spacing:.15em; font-size:.68rem; font-weight:700; color:var(--teal); margin-bottom:.7rem; }
    .hero h1 { max-width:720px; margin:.2rem 0 .8rem; }
    .hero p { max-width:610px; font-size:1rem; line-height:1.7; margin-bottom:0; }
    .card { background:rgba(255,255,255,.78); border:1px solid var(--line); border-radius:18px; padding:1.15rem 1.25rem; height:100%; box-shadow:0 8px 24px rgba(26,67,69,.05); }
    .doctor { background:rgba(255,255,255,.78); border:1px solid var(--line); border-radius:16px; padding:1.05rem 1.15rem; margin:.6rem 0; transition:transform .18s ease, box-shadow .18s ease; }
    .doctor:hover { transform:translateY(-2px); box-shadow:var(--shadow); }
    .doctor-name { font:700 1rem 'Manrope',sans-serif; color:var(--ink); }
    .doctor-spec { color:var(--teal); font-size:.83rem; font-weight:600; margin:.25rem 0 .55rem; }
    .doctor-meta { color:var(--muted); font-size:.78rem; }
    .section-kicker { font-size:.72rem; color:var(--teal); font-weight:700; text-transform:uppercase; letter-spacing:.13em; }
    .info-row { background:rgba(255,255,255,.78); border:1px solid var(--line); border-radius:13px; padding:.82rem 1rem; margin:.48rem 0; color:var(--muted); }
    .info-row strong { color:var(--ink); }
    .stButton > button, .stFormSubmitButton > button { min-height:2.65rem; border-radius:8px; font-weight:700; border-color:var(--line); background:rgba(255,255,255,.8); color:var(--ink); transition:background .18s ease, border-color .18s ease, transform .18s ease; }
    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] { background:var(--teal); border-color:var(--teal); color:white; }
    .stButton > button:hover, .stFormSubmitButton > button:hover { border-color:var(--teal); color:var(--teal); transform:translateY(-1px); }
    .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover { color:white; background:var(--teal-dark); }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stTimeInput input, .stNumberInput input { background:rgba(255,255,255,.82); color:var(--ink); border-color:var(--line); border-radius:9px; }
    [data-testid="stTabs"] button { color:var(--muted); font-weight:600; }
    [data-testid="stTabs"] button[aria-selected="true"] { color:var(--teal); }
    [data-testid="stExpander"], [data-testid="stChatMessage"] { background:rgba(255,255,255,.72); border:1px solid var(--line); border-radius:13px; }
    [data-testid="stRadio"] label, [data-testid="stMarkdownContainer"] p, [data-testid="stMetricLabel"] { color:var(--muted); }
    [data-testid="stMetricValue"] { color:var(--ink); }
    [data-baseweb="select"] span, [data-baseweb="popover"] *, [role="listbox"] * { color:var(--ink); }
    hr { border-color:var(--line); }
    .stAlert { border-radius:12px; }
    footer { visibility:hidden; }
    @keyframes appear { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
    @media (prefers-reduced-motion: reduce) { *, *:before, *:after { animation:none !important; transition:none !important; } }
    @media (max-width: 700px) { .block-container { padding:1.1rem 1rem 3rem; } .hero { padding:1.7rem 1.45rem; } .hero:after { right:-8%; top:10%; font-size:9rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def gemini_client():
    key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=key) if key else None


def ask_assistant(question, client):
    try:
        task = get_action(client, question)
        result = action(task) if task.get("action") != "answer" else task
        return reply(client, question, result)
    except (RuntimeError, ValueError, KeyError) as error:
        return f"I couldn't complete that request: {error}"


client = gemini_client()
today = date.today()

if "nav_page" in st.session_state:
    st.session_state.navigation = st.session_state.pop("nav_page")

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">✳</span>CampusCare</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-note">Your campus health centre, made easier to reach.</div>', unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("Explore", ["Overview", "Care directory", "Book a visit", "Centre information"], label_visibility="collapsed", key="navigation")
    st.markdown("---")
    st.markdown("**Need urgent help?**")
    st.caption("For emergencies, contact the medical centre directly. The AI assistant is not an emergency service.")
    st.markdown('<div class="status"><span class="live"></span> Centre support: 24/7</div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="topline"><span>College Medical Centre &nbsp;·&nbsp; Student health services</span><span>{today.strftime("%A, %d %B")}</span></div>',
    unsafe_allow_html=True,
)

if page == "Overview":
    st.markdown(
        '<section class="hero"><div class="eyebrow">Medical centre services</div>'
        '<h1>Appointments, schedules, and centre information.</h1>'
        '<p>Check provider availability, book a visit, or contact the health centre.</p></section>',
        unsafe_allow_html=True,
    )
    st.markdown("## Start here")
    st.caption("Use the directory to check schedules or book a visit when you know what you need.")
    q1, q2 = st.columns(2)
    with q1:
        if st.button("Browse care team  →", use_container_width=True):
            st.session_state.nav_page = "Care directory"
            st.rerun()
    with q2:
        if st.button("Book an appointment  →", type="primary", use_container_width=True):
            st.session_state.nav_page = "Book a visit"
            st.rerun()

    st.markdown("## Ask CampusCare")
    status = "Assistant ready" if client else "Assistant paused · add GEMINI_API_KEY to .env"
    st.markdown(f'<div class="status"><span class="{"live" if client else ""}"></span>{status}</div>', unsafe_allow_html=True)
    suggestions = ["Which providers are available today?", "What are the centre hours?", "Help me book an appointment", "Who should I contact in an emergency?"]
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for item in st.session_state.chat_history:
        with st.chat_message(item["role"]):
            st.write(item["content"])
    if client:
        prompt_cols = st.columns(4)
        for col, prompt in zip(prompt_cols, suggestions):
            with col:
                if st.button(prompt, key=f"prompt_{prompt}", use_container_width=True):
                    st.session_state.chat_question = prompt
        question = st.chat_input("Ask about care, appointments, or centre information")
        question = question or st.session_state.pop("chat_question", None)
        if question:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.write(question)
            answer = ask_assistant(question, client)
            with st.chat_message("assistant"):
                st.write(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
    else:
        st.info("The assistant is paused. Add GEMINI_API_KEY to your .env file and restart the app to enable AI guidance.")

elif page == "Care directory":
    st.markdown('<div class="section-kicker">Find your care team</div>', unsafe_allow_html=True)
    st.title("Care directory")
    st.caption("See who is scheduled and how many appointment slots remain.")
    selected_date = st.date_input("Check availability for", today, key="directory_date")
    doctors = action({"action": "list_doctors", "appointment_date": selected_date.isoformat()})["doctors"]
    if not doctors:
        st.info("No providers are listed yet.")
    for doctor in doctors:
        left, right = st.columns([5, 1])
        with left:
            scheduled = "Scheduled" if doctor["available_on_date"] else "Not scheduled"
            st.markdown(f'<div class="doctor"><div class="doctor-name">{doctor["name"]}</div><div class="doctor-spec">{doctor["specialization"]}</div><div class="doctor-meta">{doctor["working_days"]} &nbsp;·&nbsp; {doctor["working_hours"]} &nbsp;·&nbsp; {scheduled}</div></div>', unsafe_allow_html=True)
        with right:
            st.metric("Slots", f'{max(doctor["remaining_slots"], 0)} / {doctor["daily_capacity"]}')

elif page == "Book a visit":
    st.markdown('<div class="section-kicker">Plan your visit</div>', unsafe_allow_html=True)
    st.title("Book an appointment")
    st.caption("Choose a provider and preferred time. We'll confirm your booking right away.")
    doctors = action({"action": "list_doctors"})["doctors"]
    if not doctors:
        st.info("Appointments are not available yet because no providers are listed.")
    else:
        with st.form("booking"):
            doctor = st.selectbox("Provider", [item["name"] for item in doctors])
            name_col, email_col = st.columns(2)
            with name_col:
                patient = st.text_input("Your name")
            with email_col:
                email = st.text_input("Email address")
            date_col, time_col = st.columns(2)
            with date_col:
                visit_date = st.date_input("Date", today, min_value=today)
            with time_col:
                visit_time = st.time_input("Preferred time")
            reason = st.text_area("Reason for visit", placeholder="A short description helps the team prepare.")
            submitted = st.form_submit_button("Confirm appointment", type="primary", use_container_width=True)
        if submitted:
            if not patient.strip() or not email.strip() or not reason.strip():
                st.error("Please complete your name, email, and reason for visit.")
            else:
                result = action({"action": "book_appointment", "doctor_name": doctor, "patient_name": patient.strip(), "patient_email": email.strip(), "appointment_date": visit_date.isoformat(), "appointment_time": visit_time.strftime("%H:%M"), "reason": reason.strip()})
                (st.success if "message" in result else st.error)(result.get("message") or result.get("error"))

else:
    st.markdown('<div class="section-kicker">Were here for you</div>', unsafe_allow_html=True)
    st.title("Centre information")
    st.caption("Hours and contact details for the College Medical Centre.")
    centre = action({"action": "centre_information"})
    hours_col, contact_col = st.columns(2)
    with hours_col:
        st.subheader("Hours")
        if not centre["hours"]:
            st.info("Centre hours have not been added yet.")
        for item in centre["hours"]:
            st.markdown(f'<div class="info-row"><strong>{item["day_group"]}</strong><br>{item["timings"]}</div>', unsafe_allow_html=True)
    with contact_col:
        st.subheader("Contact directory")
        if not centre["contacts"]:
            st.info("Contact details have not been added yet.")
        for item in centre["contacts"]:
            st.markdown(f'<div class="info-row"><strong>{item["contact_person"]}</strong><br>{item["phone"]}</div>', unsafe_allow_html=True)

    with st.expander("Staff schedule tools"):
        st.caption("Restricted operational controls for authorised staff.")
        doctors = action({"action": "list_doctors"})["doctors"]
        if not doctors:
            st.info("Add a provider before updating schedules.")
        else:
            with st.form("admin"):
                doctor_name = st.selectbox("Provider to update", [item["name"] for item in doctors])
                pin = st.text_input("Admin PIN", type="password")
                days = st.text_input("Working days")
                hours = st.text_input("Working hours")
                capacity = st.number_input("Daily capacity", min_value=1, value=10)
                update = st.form_submit_button("Update schedule", type="primary")
            if update:
                result = action({"action": "edit_doctor", "doctor_name": doctor_name, "admin_pin": pin, "working_days": days or None, "working_hours": hours or None, "daily_capacity": capacity})
                (st.success if "message" in result else st.error)(result.get("message") or result.get("error"))

st.markdown("---")
st.caption(f"CampusCare · Last refreshed {datetime.now().strftime('%d %b %Y, %I:%M %p')} · For emergencies, contact the centre directly.")
