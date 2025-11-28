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
    "selected_page": "home",   # page slug, no emojis here
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# Map any old emoji names → new slugs (safety)
legacy_map = {
    "Home 🏠": "home",
    "Contact 📞": "contact",
    "Login 🔑": "login",
    "Internal Store Transfer📦": "transfer",
    "Admin Panel 🛠️": "admin",
    "Logout 🚪": "logout",
}
sel = st.session_state.get("selected_page")
if sel in legacy_map:
    st.session_state["selected_page"] = legacy_map[sel]

# -------- NAVBAR LABELS --------
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
    # Don't clear the whole session, just reset auth info
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

    # Internal Store Transfer page
    if st.session_state.rights.get("internal_store_transfer", False):
        pages["transfer"] = network.show_Network

    # Admin panel
    if st.session_state.role == "admin":
        pages["admin"] = admin.show_admin_panel

    pages["logout"] = handle_logout
    return pages


PUBLIC_PAGES = {
    "home": home.show_home,
    "contact": contact.show_contact,
    "login": login.show_login,
}

# ---------- NAVBAR (button-based, no <a href>) ----------
def fixed_navbar(slugs):
    current = st.session_state.get("selected_page", "home")

    # CSS for fixed black bar
    st.markdown(
        """
        <style>
        .top-nav-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 65px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding: 0 40px;
            gap: 24px;
            z-index: 9999;
        }
        .block-container {
            padding-top: 95px !important;  /* push content below bar */
        }
        header, div[data-testid="stToolbar"], div[data-testid="stDecoration"] {
            display: none !important;
        }
        /* Make navbar buttons look like links */
        button.nav-btn {
            background: none !important;
            border: none !important;
            font-size: 18px !important;
            padding: 6px 12px !important;
            border-radius: 6px !important;
        }
        button.nav-btn:hover {
            background: #222222 !important;
            color: #ffcc00 !important;
        }
        button.nav-btn-active {
            background: #333333 !important;
            color: #ffcc00 !important;
            border-bottom: 2px solid #ffcc00 !important;
        }
        .st-emotion-cache-1permvm {
    display: flex;
    gap: 1rem;
    width: 100%;
    flex-flow: row-reverse wrap;
    align-items: flex-start;
    justify-content: flex-start;
    overflow: visible;
    color: white;
}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Use a horizontal container for the nav buttons
    nav_area = st.container()
    with nav_area:
        cols = st.columns(len(slugs))
        for i, slug in enumerate(slugs):
            label = LABELS.get(slug, slug.title())
            is_active = (slug == current)
            btn_class = "nav-btn-active" if is_active else "nav-btn"
            if cols[i].button(label, key=f"nav_{slug}", help=label, type="secondary"):
                st.session_state["selected_page"] = slug
                st.rerun()

        # Inject a div so our CSS can hook into it
        st.markdown(
            """
            <script>
            const root = window.parent.document;
            const blocks = root.querySelectorAll('section.main div[data-testid="stHorizontalBlock"]');
            if (blocks.length > 0) {
                blocks[0].classList.add('top-nav-container');
            }
            </script>
            """,
            unsafe_allow_html=True,
        )

# ---------- ROUTER ----------

# 1. Decide which pages are available
if st.session_state.get("logged_in", False):
    PAGES = get_private_pages()
else:
    PAGES = PUBLIC_PAGES

# 2. Render navbar with the available pages
fixed_navbar(list(PAGES.keys()))

# 3. Decide which page to show based ONLY on session_state
selected = st.session_state.get("selected_page", "home")
if selected not in PAGES:
    selected = "home"
    st.session_state["selected_page"] = "home"

# 4. Render selected page
PAGES[selected]()





