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
        "Internal Store Transfer📦": network.show_Network,
    }

    if st.session_state.role == "admin":
        pages["Admin Panel 🛠️"] = admin.show_admin_panel

    pages["Logout 🚪"] = handle_logout
    return pages


PUBLIC_PAGES = {
    "Home 🏠": home.show_home,
    "Contact 📞": contact.show_contact,
    "Login 🔑": login.show_login,
}


# ---------- NAVBAR WITHOUT URL ----------
def fixed_navbar(page_names):
    current = st.session_state.get("selected_page", "Home 🏠")

    links_html = []
    for name in page_names:
        active = (name == current)
        color = "#ffcc00" if active else "#ffffff"

        # Use JS postMessage to change session page without changing URL
        links_html.append(
            f"""<a href="#" onclick="parent.postMessage({{'page':'{name}'}}, '*')" 
            style="color:{color};text-decoration:none;font-size:17px;">
            {name}</a>"""
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
            }}
            .block-container {{
                padding-top: 100px !important;
            }}
            div[data-testid="stToolbar"],
            div[data-testid="stDecoration"],
            header {{
                display: none !important;
            }}
        </style>

        <script>
            window.addEventListener("message", (event) => {{
                const page = event.data.page;
                if (page) {{
                    window.location.search = "";
                    window.parent.postMessage({{'setPage':page}}, "*");
                }}
            }});
        </script>
        """,
        unsafe_allow_html=True
    )


# ---------- PAGE HANDLER ----------
def load_page():
    if st.session_state.get("logged_in"):
        pages = get_private_pages()
    else:
        pages = PUBLIC_PAGES

    fixed_navbar(list(pages.keys()))

    page = st.session_state.get("selected_page", "Home 🏠")
    pages[page]()


load_page()
