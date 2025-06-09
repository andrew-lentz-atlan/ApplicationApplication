"""
Step 2/3: Enrichment Page

Allows users to add enrichment details like descriptions, owners, and Atlan tags.
"""

import streamlit as st
from services.connection_service import get_users_and_groups, get_tags
from utils.session_state import is_update_mode, get_selected_application


def step2_enrich_asset(client):
    """Render the UI for step 2: Enriching the asset."""
    is_update = is_update_mode()
    
    st.markdown("---")
    if is_update:
        st.header("Step 3: Update Enrichment Details")
        st.write("Update optional details to enrich your application with more context.")
        selected_app = get_selected_application()
        if selected_app:
            st.info(f"Updating enrichment for: **{selected_app.name}**")
    else:
        st.header("Step 2: Add Enrichment Details")
        st.write("Add optional details to enrich your new asset with more context.")

    owners = get_users_and_groups(client)
    tags = get_tags(client)
    
    # Load existing enrichment data for updates
    if is_update:
        selected_app = get_selected_application()
        default_description = getattr(selected_app, 'description', '') if selected_app else ''
        # Note: Loading existing owners and tags would require additional API calls
        # For now, start with empty and let user add what they want
        default_owners = []
        default_tags = []
    else:
        default_description = ''
        default_owners = []
        default_tags = []

    with st.form("enrichment_form"):
        description = st.text_area(
            "Description", 
            value=default_description,
            help="A detailed description for your application asset."
        )
        selected_owners = st.multiselect(
            "Select Owners",
            options=list(owners.keys()),
            default=default_owners,
            help="Select the users or groups that own this asset.",
        )
        selected_tags = st.multiselect(
            "Select Atlan Tags",
            options=list(tags.keys()),
            default=default_tags,
            help="Select the Atlan tags (classifications) to apply to this asset.",
        )

        # Navigation Buttons
        cols = st.columns(2)

        go_back = cols[0].form_submit_button("Go Back", use_container_width=True)
        
        button_text = "Next: Define Relationships" if not is_update else "Next: Update Relationships"
        proceed = cols[1].form_submit_button(
            button_text, use_container_width=True, type="primary"
        )

        if go_back:
            del st.session_state["asset_details"]
            st.rerun()

        elif proceed:
            st.session_state.enrichment_details = {
                "description": description,
                "owner_users": [
                    owners[o].username for o in selected_owners if "User" in o
                ],
                "owner_groups": [
                    owners[o].alias for o in selected_owners if "Group" in o
                ],
                "tag_names": selected_tags,
            }
            st.rerun() 