import streamlit as st
import requests
import re

def set_page_config():
    st.set_page_config(
        page_title="Contact Us Form",
        page_icon="notes.png",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def show_contact():
    st.markdown("""
        <style>
            .stApp {
                background-image: url("https://emc2rrspvpp.exactdn.com/wp-content/themes/centricSoftware/img/correct-glow.jpg");
                background-size: cover;
                color: #5c5c6052;
               height: 160%;
            }
            .st-emotion-cache-1whx7iy p {
    word-break: break-word;
    margin-bottom: 0px;
    font-size: 14px;
    color: white;
}
                h1 {
    font-family: "Source Sans Pro", sans-serif;
    font-weight: 700;
    color: rgb(239 240 249);
    padding: 1.25rem 0px 1rem;
    margin: 0px;
    line-height: 1.2;
}
                .st-emotion-cache-1vt4y43 {
    
    align-items: center;
   
    justify-content: center;
   
    padding: 0.25rem 0.75rem;
    border-radius: 0.5rem;
    min-height: 2.5rem;
    margin: 0px;
    line-height: 1.6;
    color: white;
    width: 200px;
    user-select: none;
    background-color: rgb(38 85 194);
    border: 1px solid rgba(49, 51, 63, 0.2);
    position: relative;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}
        </style>
    """, unsafe_allow_html=True)

    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    st.success("Got a question? We'd love to hear from you. Send us a message and we'll respond as soon as possible.")
    st.markdown("<h1 style='text-align: center;'>Contact Us</h1>", unsafe_allow_html=True)

    with st.form(key='my_form'):
        occupation = st.selectbox(label='What can we help you with?', options=['Select', 'I want the tool', 'I have a suggestion', 'Other'])
        name = st.text_input(label='Name')
        email = st.text_input(label='Email')
        text = st.text_area("Message")
        submit_button = st.form_submit_button(label='Submit')

    # Process the form data
    if submit_button:
        if occupation == 'Select':
            st.error("Please select the reason")
        if not name:
            st.error('Please enter your name')
        if not email:
            st.error('Please enter your email')
        if not text:
            st.error('Please enter a message')

        if name and email and text and occupation != 'Select':
            # Validate email format
            if not re.match(email_regex, email):
                st.error('Please enter a valid email address')
                return

            # Send the form data to FormsPree
            data = {'Name': name, 'Email': email, 'Purpose': occupation, 'Message': text}
            response = requests.post('https://formspree.io/f/xyzgyady', data=data)

            # Display a success or error message
            if response.status_code == 200:
                st.success('Form submitted successfully.')
            else:
                st.error('Error submitting form.')

if __name__ == "__main__":
    set_page_config()
    show_contact()
