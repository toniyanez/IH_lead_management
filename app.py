import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from db import init_db, insert_lead, fetch_all_leads_df, update_leads_bulk
from lead_utils import calculate_score
from scraper import extract_info_from_url

# Initialize database
init_db()

# Set page configuration with InnHealthium branding
st.set_page_config(
    page_title="LeadNavigator by InnHealthium",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add InnHealthium logo and title
st.image("innhealthium_logo.png", width=200)
st.title("LeadNavigator CRM")
st.caption("Empowering MedTech innovators with AI-driven lead management.")

# Sidebar menu
st.sidebar.image("innhealthium_logo.png", width=150)
menu = ["Upload Leads", "Analyze Website (AI)", "View & Edit Leads"]
choice = st.sidebar.radio("Navigate", menu)

# Define primary color for buttons and accents
primary_color = "#1A73E8"  # InnHealthium blue

# Upload Leads Section
if choice == "Upload Leads":
    st.subheader("📁 Upload Leads via Excel")
    st.markdown("Upload your `.xlsx` file containing lead information.")

    file = st.file_uploader("Choose an Excel file", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        st.success("File loaded successfully!")

        for _, row in df.iterrows():
            score = calculate_score(row['summary'], row['growth_phase'])
            data = (
                row['company'], row['website'], row['email'], row['contact_person'],
                row['summary'], row['growth_phase'], score, "", ""
            )
            insert_lead(data)

        st.balloons()
        st.success("Leads imported and scored!")

# Analyze Website (AI) Section
elif choice == "Analyze Website (AI)":
    st.subheader("🌐 Analyze a Startup Website")
    st.markdown("Let AI extract key information and score the lead.")

    company_url = st.text_input("Enter the company's website URL")

    if st.button("Analyze", key="analyze_button"):
        with st.spinner("Analyzing the website..."):
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
            st.success(f"{parsed.get('company')} added to your leads!")
        else:
            st.warning("Could not parse the AI response.")

# View & Edit Leads Section
elif choice == "View & Edit Leads":
    st.subheader("🛠 View & Edit Leads")
    st.markdown("Edit your leads directly in the table below.")

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
        theme="blue",  # Matching InnHealthium's color scheme
        key="editable_grid"
    )

    updated_df = grid_response["data"]
    if st.button("Save Changes", key="save_button"):
        update_leads_bulk(updated_df)
        st.success("Changes saved successfully!")

# Footer
st.markdown("---")
st.caption("© 2025 InnHealthium | Transforming healthcare innovation.")

