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

    nav_items = ""
    for name in page_names:
        active_class = "active" if name == current else ""
        nav_items += f"""
            <button class="nav-btn {active_class}" onclick="window.location.href='/?page={name}'">
                {name}
            </button>
        """

    st.markdown(f"""
        <style>
            #top-nav {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 65px;
                background: #000000;
                display: flex;
                justify-content: flex-end;
                align-items: center;
                gap: 30px;
                padding: 0 40px;
                z-index: 9999;
            }}
            .nav-btn {{
                background: none;
                border: none;
                font-size: 18px;
                color: white;
                cursor: pointer;
            }}
            .nav-btn:hover {{
                color: #ffcc00;
            }}
            .active {{
                color: #ffcc00;
                font-weight: bold;
            }}
            .block-container {{
                padding-top: 100px !important;
            }}
            header, div[data-testid="stToolbar"], div[data-testid="stDecoration"] {{
                display: none !important;
            }}
        </style>
        <div id="top-nav">{nav_items}</div>
    """, unsafe_allow_html=True)


# ---------- ROUTER ----------
# Build pages available to user
if st.session_state.get("logged_in"):
    PAGES = get_private_pages()
else:
    PAGES = PUBLIC_PAGES

# Capture URL param
page_query = st.query_params.get("page")
if page_query and page_query in PAGES:
    st.session_state["selected_page"] = page_query

# Show navbar
fixed_navbar(list(PAGES.keys()))

# Render selected page
selected_page = st.session_state.get("selected_page", "Home 🏠")
PAGES[selected_page]()
