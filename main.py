"""
Atlan Asset Builder - Main Entry Point

A Streamlit application for creating and updating Application assets in Atlan.

Usage:
    streamlit run main.py

Features:
- Create new Application assets with ApplicationField sub-assets
- Update existing Application assets
- Add enrichment details (descriptions, owners, tags)
- Define relationships and lineage
- Automatic client reconnection handling
"""

import streamlit as st
from ui.components.sidebar import render_sidebar
from ui.pages.operation_selection import step0_choose_operation
from ui.pages.application_selection import step1_select_existing_application
from ui.pages.asset_definition import step1_define_asset
from ui.pages.enrichment import step2_enrich_asset
from ui.pages.relationships import step3_relationships_and_submit
from utils.session_state import clear_workflow_state


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Atlan Asset Builder",
        page_icon="🤖",
        layout="wide",
    )
    
    st.title("🤖 Atlan Asset Builder")

    # Render sidebar for Atlan connection
    client = render_sidebar()
    
    if client is None:
        st.info("Please connect to your Atlan instance using the sidebar to begin.")
        return

    # State-based navigation through the workflow
    if "operation_type" not in st.session_state:
        step0_choose_operation()
    elif st.session_state.get("operation_type") == "Update an existing Application" and "selected_application" not in st.session_state:
        step1_select_existing_application(client)
    elif "asset_details" not in st.session_state:
        step1_define_asset(client)
    elif "enrichment_details" not in st.session_state:
        step2_enrich_asset(client)
    else:
        step3_relationships_and_submit(client)

    # Always show start over button at the bottom
    st.markdown("---")
    if st.button("🔄 Start Over"):
        clear_workflow_state()
        st.rerun()


if __name__ == "__main__":
    main() 