import time
import streamlit as st
from utils import get_user

# Verify_password removed — no longer needed

def _safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()  # For older versions


def login_page():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.session_state.get("logged_in"):
        st.success(f"✅ Already logged in as {st.session_state['username']}")
        return

    if st.button("Login"):
        # Call API with both username + password
        user = get_user(username, password)

        if user:
            st.session_state["logged_in"] = True
            st.session_state["username"] = user["username"]
            st.session_state["user_id"] = user.get("id")
            st.session_state["role"] = user.get("role")

            st.session_state["rights"] = {
                "internal_store_transfer": user.get("can_access_internal_store_transfer", False),
                "assortment": user.get("can_access_assortment", False),
                "ip": user.get("can_access_ip", False),
            }

            st.success("🎉 Login successful! Redirecting...")
            time.sleep(0.8)
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
            -webkit-box-align: center;
            align-items: center;
            -webkit-box-pack: center;
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
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 0.5, 1])

    with col1:
        if not st.session_state.get("logged_in"):
            login_page()
        else:
            st.success(f"Logged in as: {st.session_state['username']}")

    with col2:
        st.write("")

    with col3:
        st.header("Welcome")
        st.write("Welcome to the Internal Store Transfer and Assortment Management App!")
        st.write("Upload your Excel file to manage assortments and streamline internal store transfers.")


# Entry point
if not st.session_state.get("logged_in"):
    show_login()
else:
    st.success(f"Logged in as {st.session_state['username']}")
