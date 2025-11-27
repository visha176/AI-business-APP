import streamlit as st
from urllib.parse import quote, unquote

# pages
import pages.home as home
import pages.Network as network
import pages.contact as contact
import pages.login as login
import admin

import streamlit as st
from utils import get_user
from urllib.parse import quote, unquote

# ---------- CONFIG ----------
st.set_page_config(page_title="AI Business App", layout="wide")

# ---------- SESSION ----------
defaults = {
    "logged_in": False,
    "username": "",
    "role": "",
    "rights": {},
    "selected_page": "Home 🏠",
}

for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ---------- AUTH ----------
def handle_login():
    user = get_user(st.session_state["username"])
    if user:
        st.session_state.logged_in = True
        st.session_state.username = user["username"]
        st.session_state.user_id = user["id"]       # keep this
        st.session_state.role = user["role"]
        st.session_state.rights = {
            "internal_store_transfer": user.get("can_access_internal_store_transfer", False)
        }

        if "selected_page" not in st.session_state:
            st.session_state["selected_page"] = "Home 🏠"

        st.rerun()


def handle_logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

    st.session_state["logged_in"] = False
    st.session_state["selected_page"] = "Home 🏠"
    st.rerun()


# ---------- PAGE MAPS ----------
def get_private_pages():
    pages = {
        "Home 🏠": home.show_home,
        "Contact 📞": contact.show_contact,
        "Internal Store Transfer📦": network.show_Network,   # Always available
    }

    # Admin page only for admin
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


# ---------- FIXED TOP NAV ----------
def fixed_navbar(page_names):
    current = st.query_params.get("page", st.session_state.get("selected_page", "Home 🏠"))

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


# ---------- ROUTER ----------
selected = unquote(
    st.query_params.get("page", st.session_state.get("selected_page", "Home 🏠"))
)

if selected != st.session_state.get("selected_page"):
    st.session_state["selected_page"] = selected

# Load routes
if st.session_state.get("logged_in", False):
    PAGES = get_private_pages()
else:
    PAGES = PUBLIC_PAGES

# Render navbar
fixed_navbar(list(PAGES.keys()))

# Route
if selected == "Logout 🚪":
    handle_logout()
elif selected in PAGES:
    PAGES[selected]()
else:
    if st.session_state.get("logged_in", False):
        home.show_home()
    else:
        login.show_login()



