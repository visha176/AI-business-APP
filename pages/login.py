import time
import streamlit as st
from utils import get_user, verify_password

def _safe_rerun():
    """Works on both new and old Streamlit versions."""
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()  # for older versions

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.session_state.get("logged_in"):
        st.success(f"✅ Already logged in as {st.session_state['username']}")
        return

    if st.button("Login"):
        user = get_user(username)
        if user and verify_password(password, user["password"]):
            st.session_state["logged_in"] = True
            st.session_state["username"] = user["username"]
            st.session_state["user_id"] = user.get("id")
            st.session_state["role"] = user.get("role")
            st.session_state["rights"] = {
                "internal_store_transfer": user.get("can_access_internal_store_transfer", False),
                "assortment": user.get("can_access_assortment", False),
                "ip": user.get("can_access_ip", False),
            }
            st.success("✅ Login successful! Redirecting...")
            time.sleep(0.8)
            _safe_rerun()
        else:
            st.error("❌ Invalid username or password.")

def show_login():
    st.markdown("""
        <style>
            .stApp{background-image:url("https://images.unsplash.com/photo-1526666923127-b2970f64b422?q=80&w=2072&auto=format&fit=crop");background-size:cover;color:white;}
            .st-emotion-cache-ocqkz7{display:flex;flex-wrap:wrap;flex-grow:1;align-items:stretch;gap:1rem;margin-left:-25rem;width:1600px;padding:100px;}
            h1,h2{font-family:"Source Sans Pro",sans-serif;color:white;margin:0;padding:1.25rem 0 1rem;line-height:1.2;}
            h1{font-weight:700;} h2{font-weight:600;letter-spacing:-.005em;}
            .st-emotion-cache-1whx7iy p{font-size:19px;font-family:"Source Sans Pro";color:white;}
            .st-emotion-cache-1vt4y43{background-color:rgb(31,55,154);border:1px solid rgba(49,51,63,.2);}
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 0.5, 1])
    with col1:
        if not st.session_state.get("logged_in"):
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            login_page()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success(f"✅ Logged in as {st.session_state['username']}")

    with col2:
        st.markdown('<div class="gap"></div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="welcome-container">', unsafe_allow_html=True)
        st.header("Welcome")
        st.write("Welcome to the Internal Store Transfer and Assortment Management App!")
        st.write("Upload your Excel file to manage assortments and streamline internal store transfers.")
        st.markdown('</div>', unsafe_allow_html=True)

# Entry
if not st.session_state.get("logged_in"):
    show_login()
else:
    st.success(f"✅ You are logged in as {st.session_state['username']}")
