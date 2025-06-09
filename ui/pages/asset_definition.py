"""
Step 1/2: Asset Definition Page

Allows users to define application details and manage ApplicationField assets.
"""

import streamlit as st
from pyatlan.model.enums import AtlanConnectorType
from services.connection_service import get_connections, get_api_connections
from ui.components.field_editor import render_field_editor
from utils.session_state import initialize_application_fields, is_update_mode, get_selected_application


def step1_define_asset(client):
    """Render the UI for step 1: Defining the application asset."""
    is_update = is_update_mode()
    
    # Initialize application fields
    initialize_application_fields()

    st.markdown("---")
    if is_update:
        st.header("Step 2: Update Application Details")
        st.write(
            "Modify the details of your Application asset. You can update existing fields or add new ones."
        )
        # Show which application we're updating
        selected_app = get_selected_application()
        if selected_app:
            st.info(f"Updating: **{selected_app.name}** (QN: {selected_app.qualified_name})")
    else:
        st.header("Step 1: Define Application Asset")
        st.write(
            "Define the core details of the Application asset you want to create below."
        )

    # Render field editor
    render_field_editor()
    
    # Main form for asset details
    with st.form("asset_form"):
        st.subheader("Application Details")
        
        # Handle connection setup (only for create mode)
        if not is_update:
            connections = get_connections(client)
            api_connections = get_api_connections(connections)
            
            connection_choice = st.radio(
                "Connection Setup",
                ("Use an existing connection", "Create a new connection"),
                horizontal=True,
                help="Choose an existing API-type connection or create a new one.",
            )

            connection_qn = None
            new_connection_name = None

            if connection_choice == "Use an existing connection":
                if not api_connections:
                    st.warning("No existing API connections found. Please create one.")
                else:
                    connection_options = {
                        f"{getattr(c.connector_name, 'value', 'Unknown')} - {c.name}": c 
                        for c in api_connections
                    }
                    selected_connection_display_name = st.selectbox(
                        "Select Connection",
                        options=list(connection_options.keys()),
                        help="Select the API connection under which this application will be created.",
                    )
                    if selected_connection_display_name:
                        connection_qn = connection_options[
                            selected_connection_display_name
                        ].qualified_name
            else:
                new_connection_name = st.text_input(
                    "New Connection Name",
                    help="Provide a name for the new API connection.",
                )
        else:
            # For updates, connection cannot be changed
            existing_connection_qn = st.session_state["asset_details"]["connection_qualified_name"]
            st.info(f"🔗 Connection: {existing_connection_qn} *(cannot be changed)*")
            connection_qn = existing_connection_qn
            new_connection_name = None

        # Application details form
        default_name = st.session_state.get("asset_details", {}).get("name", "")
        default_app_id = st.session_state.get("asset_details", {}).get("app_id", "")
        
        application_name = st.text_input(
            "Application Name", 
            value=default_name,
            help="Enter a unique name for your application."
        )
        application_app_id = st.text_input(
            "Application ID (Optional)",
            value=default_app_id,
            help="Enter the ID of this application in the source system, if any.",
        )

        button_text = "Next: Add Enrichment Details" if not is_update else "Next: Update Enrichment Details"
        submitted = st.form_submit_button(button_text)

        if submitted:
            if not application_name:
                st.error("Application Name is a required field.")
                return
            
            # Validation only for create mode
            if not is_update:
                if (
                    connection_choice == "Create a new connection"
                    and not new_connection_name
                ):
                    st.error("New Connection Name is required when creating a new connection.")
                    return
                if connection_choice == "Use an existing connection" and not connection_qn:
                    st.error("You must select an existing connection.")
                    return

            # Update or create asset details
            asset_details = {
                "connection_qualified_name": connection_qn,
                "name": application_name,
                "app_id": application_app_id,
                "fields": st.session_state.application_fields,
                "is_update": is_update,
            }
            
            # Add create-specific fields
            if not is_update:
                asset_details.update({
                    "create_new_connection": connection_choice == "Create a new connection",
                    "new_connection_name": new_connection_name,
                })
            else:
                # Add update-specific fields
                asset_details.update({
                    "qualified_name": st.session_state["asset_details"]["qualified_name"],
                    "create_new_connection": False,
                })
            
            st.session_state.asset_details = asset_details
            st.rerun() 