import streamlit as st
from urllib.parse import quote, unquote

import pages.home as home
import pages.Network as network
import pages.contact as contact
import pages.login as login
import admin

# ---------- CONFIG ----------
st.set_page_config(page_title="AI Business App", layout="wide")

# ---------- SESSION DEFAULTS ----------
defaults = {
    "logged_in": False,
    "username": "",
    "role": "",
    "rights": {},
    "selected_page": "home",   # internal keys only
}

for key, value in defaults.items():
    st.session_state.setdefault(key, value)

# ---------- LOGOUT ----------
def handle_logout():
    for key in ["logged_in", "username", "role", "rights", "user_id"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state["selected_page"] = "home"
    st.rerun()


# ---------- PAGE MAPS ----------
def get_private_pages():
    pages = {
        "home": home.show_home,
        "contact": contact.show_contact,
    }

    if st.session_state.rights.get("internal_store_transfer", True):
        pages["internal_store_transfer"] = network.show_Network

    if st.session_state.role == "admin":
        pages["admin_panel"] = admin.show_admin_panel

    pages["logout"] = handle_logout
    return pages


PUBLIC_PAGES = {
    "home": home.show_home,
    "contact": contact.show_contact,
    "login": login.show_login,
}

DISPLAY_NAMES = {
    "home": "Home 🏠",
    "contact": "Contact 📞",
    "login": "Login 🔑",
    "logout": "Logout 🚪",
    "internal_store_transfer": "Internal Store Transfer 📦",
    "admin_panel": "Admin Panel 🛠️",
}


# ---------- FIXED NAVBAR ----------
def fixed_navbar(page_names):
    current = st.session_state.get("selected_page", "home")
    links_html = []

    for name in page_names:
        href = f"?page={quote(name, safe='')}"
        active = (name == current)
        color = "#ffcc00" if active else "#ffffff"
        display = DISPLAY_NAMES.get(name, name)

        links_html.append(
            f"<a href='{href}' style='color:{color};text-decoration:none;font-size:17px'>{display}</a>"
        )

    st.markdown(
        f"""
        <div id="fixedNav">{' '.join(links_html)}</div>
        <style>
            #fixedNav {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 70px;
                background: #000;
                display: flex;
                justify-content: flex-end;
                align-items: center;
                gap: 36px;
                padding: 0 40px;
                z-index: 9999;
                box-shadow: 0 2px 10px rgba(0,0,0,.5);
            }}
            .block-container {{
                padding-top: 100px !important;
            }}
            div[data-testid="stToolbar"], div[data-testid="stDecoration"], header {{
                display: none !important;
            }}
            [data-testid="stAppViewContainer"] {{
                overflow-x: hidden !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---------- ROUTER ----------
raw_page = st.query_params.get("page")
selected_page = unquote(raw_page) if raw_page else st.session_state.get("selected_page", "home")

if selected_page != st.session_state["selected_page"]:
    st.session_state["selected_page"] = selected_page

PAGES = get_private_pages() if st.session_state["logged_in"] else PUBLIC_PAGES

# Draw navbar
fixed_navbar(list(PAGES.keys()))

# Render active page
if selected_page == "logout":
    handle_logout()
elif selected_page in PAGES:
    PAGES[selected_page]()
else:
    PAGES["home"]()



