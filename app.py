import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from io import BytesIO
from scraper import extract_info_from_url
from db import init_db, insert_lead, fetch_all_leads_df, update_leads_bulk

init_db()

st.set_page_config(page_title="LeadNavigator CRM", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
menu = ["Dashboard", "Upload Leads", "Add Lead Manually", "Edit Leads"]
choice = st.sidebar.radio("Go to", menu)

# Dashboard
if choice == "Dashboard":
    st.title("📊 Lead Dashboard")
    df = fetch_all_leads_df()

    if df.empty:
        st.warning("No leads available.")
    else:
        total_leads = len(df)
        avg_score = df['Score'].mean()
        st.metric("Total Leads", total_leads)
        st.metric("Average Fit Score", f"{avg_score:.2f}")

        fig, ax = plt.subplots()
        df['Growth_Phase'].value_counts().plot(kind='bar', ax=ax)
        ax.set_title("Growth Phase Distribution")
        ax.set_xlabel("Growth Phase")
        ax.set_ylabel("Number of Leads")
        st.pyplot(fig)

        st.subheader("Lead Details")
        AgGrid(df)

# Upload Leads
elif choice == "Upload Leads":
    st.title("📥 Upload Leads from Excel")
    file = st.file_uploader("Upload your Excel file", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            data = (
                row['Company'], row['Website'], row['Email'], row['Contact_Person'],
                row['Summary'], row['Growth_Phase'], row['Score'], row.get('Comments', ""), row.get('Next_Action', "")
            )
            insert_lead(data)
        st.success("Leads successfully uploaded!")

# Add Lead Manually
elif choice == "Add Lead Manually":
    st.title("➕ Add Lead Manually")
    with st.form(key='manual_lead_form'):
        company = st.text_input("Company Name")
        website = st.text_input("Website URL")
        email = st.text_input("Contact Email")
        contact_person = st.text_input("Contact Person")
        summary = st.text_area("Company Summary")
        growth_phase = st.selectbox("Growth Phase", ["Pre-seed", "Seed", "Series A", "Series B", "Series C", "Consolidation", "Expansion"])
        score = st.slider("Fit Score", 0, 100, 50)
        comments = st.text_area("Comments")
        next_action = st.text_input("Next Action")
        auto_fill = st.checkbox("Auto-fill using company website")
        submit_button = st.form_submit_button(label='Add Lead')

    if submit_button:
        if auto_fill and website:
            with st.spinner("Extracting info using AI..."):
                ai_data = extract_info_from_url(website)
                if 'error' not in ai_data:
                    company = ai_data.get("company", company)
                    summary = ai_data.get("summary", summary)
                    email = ai_data.get("email", email)
                    growth_phase = ai_data.get("growth_phase", growth_phase)
                    score = ai_data.get("score", score)
                    comments = ai_data.get("comments", comments)
                else:
                    st.error(ai_data['error'])

        data = (company, website, email, contact_person, summary, growth_phase, score, comments, next_action)
        insert_lead(data)
        st.success(f"Lead for {company} added!")

# Edit Leads
elif choice == "Edit Leads":
    st.title("📝 Edit Leads")
    df = fetch_all_leads_df()

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination()
    gb.configure_default_column(editable=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MANUAL,
        editable=True,
        height=600,
        theme="material"
    )

    updated_df = grid_response['data']
    if st.button("Save Changes"):
        update_leads_bulk(updated_df)
        st.success("Changes saved!")

    # Excel Export
    towrite = BytesIO()
    downloaded_file = updated_df.to_excel(towrite
