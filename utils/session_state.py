"""
Session state utility functions for managing workflow state.
"""

import streamlit as st
from config.settings import PERSISTENT_SESSION_KEYS


def clear_workflow_state():
    """Clear workflow-related session state while preserving connection details."""
    for key in list(st.session_state.keys()):
        if key not in PERSISTENT_SESSION_KEYS:
            del st.session_state[key]


def initialize_application_fields():
    """Initialize application fields in session state if not already present."""
    if "application_fields" not in st.session_state:
        # Check if we're in update mode and have existing fields
        if (st.session_state.get("asset_details", {}).get("is_update", False) and 
            "asset_details" in st.session_state):
            st.session_state.application_fields = st.session_state["asset_details"]["fields"]
        else:
            st.session_state.application_fields = []


def get_operation_type():
    """Get the current operation type (create or update)."""
    return st.session_state.get("operation_type")


def is_update_mode():
    """Check if we're in update mode."""
    return st.session_state.get("asset_details", {}).get("is_update", False)


def get_selected_application():
    """Get the currently selected application for update mode."""
    return st.session_state.get("selected_application")


def get_asset_details():
    """Get the current asset details."""
    return st.session_state.get("asset_details", {})


def get_enrichment_details():
    """Get the current enrichment details."""
    return st.session_state.get("enrichment_details", {})


def get_search_results():
    """Get the current search results."""
    return st.session_state.get("search_results", {})


def set_search_results(results):
    """Set search results in session state."""
    st.session_state.search_results = results


def initialize_search_results():
    """Initialize search results if not present."""
    if "search_results" not in st.session_state:
        st.session_state.search_results = {} 