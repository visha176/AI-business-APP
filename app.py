# app.py
import streamlit as st

# pages
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
    "selected_page": "home",   # use slug, not emoji
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# safety: if selected_page somehow holds old emoji, map it
legacy_map = {
    "Home 🏠": "home",
    "Home": "home",
    "Contact 📞": "contact",
    "Contact": "contact",
    "Login 🔑": "login",
    "Login": "login",
    "Internal Store Transfer📦": "transfer",
    "Admin Panel 🛠️": "admin",
    "Logout 🚪": "logout",
}
sel = st.session_state.get("selected_page")
if sel in legacy_map:
    st.session_state["selected_page"] = legacy_map[sel]

# LABELS for navbar
LABELS = {
    "home": "🏠 Home",
    "contact": "📞 Contact",
    "login": "🔑 Login",
    "transfer": "📦 Internal Store Transfer",
    "admin": "🛠️ Admin Panel",
    "logout": "🚪 Logout",
}

# ---------- LOGOUT ----------
def handle_logout():
    # DO NOT use clear() for safety, just reset what we need
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""
    st.session_state["rights"] = {}
    st.session_state["selected_page"] = "home"
    st.rerun()

# ---------- PAGE DEFINITIONS ----------
def get_private_pages():
    pages = {
        "home": home.show_home,
        "contact": contact.show_contact,
    }

    # internal store transfer
    if st.session_state.rights.get("internal_store_transfer", False):
        pages["transfer"] = network.show_Network

    # admin panel
    if st.session_state.role == "admin":
        pages["admin"] = admin.show_admin_panel

    pages["logout"] = handle_logout
    return pages


PUBLIC_PAGES = {
    "home": home.show_home,
    "contact": contact.show_contact,
    "login": login.show_login,
}

# ---------- NAVBAR ----------
def fixed_navbar(slugs):
    current = st.session_state.get("selected_page", "home")

    links_html = ""
    for slug in slugs:
        label = LABELS.get(slug, slug.title())
        active_class = "active" if slug == current else ""
        links_html += f"""
            <a class="nav-link {active_class}" href="/?page={slug}">
                {label}
            </a>
        """

    st.html(f"""
        <style>
            #top-nav {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 65px;
                background: #000;
                display: flex;
                justify-content: flex-end;
                align-items: center;
                gap: 24px;
                padding: 0 40px;
                z-index: 99999;
            }}
            .nav-link {{
                color: #ffffff;
                text-decoration: none;
                font-size: 18px;
                padding: 6px 12px;
                border-radius: 6px;
            }}
            .nav-link:hover {{
                background: #222;
                color: #ffcc00;
            }}
            .nav-link.active {{
                background: #333;
                color: #ffcc00;
                border-bottom: 2px solid #ffcc00;
            }}
            .block-container {{
                padding-top: 95px !important;
            }}
            header, div[data-testid="stToolbar"], div[data-testid="stDecoration"] {{
                display: none !important;
            }}
        </style>
        <div id="top-nav">
            {links_html}
        </div>
    """)

# ---------- ROUTER ----------

# 1. Decide which pages are available
if st.session_state.get("logged_in", False):
    PAGES = get_private_pages()
else:
    PAGES = PUBLIC_PAGES

# 2. Read ?page= from URL
page_query = st.query_params.get("page", "home")

# normalize and validate
page_query = page_query.lower()
if page_query not in PAGES:
    page_query = "home"

st.session_state["selected_page"] = page_query

# 3. Render navbar
fixed_navbar(list(PAGES.keys()))

# 4. Render selected page
PAGES[st.session_state["selected_page"]]()
