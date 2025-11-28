import streamlit as st
from urllib.parse import quote, unquote

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


# ---------- LOGIN HANDLING ----------
def handle_login(username, password):
    user = get_user(username, password)
    if not user:
        return False

    st.session_state["logged_in"] = True
    st.session_state["username"] = user["username"]
    st.session_state["user_id"] = user.get("id")
    st.session_state["role"] = user.get("role")

    st.session_state["rights"] = {
        "internal_store_transfer": user.get("can_access_internal_store_transfer", False),
        "assortment": user.get("can_access_assortment", False),
        "ip": user.get("can_access_ip", False),
    }

    # Force landing page after login
    st.session_state["selected_page"] = "Home 🏠"

    st.rerun()
    return True


def handle_logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

    st.session_state["logged_in"] = False
    st.session_state["selected_page"] = "Home 🏠"
    st.rerun()


# ---------- PAGE MAP ----------
def get_private_pages():
    pages = {
        "Home 🏠": home.show_home,
        "Contact 📞": contact.show_contact,
    }

    if st.session_state.rights.get("internal_store_transfer"):
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

ICONS = {
    "Home 🏠": "🏠",
    "Contact 📞": "📞",
    "Login 🔑": "🔑",
    "Logout 🚪": "🚪",
    "Internal Store Transfer📦": "📦",
    "Admin Panel 🛠️": "🛠️",
}


# ---------- NAVBAR ----------
def fixed_navbar(page_names):
    current = st.session_state.get("selected_page", "Home 🏠")

    links_html = []
    for name in page_names:
        href = f"?page={quote(name, safe='')}"
        active = (name == current)
        color = "#ffcc00" if active else "#ffffff"

        links_html.append(
            f"<a href='{href}' style='color:{color};text-decoration:none;font-size:17px'>"
            f"{ICONS.get(name, '')} {name}</a>"
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
                color: #fff;
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
            header, div[data-testid="stToolbar"], div[data-testid="stDecoration"] {{
                display: none !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------- ROUTER ----------
selected_url = st.query_params.get("page")

if selected_url:
    st.session_state["selected_page"] = unquote(selected_url)

# Define final pages list
PAGES = get_private_pages() if st.session_state.get("logged_in") else PUBLIC_PAGES

# Remove Login when logged in
if st.session_state.get("logged_in") and "Login 🔑" in PAGES:
    del PAGES["Login 🔑"]

# Render navbar
fixed_navbar(list(PAGES.keys()))

# Call selected page
selected = st.session_state["selected_page"]
page_handler = PAGES.get(selected, None)

if page_handler:
    page_handler()
else:
    home.show_home()
