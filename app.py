from pathlib import Path
from datetime import date
import io
import pandas as pd
import plotly.express as px
import streamlit as st

# ------------------------------------------------------------
# PAGE CONFIG + THEME
# ------------------------------------------------------------
st.set_page_config(
    page_title="Eventora | Smart Event Budget Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_DIR = Path(__file__).parent / "data"
HISTORY_FILE = DATA_DIR / "event_history.csv"
DATA_DIR.mkdir(exist_ok=True)

EVENTS = {
    "Birthday Celebration": {
        "venue": 14000, "decoration": 12000, "photo": 8500,
        "food": 420, "sound": 5500, "stage": 6500,
        "entertainment": 7000, "misc": 0.09
    },
    "Wedding / Marriage": {
        "venue": 65000, "decoration": 55000, "photo": 35000,
        "food": 950, "sound": 22000, "stage": 30000,
        "entertainment": 18000, "misc": 0.12
    },
    "Puberty Ceremony": {
        "venue": 28000, "decoration": 24000, "photo": 18000,
        "food": 600, "sound": 10000, "stage": 15000,
        "entertainment": 6000, "misc": 0.10
    },
    "Success Meet": {
        "venue": 22000, "decoration": 13000, "photo": 10000,
        "food": 480, "sound": 16000, "stage": 12000,
        "entertainment": 12000, "misc": 0.09
    },
    "Engagement": {
        "venue": 30000, "decoration": 28000, "photo": 20000,
        "food": 650, "sound": 12000, "stage": 18000,
        "entertainment": 8000, "misc": 0.10
    },
    "Baby Shower / Seemantham": {
        "venue": 18000, "decoration": 16000, "photo": 12000,
        "food": 500, "sound": 7000, "stage": 9000,
        "entertainment": 5000, "misc": 0.09
    },
    "Housewarming": {
        "venue": 10000, "decoration": 9000, "photo": 7000,
        "food": 380, "sound": 4000, "stage": 3500,
        "entertainment": 2500, "misc": 0.08
    },
    "Corporate / College Event": {
        "venue": 35000, "decoration": 18000, "photo": 15000,
        "food": 700, "sound": 24000, "stage": 20000,
        "entertainment": 16000, "misc": 0.10
    },
    "Custom Function": {
        "venue": 18000, "decoration": 14000, "photo": 10000,
        "food": 500, "sound": 8000, "stage": 9000,
        "entertainment": 5000, "misc": 0.10
    }
}

CITY_FACTOR = {
    "Chennai": 1.00, "Coimbatore": 0.88, "Madurai": 0.82,
    "Trichy": 0.84, "Salem": 0.80, "Bengaluru": 1.12,
    "Hyderabad": 1.05, "Other": 1.00
}
QUALITY_FACTOR = {"Essential": 0.78, "Classic": 1.00, "Premium": 1.38, "Luxury": 1.85}

def inr(value):
    return f"₹{value:,.0f}"

def estimate(event_type, guests, days, city, quality, opts):
    rate = EVENTS[event_type]
    city_factor = CITY_FACTOR[city]
    q = QUALITY_FACTOR[quality]
    costs = {
        "Venue / Hall": rate["venue"] * days * city_factor,
        "Decoration & Theme": rate["decoration"] * q * city_factor,
        "Photography & Videography": rate["photo"] * q * city_factor,
        "Food & Catering": rate["food"] * guests * days * opts["meal_factor"] * city_factor,
        "Sound & Lighting": rate["sound"] * q * city_factor,
        "Stage & Backdrop": rate["stage"] * q * city_factor,
        "Entertainment": rate["entertainment"] * q * city_factor,
        "Stalls / Food Counters": opts["stalls"],
        "Transportation": opts["transport"],
        "Makeup / Clothing": opts["makeup"],
        "Invitation / Printing": opts["invites"],
        "Gifts / Return Gifts": opts["gifts"],
        "Other Expenses": opts["other"]
    }
    subtotal = sum(costs.values())
    contingency = subtotal * rate["misc"]
    costs["Contingency Reserve"] = contingency
    return costs, subtotal, contingency, subtotal + contingency

def load_history():
    if HISTORY_FILE.exists():
        try:
            return pd.read_csv(HISTORY_FILE)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

# ------------------------------------------------------------
# PREMIUM CSS
# ------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --ink:#f4f2ff; --muted:#a7a5bd; --panel:#151525; --line:rgba(255,255,255,.09); }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp {
  background:
    radial-gradient(ellipse at 8% 0%, rgba(112,76,255,.20), transparent 32%),
    radial-gradient(ellipse at 92% 10%, rgba(27,190,177,.12), transparent 28%),
    #0b0b14;
  color:var(--ink);
}
.block-container { padding-top:1.7rem; padding-bottom:3rem; max-width:1440px; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#151426 0%,#10101b 100%); border-right:1px solid var(--line); }
[data-testid="stSidebar"] * { color:#efedff; }
h1,h2,h3 { font-family:'Manrope',sans-serif; letter-spacing:-.04em; color:#fbfaff; }
.hero {
  padding:30px 34px; border:1px solid rgba(173,151,255,.24); border-radius:25px;
  background:linear-gradient(115deg,rgba(93,65,210,.30),rgba(26,155,151,.12) 65%,rgba(255,255,255,.035));
  box-shadow:0 20px 65px rgba(0,0,0,.20); margin-bottom:22px;
}
.hero-kicker { color:#c3b7ff; text-transform:uppercase; font-size:11px; font-weight:800; letter-spacing:2px; }
.hero-title { font-family:'Manrope',sans-serif; font-size:clamp(28px,4vw,44px); line-height:1.08; font-weight:800; margin:10px 0 9px; }
.hero-copy { color:#c4c1d7; font-size:14px; max-width:720px; line-height:1.7; }
.metric-card {
  background:linear-gradient(145deg,rgba(255,255,255,.075),rgba(255,255,255,.025));
  border:1px solid var(--line); border-radius:18px; padding:18px 20px; min-height:112px;
}
.metric-label { color:#aaa7c2; font-size:12px; font-weight:700; letter-spacing:.5px; }
.metric-value { color:#fff; font-family:'Manrope'; font-size:27px; font-weight:800; margin-top:8px; }
.metric-note { color:#7edbc9; font-size:11px; margin-top:2px; }
.section-label { color:#b9adff; text-transform:uppercase; letter-spacing:1.7px; font-size:11px; font-weight:800; margin:12px 0 8px; }
.info-card {
  background:rgba(255,255,255,.045); border:1px solid var(--line);
  border-radius:17px; padding:18px; height:100%;
}
.info-title { font-weight:800; color:#f5f2ff; font-size:15px; margin-bottom:7px; }
.info-copy { color:#aaa7bd; font-size:12px; line-height:1.6; }
div.stButton > button {
  border:0; border-radius:12px; padding:.68rem 1rem; font-weight:800;
  background:linear-gradient(100deg,#8065ff,#5e9eff); color:white;
  box-shadow:0 8px 24px rgba(105,91,255,.22); transition:.2s ease;
}
div.stButton > button:hover { transform:translateY(-1px); border:0; color:white; filter:brightness(1.08); }
.stDownloadButton button { border-radius:11px; }
div[data-testid="stTabs"] button { color:#b9b6ca; font-weight:700; }
div[data-testid="stTabs"] button[aria-selected="true"] { color:#c8bcff; }
[data-testid="stNumberInput"] input, [data-testid="stTextInput"] input, [data-testid="stDateInput"] input {
  background:#171727; color:#fff; border-radius:10px;
}
[data-testid="stSelectbox"] > div > div, [data-testid="stMultiSelect"] > div > div {
  background:#171727; border-radius:10px;
}
hr { border-color:var(--line); }
small, .muted { color:#aaa7bd; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("<div style='font-size:25px;font-weight:800;letter-spacing:-1px'>✦ EVENTORA</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#aaa7bd;font-size:10px;letter-spacing:2px;margin:3px 0 24px'>SMART EVENT BUDGET STUDIO</div>", unsafe_allow_html=True)
    page = st.radio("WORKSPACE", ["Overview", "Create Estimate", "Budget Analytics", "Saved Events", "About Project"], label_visibility="visible")
    st.markdown("---")
    st.markdown("**Planning workspace**")
    st.caption("Create clear, category-wise event budgets before you book vendors.")
    st.markdown("---")
    st.caption("Version 1.0 • Budget estimates in INR")

# ------------------------------------------------------------
# OVERVIEW
# ------------------------------------------------------------
if page == "Overview":
    st.markdown("""
    <div class="hero">
      <div class="hero-kicker">Plan beautifully. Spend wisely.</div>
      <div class="hero-title">Every great event starts<br>with a smarter budget.</div>
      <div class="hero-copy">An intelligent event planning workspace to estimate venue, catering, decoration, photography, stage, stalls and all the little expenses that make an occasion memorable.</div>
    </div>
    """, unsafe_allow_html=True)
    hist = load_history()
    total_events = len(hist)
    total_value = hist["estimated_total"].sum() if not hist.empty and "estimated_total" in hist else 0
    avg_value = hist["estimated_total"].mean() if not hist.empty and "estimated_total" in hist else 0
    m1,m2,m3 = st.columns(3)
    for col, label, val, note in [
        (m1,"SAVED EVENTS",f"{total_events:,}","Your planning history"),
        (m2,"TOTAL PLANNED VALUE",inr(total_value),"Across saved estimates"),
        (m3,"AVERAGE EVENT BUDGET",inr(avg_value),"Average saved estimate")
    ]:
        with col:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{val}</div><div class='metric-note'>{note}</div></div>",unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Explore the workspace</div>",unsafe_allow_html=True)
    cards = [
        ("01","Create an estimate","Choose your function, guest count, city and service preferences."),
        ("02","Understand every rupee","Review category-wise cost estimates and budget distribution."),
        ("03","Save and compare","Keep a record of estimates and compare future event plans.")
    ]
    cols = st.columns(3)
    for col,(num,title,copy) in zip(cols,cards):
        with col:
            st.markdown(f"<div class='info-card'><div style='color:#9c89ff;font-size:12px;font-weight:800'>{num}</div><div class='info-title'>{title}</div><div class='info-copy'>{copy}</div></div>",unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Supported occasions</div>",unsafe_allow_html=True)
    st.write("🎂 Birthday  ·  💍 Wedding  ·  🌸 Puberty Ceremony  ·  🏆 Success Meet  ·  🤝 Corporate Event  ·  💐 Engagement  ·  🍼 Baby Shower  ·  🏡 Housewarming  ·  🎓 College Event")

# ------------------------------------------------------------
# CREATE ESTIMATE
# ------------------------------------------------------------
elif page == "Create Estimate":
    st.markdown("<div class='hero'><div class='hero-kicker'>Event budget builder</div><div class='hero-title'>Create your event estimate.</div><div class='hero-copy'>Enter the event details and customize the services. Your estimate updates when you calculate the budget.</div></div>",unsafe_allow_html=True)
    with st.form("estimate_form"):
        st.markdown("<div class='section-label'>01 / Event information</div>",unsafe_allow_html=True)
        a,b,c = st.columns(3)
        with a:
            event_name = st.text_input("Event name",placeholder="e.g. Kumar Family Wedding")
            event_type = st.selectbox("Function type",list(EVENTS.keys()))
            city = st.selectbox("Event city",list(CITY_FACTOR.keys()))
        with b:
            event_date = st.date_input("Event date",value=date.today())
            guests = st.number_input("Expected guests",min_value=1,max_value=100000,value=200,step=10)
            days = st.number_input("Duration (days)",min_value=1,max_value=30,value=1)
        with c:
            quality = st.selectbox("Experience level",list(QUALITY_FACTOR.keys()),index=1)
            meal = st.selectbox("Catering preference",["Standard menu","Premium menu","Luxury menu"])
            meal_factor = {"Standard menu":1.0,"Premium menu":1.25,"Luxury menu":1.55}[meal]
        st.markdown("<div class='section-label'>02 / Add-on services and allowances</div>",unsafe_allow_html=True)
        x1,x2,x3,x4 = st.columns(4)
        with x1:
            stalls = st.number_input("Stalls / counters (₹)",min_value=0,value=0,step=1000)
            transport = st.number_input("Transportation (₹)",min_value=0,value=5000,step=1000)
        with x2:
            makeup = st.number_input("Makeup / clothing (₹)",min_value=0,value=0,step=1000)
            invites = st.number_input("Invitation / printing (₹)",min_value=0,value=3000,step=500)
        with x3:
            gifts = st.number_input("Gifts / return gifts (₹)",min_value=0,value=5000,step=1000)
            other = st.number_input("Other expenses (₹)",min_value=0,value=5000,step=1000)
        with x4:
            custom_buffer = st.number_input("Extra contingency (%)",min_value=0,max_value=30,value=0,step=1)
            notes = st.text_input("Special requirements",placeholder="e.g. floral entrance, LED wall")
        submitted = st.form_submit_button("✦ Calculate my event budget",use_container_width=True)
    if submitted:
        opts={"stalls":stalls,"transport":transport,"makeup":makeup,"invites":invites,"gifts":gifts,"other":other,"meal_factor":meal_factor}
        costs,subtotal,contingency,total=estimate(event_type,guests,days,city,quality,opts)
        extra = subtotal * custom_buffer / 100
        costs["Additional contingency"] = extra
        total += extra
        st.session_state["current_estimate"]={
            "event_name":event_name or event_type,"event_type":event_type,"city":city,
            "event_date":str(event_date),"guests":int(guests),"days":int(days),
            "quality":quality,"meal":meal,"notes":notes,"costs":costs,
            "subtotal":subtotal,"contingency":contingency+extra,"total":total
        }
    if "current_estimate" in st.session_state:
        r=st.session_state["current_estimate"]
        st.divider()
        st.markdown("<div class='section-label'>03 / Your budget result</div>",unsafe_allow_html=True)
        k1,k2,k3 = st.columns(3)
        for col,label,val,note in [
            (k1,"ESTIMATED TOTAL",inr(r["total"]),"Your current planning estimate"),
            (k2,"BASE EXPENSES",inr(r["subtotal"]),"Before contingency reserve"),
            (k3,"CONTINGENCY",inr(r["contingency"]),"Buffer for unexpected costs")
        ]:
            with col:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{val}</div><div class='metric-note'>{note}</div></div>",unsafe_allow_html=True)
        breakdown=pd.DataFrame([{"Expense category":k,"Estimated amount (₹)":round(v)} for k,v in r["costs"].items()])
        tab1,tab2,tab3=st.tabs(["Expense breakdown","Budget visualization","Planning summary"])
        with tab1:
            st.dataframe(breakdown,use_container_width=True,hide_index=True)
        with tab2:
            fig=px.pie(breakdown,names="Expense category",values="Estimated amount (₹)",hole=.58,
                       title="Where your event budget goes")
            fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#efedff",legend_title="")
            st.plotly_chart(fig,use_container_width=True)
        with tab3:
            st.write(f"**{r['event_name']}** — {r['event_type']}")
            st.write(f"📍 {r['city']}  ·  📅 {r['event_date']}  ·  👥 {r['guests']:,} guests  ·  {r['days']} day(s)")
            st.write(f"Package: **{r['quality']}** | Catering: **{r['meal']}**")
            if r["notes"]: st.write(f"Special requirements: {r['notes']}")
            st.info(f"Planning range: {inr(r['total']*.90)} to {inr(r['total']*1.15)}. This is an indicative range, not a vendor quotation.")
        csv_data=breakdown.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download expense breakdown CSV",csv_data,"event_budget_breakdown.csv","text/csv")
        excel_buffer=io.BytesIO()
        with pd.ExcelWriter(excel_buffer,engine="openpyxl") as writer:
            breakdown.to_excel(writer,index=False,sheet_name="Expense Breakdown")
            pd.DataFrame([{"Event":r["event_name"],"Type":r["event_type"],"City":r["city"],"Date":r["event_date"],"Guests":r["guests"],"Total Budget":round(r["total"])}]).to_excel(writer,index=False,sheet_name="Event Summary")
        st.download_button("⬇ Download Excel report",excel_buffer.getvalue(),"event_budget_report.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        if st.button("＋ Save this estimate to history",use_container_width=True):
            record={"event_name":r["event_name"],"event_type":r["event_type"],"city":r["city"],"event_date":r["event_date"],"guests":r["guests"],"days":r["days"],"quality":r["quality"],"estimated_total":round(r["total"])}
            old=load_history()
            pd.concat([old,pd.DataFrame([record])],ignore_index=True).to_csv(HISTORY_FILE,index=False)
            st.success("Estimate saved successfully.")

# ------------------------------------------------------------
# ANALYTICS
# ------------------------------------------------------------
elif page == "Budget Analytics":
    st.markdown("<div class='hero'><div class='hero-kicker'>Insights and comparisons</div><div class='hero-title'>See the bigger budget picture.</div><div class='hero-copy'>Explore saved event estimates and understand how your planned budgets are distributed.</div></div>",unsafe_allow_html=True)
    hist=load_history()
    if hist.empty:
        st.info("No saved estimates yet. Create an estimate and choose 'Save this estimate to history' to populate analytics.")
    else:
        p1,p2=st.columns(2)
        with p1:
            types=st.multiselect("Filter by event type",sorted(hist["event_type"].dropna().unique()),default=sorted(hist["event_type"].dropna().unique()))
        with p2:
            cities=st.multiselect("Filter by city",sorted(hist["city"].dropna().unique()),default=sorted(hist["city"].dropna().unique()))
        view=hist[hist["event_type"].isin(types)&hist["city"].isin(cities)]
        q1,q2,q3=st.columns(3)
        q1.metric("Events",len(view))
        q2.metric("Total planned",inr(view["estimated_total"].sum()))
        q3.metric("Average budget",inr(view["estimated_total"].mean()) if len(view) else "₹0")
        if not view.empty:
            fig=px.bar(view,x="event_name",y="estimated_total",color="event_type",title="Saved event budget comparison",hover_data=["city","guests"])
            fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#efedff",xaxis_title="",yaxis_title="Estimated budget (₹)")
            st.plotly_chart(fig,use_container_width=True)
            st.dataframe(view,use_container_width=True,hide_index=True)

# ------------------------------------------------------------
# SAVED EVENTS
# ------------------------------------------------------------
elif page == "Saved Events":
    st.markdown("<div class='hero'><div class='hero-kicker'>Your planning history</div><div class='hero-title'>Saved event estimates.</div><div class='hero-copy'>Keep track of budgets you have prepared and export your records.</div></div>",unsafe_allow_html=True)
    hist=load_history()
    if hist.empty:
        st.info("You haven't saved any estimates yet.")
    else:
        st.dataframe(hist,use_container_width=True,hide_index=True)
        st.download_button("⬇ Download saved event history",hist.to_csv(index=False).encode("utf-8"),"event_history.csv","text/csv")
        if st.button("Clear saved history"):
            HISTORY_FILE.unlink(missing_ok=True)
            st.rerun()

# ------------------------------------------------------------
# ABOUT
# ------------------------------------------------------------
elif page == "About Project":
    st.markdown("<div class='hero'><div class='hero-kicker'>About Eventora</div><div class='hero-title'>A smarter way to plan events.</div><div class='hero-copy'>An event budgeting prototype designed to bring cost visibility and structure to personal, family and corporate functions.</div></div>",unsafe_allow_html=True)
    st.markdown("### What this application does")
    st.write("Eventora creates an indicative expense plan based on function type, city, guest count, duration, service quality and optional add-ons.")
    st.markdown("### Technology")
    st.write("Python · Streamlit · Pandas · Plotly · Excel export")
    st.markdown("### Important pricing note")
    st.warning("The baseline rates in this prototype are illustrative assumptions. They are not live vendor prices or a trained machine-learning prediction. Validate and replace the rates with real quotations from vendors in each city. A future ML model should be trained on verified historical event records.")
    st.markdown("### Suggested next development")
    st.write("Connect a vendor quotation database, add authentication, store events in SQLite, then train separate regression models for food, decoration, venue, photography and total budget.")
