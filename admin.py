# admin.py
import streamlit as st
from utils import add_user, delete_user, get_user, update_user_rights

# Custom CSS to center the content and remove extra padding
st.markdown(
    """
    <style>
    
    .st-emotion-cache-bm2z3a {
    /* display: flex; */
    flex-direction: column;
    width: 100%;
    overflow: auto;
    -webkit-box-align: center;
    align-items: center;
}


.st-emotion-cache-ocqkz7 {
    display: flex;
    /* flex-wrap: wrap; */
    -webkit-box-flex: 1;
    /* flex-grow: 1; */
    /* -webkit-box-align: stretch; */
    /* align-items: stretch; */
    gap: 40rem;
    padding-right: 2rem;
    padding-left: 6rem;
}
    </style>
    """,
    unsafe_allow_html=True
)

def show_admin_panel():
    st.title("Admin Panel - User Management")

    # Creating two columns for the layout
    col1, col2 = st.columns([2, 2])

    # Left Column: Update User and Delete User
    with col1:
        # Section to Update User Rights
        st.header("Update User Details")
        username_for_update = st.text_input("Username for Update", key="username_for_update")

        if st.button("Load User for Update", key="load_user_button"):
            user = get_user(username_for_update)
            if user:
                st.session_state['user_to_update'] = user  # Store user details in session state
                st.success(f"User '{username_for_update}' loaded for update.")
            else:
                st.error("User not found.")
                st.session_state.pop('user_to_update', None)

        # If user is loaded, display fields with current values
        if 'user_to_update' in st.session_state:
            user = st.session_state['user_to_update']

            # Update rights checkboxes with unique keys
            update_access_internal_store_transfer = st.checkbox(
                "Access to Internal Store Transfer", 
                value=user.get('can_access_internal_store_transfer', False), 
                key="update_user_internal_store"
            )
            update_access_assortment = st.checkbox(
                "Access to Assortment", 
                value=user.get('can_access_assortment', False), 
                key="update_user_assortment"
            )
            update_access_ip = st.checkbox(
                "Access to IP", 
                value=user.get('can_access_ip', False), 
                key="update_user_ip"
            )

            if st.button("Update User Details"):
                try:
                    updated_rights = {
                        "internal_store_transfer": update_access_internal_store_transfer,
                        "assortment": update_access_assortment,
                        "ip": update_access_ip
                    }
                    update_user_rights(username_for_update, updated_rights)
                    st.success(f"User '{username_for_update}' details updated successfully.")
                    st.session_state.pop('user_to_update')  # Clear the loaded user after update
                except Exception as e:
                    st.error(f"An error occurred while updating the user details: {e}")

        # Section to Delete a User
        st.header("Delete User")
        username_to_delete = st.text_input("Username to Delete")
        if st.button("Delete User"):
            try:
                delete_user(username_to_delete)
                st.success(f"User '{username_to_delete}' deleted successfully.")
            except Exception as e:
                st.error(f"An error occurred while deleting the user: {e}")

    # Right Column: Add User
    with col2:
        # Section to Add a New User
        st.header("Add New User")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        new_role = st.selectbox("Role", ["admin", "user"])

        # User Rights Checkboxes with unique keys
        access_internal_store_transfer = st.checkbox("Access to Internal Store Transfer", key="new_user_internal_store")
        access_assortment = st.checkbox("Access to Assortment", key="new_user_assortment")
        access_ip = st.checkbox("Access to IP", key="new_user_ip")

        if st.button("Add User"):
            if new_username and new_password:
                rights = {
                    "internal_store_transfer": access_internal_store_transfer,
                    "assortment": access_assortment,
                    "ip": access_ip
                }
                try:
                    add_user(new_username, new_password, new_role, rights=rights)
                    st.success(f"User '{new_username}' added successfully with assigned rights.")
                    st.write("Assigned rights:", rights)  # Debugging assigned rights
                except Exception as e:
                    st.error(f"An error occurred while adding the user: {e}")
            else:
                st.error("Username and password are required to add a user.")

# Call the function to display the admin panel
#  show_admin_panel()
