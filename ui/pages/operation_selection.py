"""
Step 0: Operation Selection Page

Allows users to choose between creating a new application or updating an existing one.
"""

import streamlit as st


def step0_choose_operation():
    """Render the UI for step 0: Choosing operation type."""
    st.markdown("---")
    st.header("Welcome to Atlan Asset Builder")
    st.write("What would you like to do today?")
    
    operation = st.radio(
        "Choose an operation:",
        ("Create a new Application", "Update an existing Application"),
        help="Select whether you want to create a brand new Application asset or update an existing one."
    )
    
    # Show info about each option
    if operation == "Create a new Application":
        st.info("🆕 **Create Mode**: You'll define a new Application asset from scratch, including fields, connections, and metadata.")
    else:
        st.info("✏️ **Update Mode**: You'll select an existing Application and modify its properties, add new fields, or update metadata.")
    
    if st.button("Continue ➡️", type="primary"):
        st.session_state["operation_type"] = operation
        st.rerun() 