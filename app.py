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

# ---------- SESSION STATE DEFAULTS ----------
defaults = {
    "logged_in": False,
    "username": "",
    "role": "",
    "rights": {},
    "selected_page": "Home",
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)


# ---------- LOGOUT ----------
def handle_logout():
    st.session_state.clear()
    st.session_state["logged_in"] = False
    st.session_state["selected_page"] = "Home"
    st.rerun()


# ---------- PRIVATE & PUBLIC PAGES ----------
def get_private_pages():
    pages = {
        "Home": home.show_home,
        "Contact": contact.show_contact,
    }

    if st.session_state.rights.get("internal_store_transfer", False):
        pages["Internal"] = network.show_Network

    if st.session_state.role == "admin":
        pages["Admin"] = admin.show_admin_panel

    pages["Logout"] = handle_logout
    return pages


PUBLIC_PAGES = {
    "Home": home.show_home,
    "Contact": contact.show_contact,
    "Login": login.show_login,
}

LABELS = {
    "Home": "🏠 Home",
    "Contact": "📞 Contact",
    "Login": "🔑 Login",
    "Logout": "🚪 Logout",
    "Internal": "📦 Internal Store Transfer",
    "Admin": "🛠 Admin Panel",
}


# ---------- NAVBAR ----------
def fixed_navbar(page_names):
    current = st.session_state.get("selected_page", "Home")

    nav = ""
    for page in page_names:
        label = LABELS.get(page, page)
        active = "active" if page == current else ""
        nav += f"""
        <button class="nav-btn {active}" onclick="window.location.href='/?page={page}'">
            {label}
        </button>
        """

    st.markdown(f"""
    <style>
        #top-nav {{
            position: fixed; top: 0; left: 0;
            width: 100%; height: 65px;
            background: black;
            display: flex; align-items: center; justify-content: flex-end;
            padding: 0 40px; gap: 22px;
            z-index: 99999;
        }}
        .nav-btn {{
            background: none; border: none; color: white;
            font-size: 18px; cursor: pointer;
        }}
        .nav-btn:hover {{ color: #ffcc00; }}
        .active {{ color: #ffcc00; font-weight: bold; }}
        .block-container {{ padding-top: 95px !important; }}
        header, div[data-testid="stToolbar"], div[data-testid="stDecoration"] {{
            display: none !important;
        }}
    </style>

    <div id="top-nav">{nav}</div>
    """, unsafe_allow_html=True)


# ---------- ROUTER & PAGE SELECTION ----------
page_query = st.query_params.get("page")

if st.session_state.get("logged_in"):
    PAGES = get_private_pages()
else:
    PAGES = PUBLIC_PAGES

if page_query in PAGES:
    st.session_state["selected_page"] = page_query

fixed_navbar(list(PAGES.keys()))

PAGES[st.session_state["selected_page"]]()
