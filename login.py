import streamlit as st
import requests
import random
import webbrowser

# Function to generate a random code
def generate_random_code(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

# Function to send SMS
def send_sms(username, password, recipient_number, random_code, special_number, checking_message_id):
    url = f"https://sms.sunwaysms.com/smsws/HttpService.ashx?service=SendArray"
    message_body = f"Your verification code is: {random_code}"
    params = {
        "username": username,
        "password": password,
        "to": recipient_number,
        "message": message_body,
        "from": special_number,
        "chkMessageId": checking_message_id
    }
    response = requests.get(url, params=params)
    return response.text

# State management for storing the verification code
if 'verification_code' not in st.session_state:
    st.session_state.verification_code = None
if 'is_verified' not in st.session_state:
    st.session_state.is_verified = False

# Streamlit interface
st.title("Login with Verification Code")

username = st.text_input("User Name")
password = st.text_input("Password", type="password")
recipient_number = st.text_input("Recipient Number")
special_number = "3000797111"#st.text_input("Special Number")
checking_message_id = st.text_input("Checking Message ID")

if st.button("Send Verification Code"):
    random_code = generate_random_code()
    result = send_sms(username, password, recipient_number, random_code, special_number, checking_message_id)
    st.session_state.verification_code = random_code
    st.write("Verification code has been sent to your phone.")

if st.session_state.verification_code:
    entered_code = st.text_input("Enter the verification code you received")
    if st.button("Verify and Login"):
        if entered_code == st.session_state.verification_code:
            st.session_state.is_verified = True
            st.write("You have successfully logged in!")
            # webbrowser.open('https://katebyaar.ir/')
            
        else:
            st.write("Invalid verification code. Please try again.")

# Example of post-login content
if st.session_state.is_verified:
    st.write("Welcome to katebyaar!")
    webbrowser.open('https://katebyaar.ir/')
