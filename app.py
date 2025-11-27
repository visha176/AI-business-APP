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
    "selected_page": "Home 🏠",
}

for key, value in defaults.items():
    st.session_state.setdefault(key, value)

# ---------- LOGOUT ----------
def handle_logout():
    st.session_state.clear()
    st.session_state["logged_in"] = False
    st.session_state["selected_page"] = "Home 🏠"
    st.rerun()

# ---------- PAGE MAPS ----------
def get_private_pages():
    pages = {
        "Home 🏠": home.show_home,
        "Contact 📞": contact.show_contact,
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

ICONS = {
    "Home 🏠": "🏠",
    "Contact 📞": "📞",
    "Login 🔑": "🔑",
    "Logout 🚪": "🚪",
    "Internal Store Transfer📦": "📦",
    "Admin Panel 🛠️": "🛠️",
}

# ---------- FIXED NAVBAR ----------
def fixed_navbar(page_names):
    current = st.session_state.get("selected_page", "Home 🏠")
    links_html = []

    for name in page_names:
        href = f"?page={quote(name, safe='')}"
        active = name == current
        color = "#ffcc00" if active else "#ffffff"

        links_html.append(
            f"<a href='{href}' style='color:{color};text-decoration:none;font-size:17px'>{ICONS.get(name,'')} {name}</a>"
        )

    st.markdown(
        f"""
        <div id="fixedNav">{' '.join(links_html)}</div>
        <style>
            #fixedNav {{
                position: fixed; top: 0; left: 0; width: 100%;
                height: 70px; background: #000; color: #fff;
                display: flex; justify-content: flex-end; align-items: center;
                gap: 36px; padding: 0 40px; z-index: 9999;
                box-shadow: 0 2px 10px rgba(0,0,0,.5);
            }}
            .block-container {{ padding-top: 100px !important; }}
            div[data-testid="stToolbar"],
            div[data-testid="stDecoration"],
            header {{ display:none !important; }}
            [data-testid="stAppViewContainer"] {{ overflow-x: hidden !important; }}
        </style>
        """, unsafe_allow_html=True,
    )

# ---------- ROUTER ----------
selected_page = unquote(st.query_params.get("page", st.session_state["selected_page"]))

if selected_page != st.session_state["selected_page"]:
    st.session_state["selected_page"] = selected_page

PAGES = get_private_pages() if st.session_state["logged_in"] else PUBLIC_PAGES

fixed_navbar(list(PAGES.keys()))

if selected_page == "Logout 🚪":
    handle_logout()
elif selected_page in PAGES:
    PAGES[selected_page]()
else:
    PAGES["Home 🏠"]()
