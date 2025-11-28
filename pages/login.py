import time
import streamlit as st
from utils import get_user


def _safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def login_page():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # If already logged in, do not display form again
    if st.session_state.get("logged_in", False):
        st.success(f"✅ Already logged in as {st.session_state['username']}")
        return

    if st.button("Login"):
        user = get_user(username, password)

        if user:
            # SAVE USER SESSION STATE HERE
            st.session_state["logged_in"] = True
            st.session_state["username"] = user.get("username")
            st.session_state["user_id"] = user.get("id")
            st.session_state["role"] = user.get("role")

            st.session_state["rights"] = {
                "internal_store_transfer": user.get("can_access_internal_store_transfer", False),
                "assortment": user.get("can_access_assortment", False),
                "ip": user.get("can_access_ip", False),
            }

            # land on home after login
            st.session_state["selected_page"] = "Home 🏠"

            st.success("🎉 Login successful! Redirecting...")
            time.sleep(0.5)
            _safe_rerun()

        else:
            st.error("❌ Invalid username or password")


def show_login():
    st.markdown(
        """
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
            width: 100%;
            cursor: pointer;
            background-color: rgb(0 0 0);
        }
        h1{font-weight:700;}
        h2{font-weight:600;}
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 0.5, 1])

    with col1:
        login_page()

    with col3:
        st.header("Welcome")
        st.write("Internal Store Transfer & Assortment Management System")
        st.write("Upload files and access internal inventory systems.")
