import time
import streamlit as st
from utils import get_user  # verify_password removed, no longer needed

def _safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def login_page():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # If already logged in, show status and exit
    if st.session_state.get("logged_in", False):
        st.success(f"✅ Already logged in as {st.session_state['username']}")
        return

    if st.button("Login"):
        user = get_user(username, password)

        if user:
            # Store login session state
            st.session_state["logged_in"] = True
            st.session_state["username"] = user.get("username", "")
            st.session_state["user_id"] = user.get("id")
            st.session_state["role"] = user.get("role", "")

            # ✔ Ensure rights exist so pages stay visible
            st.session_state["rights"] = {
            "internal_store_transfer": True,   # FORCE ENABLE ACCESS TEMPORARILY
            "assortment": True,
            "ip": True,
        }


            # Debug temporary check - remove later
            st.write("DEBUG RIGHTS:", st.session_state["rights"])

            # 🎯 Redirect to Internal Store Transfer
            st.session_state["selected_page"] = "Internal Store Transfer📦"

            st.success("🎉 Login successful! Redirecting...")
            time.sleep(0.8)
            _safe_rerun()

        else:
            st.error("❌ Invalid username or password")


def show_login():
    st.markdown("""
        <style>
            .stApp{
                background-image:url("https://images.unsplash.com/photo-1526666923127-b2970f64b422?q=80&w=2072&auto=format&fit=crop");
                background-size:cover;
                color:white;
            }
            h1, h2 {
                font-family:"Source Sans Pro",sans-serif;
                color:white;
            }
            .st-emotion-cache-5qfegl {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-weight: 400;
                padding: 0.25rem 0.75rem;
                border-radius: 0.5rem;
                min-height: 2.5rem;
                margin: 0px;
                line-height: 1.6;
                text-transform: none;
                font-size: inherit;
                font-family: inherit;
                color: inherit;
                width: 100%;
                cursor: pointer;
                user-select: none;
                background-color: rgb(0 0 0);
            }
            h1{font-weight:700;}
            h2{font-weight:600;}
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 0.5, 1])

    with col1:
        if not st.session_state.get("logged_in"):
            login_page()
        else:
            st.success(f"Logged in as: {st.session_state['username']}")

    with col3:
        st.header("Welcome")
        st.write("Welcome to the Internal Store Transfer and Assortment Management App!")
        st.write("Upload your Excel file to manage assortments and streamline internal store transfers.")


# ⏺ ENTRY POINT
if not st.session_state.get("logged_in"):
    show_login()
else:
    st.success(f"Logged in as {st.session_state['username']}")

