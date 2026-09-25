import streamlit as st

#initialise all states, pages here NO DISPLAY ITEMS

#srteamlit reeuns after pressing button so chaning state so it remembers after refersh
if 'user_matched' not in st.session_state:
    st.session_state.user_matched = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = 0
if 'users' not in st.session_state:
    st.session_state.users = set()
if 'selected_character' not in st.session_state:
    st.session_state.selected_character = 0
if 'start_battle' not in st.session_state:
    st.session_state.start_battle = False
if 'waiting_for_match' not in st.session_state:
    st.session_state.waiting_for_match = False
#if 'player_list' not in st.session_state:
#    st.session_state.player_list = []


#creating user Id using cookies

import extra_streamlit_components as cookie_manager
import uuid

# 1. Initialize the cookie manager

cookies = cookie_manager.CookieManager(key="my_cookie_manager")


# 2. Give the manager a moment to read cookies from the browser
# (Cookies take a split second to load via frontend component)
st.write("") 

# 3. Fetch or Create the persistent unique ID
user_uuid = cookies.get(cookie="streamlit_instance_id")

if not user_uuid:
    # Generate a brand new unique ID if they don't have one
    new_uuid = uuid.uuid4()
    user_uuid = str(uuid.uuid4())
    
    # Save it to the browser's cookies (expires in 30 days)
    cookies.set(
        "streamlit_instance_id", 
        user_uuid, 
        max_age=30 * 24 * 3600
    )
    st.session_state.user_id = str(new_uuid)
else:
    # 4. Save it to session state for easy access across pages
    uuid_object = uuid.UUID(user_uuid)
    st.session_state.user_id = str(uuid_object)


# --- Visual Proof (Test by refreshing the page!) ---
#st.title("Persistent Instance Tracker")
#st.write("Your Unique Instance ID:")
#st.code(st.session_state.user_id, language="text")


first_page = st.Page('frontend_pages/1st_page.py',title='first_page')
second_page = st.Page("frontend_pages/2nd_page.py", title="Second Page")
third_page = st.Page('frontend_pages/3rd_page.py',title='Third page')

pg = st.navigation([first_page,second_page,third_page])

pg.run()

