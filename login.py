import streamlit as st
import pandas as pd

# --- Load Users ---
@st.cache_data
def load_users():
    df = pd.read_csv("authentication.csv")
    df.columns = df.columns.str.strip()
    return df[df["is_active"] == "X"]

# --- Authentication Logic ---
def authenticate_user(username, password, users_df):
    username = username.lower()
    users_df["User_Name"] = users_df["User_Name"].str.lower()
    match = users_df[(users_df["User_Name"] == username) & (users_df["Password"] == password)]
    if not match.empty:
        return match.iloc[0]
    return None

# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

# --- UI ---
st.title("Login to  Dashboard")

if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    users_df = load_users()

    if st.button("Login"):
        user = authenticate_user(username, password, users_df)
        if user is not None:
            if user["user_type"] == "A" and user["Menu_type"] == "A":
                st.session_state.logged_in = True
                st.session_state.user_info = user
                st.success("✅ Login successful! Redirecting...")
                st.switch_page("pages/fab.py")  
            else:
                st.error("🚫 You do NOT have permission to access the dashboard.")
        else:
            st.error("❌ Invalid username or password.")
else:
    user = st.session_state.user_info
    st.success(f"🔓 Logged in as: {user['User_Name']} ({user['user_type']})")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.rerun()
