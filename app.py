import streamlit as st

# pages
import pages.home as home
import pages.Network as network
import pages.contact as contact
import pages.login as login
import admin
from utils import get_user

# ---------- CONFIG ----------
st.set_page_config(page_title="AI Business App", layout="wide")

# ---------- SESSION DEFAULTS ----------
defaults = {
    "logged_in": False,
    "username": "",
    "role": "",
    "rights": {},
    "selected_page": "Home 🏠",
}

for k, v in defaults.items():
    st.session_state.setdefault(k, v)


# ---------- LOGOUT ----------
def handle_logout():
    st.session_state.clear()
    st.session_state["logged_in"] = False
    st.session_state["selected_page"] = "Home 🏠"
    st.rerun()


# ---------- PAGE DEFINITIONS ----------
def get_private_pages():
    pages = {
        "Home 🏠": home.show_home,
        "Contact 📞": contact.show_contact
    }

    if st.session_state.rights.get("internal_store_transfer", False):
        pages["Internal Store Transfer📦"] = network.show_Network

    if st.session_state.role == "admin":
        pages["Admin Panel 🛠️"] = admin.show_admin_panel

    pages["Logout 🚪"] = handle_logout
    return pages


PUBLIC_PAGES = {
    "Home 🏠": home.show_home,
    "Contact 📞": contact.show_contact,
    "Login 🔑": login.show_login,
}


# ---------- NAVBAR ----------
def fixed_navbar(page_names):
    current = st.session_state.get("selected_page", "Home 🏠")

    # Global styling for the nav row + buttons
    st.markdown(
        """
        <style>
        /* Make the first horizontal block (our nav) look like a top bar */
        div[data-testid="stHorizontalBlock"]:first-of-type {
            background-color: #000;
            padding: 10px 30px 5px 30px;
        }

        /* Remove extra top padding so content hugs the nav bar */
        .block-container {
            padding-top: 0px !important;
        }

        /* Style nav buttons */
        div[data-testid="stHorizontalBlock"]:first-of-type button {
            background-color: transparent !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: none !important;
            font-size: 17px;
        }

        /* Hover effect */
        div[data-testid="stHorizontalBlock"]:first-of-type button:hover {
            color: #ffcc00 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # This row becomes the "top bar"
    cols = st.columns(len(page_names))

    for i, name in enumerate(page_names):
        is_active = name == current
        label = f"⭐ {name}" if is_active else name  # simple active marker (optional)

        if cols[i].button(label, key=f"nav_{name}"):
            st.session_state["selected_page"] = name
            st.rerun()



# ---------- ROUTER ----------
if st.session_state.get("logged_in"):
    PAGES = get_private_pages()
else:
    PAGES = PUBLIC_PAGES

fixed_navbar(list(PAGES.keys()))

selected_page = st.session_state.get("selected_page", "Home 🏠")
PAGES[selected_page]()

