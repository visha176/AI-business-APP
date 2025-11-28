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


# ---------- NAVBAR USING SESSION STATE ONLY ----------
def fixed_navbar(page_names):
    current = st.session_state.get("selected_page", "Home 🏠")

    st.markdown(
        """
        <style>
        .top-nav {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 60px;
            background: #000000cc;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding: 0 25px;
            gap: 25px;
            z-index: 9999;
        }
        .top-nav button {
            background-color: transparent;
            border: none;
            font-size: 17px;
            color: white;
            cursor: pointer;
        }
        .top-nav button.active {
            color: #ffcc00;
            font-weight: bold;
        }
        .block-container { padding-top: 90px !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='top-nav'>", unsafe_allow_html=True)
    for name in page_names:
        active = (name == current)
        button_class = "active" if active else ""
        if st.button(
            f"{ICONS.get(name,'')} {name}",
            key=f"nav_{name}",
            help=name
        ):
            st.session_state["selected_page"] = name
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ---------- ROUTER ----------
PAGES = get_private_pages() if st.session_state.get("logged_in") else PUBLIC_PAGES

if st.session_state.get("logged_in") and "Login 🔑" in PAGES:
    del PAGES["Login 🔑"]

fixed_navbar(list(PAGES.keys()))

selected = st.session_state.get("selected_page", "Home 🏠")
page_handler = PAGES[selected]
page_handler()
