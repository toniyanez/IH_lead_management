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


