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

    st.markdown(
        """
        <style>
        #top-nav {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 65px;
            background: #000;
            display: flex;
            justify-content: flex-end;
            align-items: center;
            gap: 28px;
            padding: 0 30px;
            z-index: 9999;
        }
        .block-container { padding-top: 110px !important; }
        button.navbtn {
            background: none;
            color: white;
            border: none;
            font-size: 18px;
            cursor: pointer;
        }
        button.navbtn:hover { color: #ffcc00; }
        .active { color: #ffcc00; font-weight: bold; }
        div[data-testid="stToolbar"], div[data-testid="stDecoration"], header {display:none !important;}
        </style>
        <div id="top-nav">
        """,
        unsafe_allow_html=True
    )

    cols = st.columns(len(page_names))

    for i, name in enumerate(page_names):
        active = "active" if name == current else ""
        if cols[i].button(name, key=f"nav_{name}", help=name):
            st.session_state["selected_page"] = name
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ---------- ROUTER ----------
if st.session_state.get("logged_in"):
    PAGES = get_private_pages()
else:
    PAGES = PUBLIC_PAGES

fixed_navbar(list(PAGES.keys()))

selected_page = st.session_state.get("selected_page", "Home 🏠")
PAGES[selected_page]()
