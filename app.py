import streamlit as st

# pages
import pages.home as home
import pages.Network as network
import pages.contact as contact
import pages.login as login
import admin

from utils import get_user
from urllib.parse import quote, unquote

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

    st.session_state["selected_page"] = "Home 🏠"
    st.rerun()
    return True


def handle_logout():
    st.session_state.clear()
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


# ---------- FIXED NAVBAR (Original UI Restored) ----------
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

            div[data-testid="stToolbar"],
            div[data-testid="stDecoration"],
            header {{
                display: none !important;
            }}

            [data-testid="stAppViewContainer"] {{
                overflow-x: hidden !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------- ROUTER WITH SESSION + URL ----------
clicked_page = st.query_params.get("page")

if clicked_page:
    clicked_page = unquote(clicked_page)

    if st.session_state.get("logged_in", False):
        if clicked_page in get_private_pages():
            st.session_state["selected_page"] = clicked_page
    else:
        if clicked_page in PUBLIC_PAGES:
            st.session_state["selected_page"] = clicked_page

# Set dynamic pages list
if st.session_state.get("logged_in", False):
    PAGES = get_private_pages()
    if "Login 🔑" in PAGES:
        del PAGES["Login 🔑"]
else:
    PAGES = PUBLIC_PAGES

# Render navbar
fixed_navbar(list(PAGES.keys()))

# Render selected page
selected = st.session_state.get("selected_page", "Home 🏠")
page_handler = PAGES.get(selected, None)

if page_handler:
    page_handler()
else:
    home.show_home()
