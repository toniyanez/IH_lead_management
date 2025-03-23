import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from db import init_db, insert_lead, fetch_all_leads_df, update_leads_bulk
from lead_utils import calculate_score
from scraper import extract_info_from_url

st.set_page_config(page_title="LeadNavigator", layout="wide")
init_db()

st.title("🚀 InnHealthium - LeadNavigator")

menu = ["Upload Excel", "Paste URL (AI)", "View & Edit Leads"]
choice = st.sidebar.selectbox("Choose Action", menu)

if choice == "Upload Excel":
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
        st.success("✅ Leads uploaded!")

elif choice == "Paste URL (AI)":
    st.subheader("🔗 Analyze a Startup Website")
    company_url = st.text_input("Paste URL")
    if st.button("Analyze"):
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
            st.success(f"✅ {parsed.get('company')} added to your leads.")

elif choice == "View & Edit Leads":
    st.subheader("📋 View & Edit Leads")
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
        fit_columns_on_grid_load=True,
        height=600,
        key="editable_grid"
    )

    updated_df = grid_response["data"]
    if st.button("💾 Save Changes"):
        update_leads_bulk(updated_df)
        st.success("✅ Saved.")

st.set_page_config(page_title="🎯 LeadNavigator by InnHealthium", layout="wide")
st.title("🚀 LeadNavigator CRM")
st.caption("Your AI-powered tool to find, qualify, and track MedTech leads — smarter and faster.")

st.sidebar.image("https://media.giphy.com/media/l0MYB8Ory7Hqefo9a/giphy.gif", width=200)
menu = ["📤 Upload Leads", "🤖 Paste Website (AI)", "📝 Edit Leads"]
choice = st.sidebar.radio("What would you like to do?", menu)

if choice == "📤 Upload Leads":
    st.subheader("📁 Upload Leads via Excel")
    st.markdown("Just drag and drop your `.xlsx` file with columns like `company`, `summary`, `email`...")

    file = st.file_uploader("Choose your Excel file", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        st.success("✅ File loaded successfully!")

        for _, row in df.iterrows():
            score = calculate_score(row['summary'], row['growth_phase'])
            data = (
                row['company'], row['website'], row['email'], row['contact_person'],
                row['summary'], row['growth_phase'], score, "", ""
            )
            insert_lead(data)

        st.balloons()
        st.success("🎉 Leads imported and scored!")

elif choice == "🤖 Paste Website (AI)":
    st.subheader("🌐 Paste a Startup Homepage")
    st.markdown("Let AI do the work. We'll read the homepage and auto-extract key info and score it 🔍")

    company_url = st.text_input("Paste a company URL (e.g. https://neuroai.tech)")

    if st.button("🧠 Analyze with AI"):
        with st.spinner("Reading, thinking, and scoring..."):
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
            st.warning("🤔 GPT response couldn't be parsed correctly.")
elif choice == "📝 Edit Leads":
    st.subheader("🛠 Edit Your Lead Database")
    st.markdown("Click any cell to edit. Don't forget to hit **Save Changes**!")

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
        height=600,
        theme="material",
        key="editable_grid"
    )

    updated_df = grid_response["data"]
    if st.button("💾 Save Changes"):
        update_leads_bulk(updated_df)
        st.success("✅ All changes saved!")
