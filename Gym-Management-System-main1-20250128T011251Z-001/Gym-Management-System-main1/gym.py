import streamlit as st
import psycopg2
from admin_interface import render_admin_interface
from admin_login import admin_login
from member_interface import show_member_page, member_signup_page
from member_functions import member_login

header_section = st.container()
main_section = st.container()
login_section = st.container()
logout_section = st.container()

# Function to establish a database connection
def connect_to_database():
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(
            dbname='gym',
            user='ROHAN',
            password='rohan',
            host='localhost',
            port=5432
        )
        return conn
    except psycopg2.Error as e:
        st.error("Error connecting to PostgreSQL database: {}".format(e))
        return None

def show_main_page():
    with main_section:
        st.title("Welcome to GYM Management System")
        st.write("Here, you can manage members, see plans, update and delete members.")
        render_admin_interface(cursor, conn)

def logged_out_clicked():
    st.session_state['logged_in'] = False
    if 'member_id' in st.session_state:
        del st.session_state['member_id']
    update_page_state('login')

def show_logout_page():
    login_section.empty()
    with logout_section:
        st.button("Log Out", key="logout", on_click=logged_out_clicked)

def admin_logged_in_clicked(username, password):
    if admin_login(cursor, username, password):
        st.session_state['logged_in'] = True
        update_page_state('main')
    else:
        st.error("Invalid admin username or password")

def member_logged_in_clicked(username, password):
    member_id = member_login(cursor, username, password)
    if member_id:
        st.session_state['logged_in'] = True
        st.session_state['member_id'] = member_id
        update_page_state('member')
    else:
        st.error("Invalid member username or password")

def show_login_page():
    with login_section:
        if not st.session_state.get('logged_in', False):
            user_type = st.radio("Login as", ["Admin", "Member"])
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if user_type == "Admin":
                st.button("Login as Admin", on_click=admin_logged_in_clicked, args=(username, password))
            else:
                st.button("Login as Member", on_click=member_logged_in_clicked, args=(username, password))
                st.write("Not a member?")
                st.button("Sign Up", on_click=update_page_state, args=('signup',))

# def update_page_state(new_page):
#     st.session_state['page'] = new_page
def update_page_state(new_page):
    st.session_state['page'] = new_page
    if new_page != 'signup':
        st.session_state['show_signup'] = False


def reset_page_state():
    st.session_state['page'] = 'login'
    if 'signup_success' in st.session_state:
        del st.session_state['signup_success']


def main():
    st.title("Gym Management System")
    global conn, cursor

    conn = connect_to_database()
    if conn is not None:
        cursor = conn.cursor()

        with header_section:
            if 'logged_in' not in st.session_state:
                st.session_state['logged_in'] = False
                st.session_state['page'] = 'login'
            
            if st.session_state.get('page') == 'login':
                show_login_page()
            elif st.session_state.get('page') == 'signup':
                member_signup_page(cursor, conn)
            elif st.session_state.get('page') == 'main':
                show_main_page()
                show_logout_page()
            elif st.session_state.get('page') == 'member':
                show_member_page(cursor, st.session_state['member_id'])
                show_logout_page()

if __name__ == "__main__":
    main()

