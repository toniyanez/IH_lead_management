import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from db import init_db, insert_lead, fetch_all_leads_df, update_leads_bulk
from lead_utils import calculate_score
from scraper import scrape_leads_from_url

st.set_page_config(page_title="LeadNavigator", layout="wide")
init_db()

st.title("🚀 InnHealthium - LeadNavigator")

menu = ["Upload Excel", "Scrape Website", "View & Edit Leads"]
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
        st.success("Leads uploaded successfully!")

elif choice == "Scrape Website":
    url = st.text_input("Enter URL")
    if st.button("Scrape"):
        leads = scrape_leads_from_url(url)
        for lead in leads:
            insert_lead(lead)
        st.success("Web leads scraped and stored!")

elif choice == "View & Edit Leads":
    st.subheader("📋 Edit Leads Inline")
    df = fetch_all_leads_df()

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination()
    gb.configure_default_column(editable=True, groupable=True)
    gb.configure_column("ID", editable=False)
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MANUAL,
        height=600,
        fit_columns_on_grid_load=True,
        editable=True,
        key='editable_grid'
    )

    updated_df = grid_response['data']

    if st.button("💾 Save Changes"):
        update_leads_bulk(updated_df)
        st.success("✅ Lead updates saved.")
menu = ["Upload Excel", "Scrape Website", "Paste URL (AI)", "View & Edit Leads"]
elif choice == "Paste URL (AI)":
    st.subheader("🔗 Analyze a Website via AI")
    company_url = st.text_input("Paste a startup homepage URL")

    if st.button("Analyze and Add Lead"):
        with st.spinner("Reading site and asking GPT..."):
            result = extract_info_from_url(company_url)

        st.code(result)

        # Try to parse result into variables (simple parser)
        lines = result.split("\n")
        parsed = {}
        for line in lines:
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
            st.success(f"✅ {parsed.get('company')} was added to your leads.")
        else:
            st.warning("⚠️ Could not parse response. Please check format.")

