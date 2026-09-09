import streamlit as st
import requests
import random

st.title("LLM Poke Game")

# 1. Initialize session states so they persist across runs
if 'attacker' not in st.session_state:
    st.session_state.attacker = 'yuji itadori'
if 'opponent' not in st.session_state:
    st.session_state.opponent = 'megumi fushiguro'
if 'battle_output' not in st.session_state:
    st.session_state.battle_output = "No moves played yet. Start the battle!"
if 'counter' not in st.session_state:
    st.session_state.counter = 0

fastapi_url1 = 'http://127.0.0.1:8000/charachter'  
fastapi_url2 = 'http://127.0.0.1:8000/give_attack'  

# Display current battle header
st.subheader(f"⚔️ {st.session_state.attacker.title()} vs {st.session_state.opponent.title()}")
st.write('1: yuji itadori \n2: maki \n3: gojo satoru \n4: megumi fushiguro')

# Character selection layout
if st.session_state.counter == 0:
    # FIXED: Changed key to 'character_form' to avoid DuplicateWidgetID crash
    with st.form(key='character_form', clear_on_submit=True):
        character = st.number_input('Choose character number (1-4): ', min_value=1, max_value=4, value=1)
        char_submit = st.form_submit_button(label='Select Character')

    # FIXED: API call now only runs AFTER the user clicks the selection button
    if char_submit:
        opponent_id = random.randint(1, 4)
        payload1 = {'id': int(character), 'opponent_id': opponent_id}
        try:
            response = requests.post(url=fastapi_url1, json=payload1)
            if response.status_code == 200:
                st.session_state.counter += 1
                st.rerun()
            else:
                st.error(f"Failed to load character. Server returned: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to FastAPI. Is your backend server up?")

# Battle phase layout (only appears after character choice handles tracking counter)
if st.session_state.counter > 0:
    with st.form(key='turn_form', clear_on_submit=True):
        user_input = st.text_input('Enter your attack (Press Enter to submit): ')
        attack_submit = st.form_submit_button(label='Submit Attack')

    if attack_submit:
        attack = user_input.strip() if user_input.strip() != "" else "does nothing"
        
        payload2 = {
            'attack': attack,
            'attacker': st.session_state.attacker,
            'opponent': st.session_state.opponent
        }
        
        try:
            response = requests.post(url=fastapi_url2, json=payload2)
            
            if response.status_code == 200:
                st.session_state.battle_output = response.json()['result']
                
                # Swap positions inside session_state for the next turn
                temp = st.session_state.attacker     
                st.session_state.attacker = st.session_state.opponent     
                st.session_state.opponent = temp
                
                st.rerun()
            else:
                st.error(f"Backend issue: Status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to FastAPI. Is your Uvicorn running?")

# 4. Display the output OUTSIDE the form block
st.header("Output:")
st.info(st.session_state.battle_output)

# Display static role tracking below
st.markdown("---")
st.write(f"**Current Attacker:** {st.session_state.attacker}")
st.write(f"**Current Opponent:** {st.session_state.opponent}")
