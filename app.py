import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from io import BytesIO
from scraper import extract_info_from_url
from db import init_db, insert_lead, fetch_all_leads_df, update_leads_bulk

# Initialize Database
init_db()

# Set Page Configuration
st.set_page_config(page_title="LeadNavigator CRM", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
menu = ["Dashboard", "Upload Leads", "Add Lead Manually", "Edit Leads"]
choice = st.sidebar.radio("Go to", menu)

# Dashboard
if choice == "Dashboard":
    st.title("📊 Lead Dashboard")
    df = fetch_all_leads_df()

    # Display Summary Metrics
    total_leads = len(df)
    avg_score = df['Score'].mean()
    st.metric("Total Leads", total_leads)
    st.metric("Average Fit Score", f"{avg_score:.2f}")

    # Plot Growth Phase Distribution
    fig, ax = plt.subplots()
    df['Growth Phase'].value_counts().plot(kind='bar', ax=ax)
    ax.set_title("Growth Phase Distribution")
    ax.set_xlabel("Growth Phase")
    ax.set_ylabel("Number of Leads")
    st.pyplot(fig)

    # Display Data Table
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
                row['Company'], row['Website'], row['Email'], row['Contact Person'],
                row['Summary'], row['Growth Phase'], row['Score'], row['Comments'], row['Next Action']
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
            with st.spinner("Extracting information from website..."):
                ai_data = extract_info_from_url(website)
                if ai_data:
                    company = ai_data.get('Company', company)
                    summary = ai_data.get('Summary', summary)
                    email = ai_data.get('Email', email)
                    growth_phase = ai_data.get('Growth Phase', growth_phase)
                    score = ai_data.get('Score', score)
                    comments = ai_data.get('Comments', comments)
        data = (company, website, email, contact_person, summary, growth_phase, score, comments, next_action)
        insert_lead(data)
        st.success(f"Lead for {company} added successfully!")

# Edit Leads
elif choice == "Edit Leads":
    st.title("📝 Edit Leads")
    df = fetch_all_leads_df()

    # Editable Data Table
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
        st.success("Changes saved successfully!")

    # Excel Export
    towrite = BytesIO()
    downloaded_file = updated_df.to_excel(towrite, encoding='utf-8', index=False, header=True)
    towrite.seek(0)
    st.download_button(
        label="Download data as Excel",
        data=towrite,
        file_name='leads_data.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Built with 💙 by InnHealthium")
