"""
Step 1: Application Selection Page (Update Mode)

Allows users to search for and select an existing application to update.
"""

import streamlit as st
from services.asset_service import search_applications, load_existing_application_fields


def step1_select_existing_application(client):
    """Render the UI for selecting an existing application to update."""
    st.markdown("---")
    st.header("Step 1: Select Application to Update")
    st.write("Search for and select the Application you want to update.")
    
    # Search input
    search_term = st.text_input(
        "🔍 Search Applications",
        placeholder="Enter application name to search...",
        help="Type part of the application name to find it"
    )
    
    if search_term and len(search_term) >= 2:
        with st.spinner("Searching for applications..."):
            applications = search_applications(client, search_term)
        
        if applications:
            st.success(f"Found {len(applications)} application(s)")
            
            selected_app_display = st.selectbox(
                "Select Application to Update:",
                options=list(applications.keys()),
                help="Choose the application you want to modify"
            )
            
            if selected_app_display:
                selected_app = applications[selected_app_display]
                
                # Show application details
                with st.expander("📋 Application Details", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Name:** {selected_app.name}")
                        st.write(f"**Qualified Name:** {selected_app.qualified_name}")
                    with col2:
                        if hasattr(selected_app, 'app_id') and selected_app.app_id:
                            st.write(f"**App ID:** {selected_app.app_id}")
                        if hasattr(selected_app, 'description') and selected_app.description:
                            st.write(f"**Description:** {selected_app.description}")
                
                if st.button("✏️ Edit This Application", type="primary"):
                    with st.spinner("Loading application details..."):
                        # Load existing fields
                        existing_fields = load_existing_application_fields(client, selected_app.qualified_name)
                        
                        # Store the selected application and extract current details
                        st.session_state["selected_application"] = selected_app
                        st.session_state["asset_details"] = {
                            "qualified_name": selected_app.qualified_name,
                            "name": selected_app.name,
                            "app_id": getattr(selected_app, 'app_id', ''),
                            "connection_qualified_name": selected_app.connection_qualified_name,
                            "fields": existing_fields,
                            "create_new_connection": False,  # Always false for updates
                            "is_update": True  # Flag to indicate this is an update operation
                        }
                        st.success("Application loaded successfully!")
                        st.rerun()
        else:
            st.info("No applications found. Try a different search term.")
    elif search_term:
        st.warning("Please enter at least 2 characters to search.")
    else:
        st.info("💡 Enter a search term above to find existing applications.") 