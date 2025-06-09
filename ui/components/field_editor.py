"""
Field editor component for managing ApplicationField assets.
"""

import streamlit as st


def add_field():
    """Callback to add a new blank field to the session state."""
    st.session_state.application_fields.append({
        "name": "", 
        "type": "", 
        "description": ""
    })


def remove_field(index):
    """Callback to remove a field from the session state at a given index."""
    if 0 <= index < len(st.session_state.application_fields):
        st.session_state.application_fields.pop(index)


def render_field_editor():
    """
    Render the field editor interface for ApplicationField assets.
    """
    st.subheader("Application Fields")
    st.write(
        "Add or remove fields that belong to this application. "
        "These will be created as `ApplicationField` assets."
    )

    # Render existing fields
    for i, field in enumerate(st.session_state.application_fields):
        # Show if this is an existing field
        field_header = f"**Field {i+1}**"
        if field.get("is_existing"):
            field_header += " *(Existing)*"
        
        st.markdown(field_header)
        cols = st.columns([3, 3, 4, 1])
        
        # Field inputs
        field["name"] = cols[0].text_input(
            "Field Name", 
            value=field.get("name", ""), 
            key=f"field_name_{i}"
        )
        field["type"] = cols[1].text_input(
            "Data Type", 
            value=field.get("type", ""), 
            key=f"field_type_{i}"
        )
        field["description"] = cols[2].text_input(
            "Description", 
            value=field.get("description", ""), 
            key=f"field_desc_{i}"
        )
        
        # Remove button (different behavior for existing vs new fields)
        if field.get("is_existing"):
            if cols[3].button(
                "❌",
                key=f"remove_field_{i}",
                help="Remove this existing field (will be deleted from Atlan).",
            ):
                field["mark_for_deletion"] = True
                remove_field(i)
        else:
            cols[3].button(
                "🗑️",
                key=f"remove_field_{i}",
                on_click=remove_field,
                args=(i,),
                help="Remove this field.",
            )
    
    # Add field button
    st.button(
        "Add Field", 
        on_click=add_field, 
        help="Add a new field to this application."
    )
    
    st.markdown("---") 