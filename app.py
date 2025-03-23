import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from db import init_db, insert_lead, fetch_all_leads_df, update_leads_bulk
from lead_utils import calculate_score
from scraper import extract_info_from_url

# Set up page
st.set_page_config(
    page_title="LeadNavigator by InnHealthium",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

# Branding & title
st.image("innhealthium_logo.png", width=200)
st.title("🚀 LeadNavigator CRM")
st.caption("Empowering MedTech innovation with AI-powered lead management.")

# Sidebar
st.sidebar.image("innhealthium_logo.png", width=150)
menu = ["📤 Upload Leads", "🤖 Paste Website (AI)", "📝 Edit Leads"]
choice = st.sidebar.radio("Navigate", menu)

# Upload Leads
if choice == "📤 Upload Leads":
    st.subheader("📁 Upload Excel Leads")
    st.markdown("Upload your `.xlsx` file with columns like `company`, `summary`, `email`, etc.")

    file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            score = calculate_score(row['summary'], row['growth_phase'])
            data = (
                row['company'], row['website'], row['email'], row['contact_person'],
                row['summary'], row['growth_phase'], score, "", ""
            )
            insert_lead(data)
        st.balloons()
        st.success("✅ Leads uploaded and scored!")

# Paste URL (AI)
elif choice == "🤖 Paste Website (AI)":
    st.subheader("🌐 Analyze Startup Website via AI")
    st.markdown("Let AI extract company info & score it.")

    company_url = st.text_input("Paste a startup homepage URL")
    if st.button("🧠 Analyze with GPT"):
        with st.spinner("AI is reading the site..."):
            result = extract_info_from_url(company_url)

        st.code(result)

        parsed = {}
        for line in result.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                parsed[key.strip().lower()] = value.strip()

        if "company" in parsed:
            insert_lead((
                parsed.get("company", ""),
                company_url,
                parsed.get("email", ""),
                "Unknown",
                parsed.get("summary", ""),
                parsed.get("growth phase", "").lower(),
                int(parsed.get("score", "0")),
                "",
                ""
            ))
            st.success(f"🎯 {parsed.get('company')} added to your leads!")
        else:
            st.warning("🤔 GPT response couldn't be parsed properly.")

# View & Edit
elif choice == "📝 Edit Leads":
    st.subheader("🛠 Manage Your Lead Database")
    df = fetch_all_leads_df()

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination()
    gb.configure_default_column(editable=True)
    gb.configure_column("ID", editable=False)
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MANUAL,
        editable=True,
        theme="material",
        height=600,
        key="editable_grid"
    )

    updated_df = grid_response["data"]
    if st.button("💾 Save Changes"):
        update_leads_bulk(updated_df)
        st.success("✅ Changes saved!")

# Footer
st.markdown("---")
st.caption("Made with ❤️ by InnHealthium | Accelerating MedTech, IVD & Diagnostics innovation 🚀")
