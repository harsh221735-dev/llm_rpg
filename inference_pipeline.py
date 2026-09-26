import load_models
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import time
import requests
import random

llm, db = load_models.loaded_models()

load_dotenv()
app = FastAPI()

selected_char = {}
charach_health = 0
charach_attack =0
charach_defence = 0
charach_speed = 0
charach_stamina = 0

opponent = {}
opponent_health = 0     
opponent_attack = 0
opponent_defence = 0
opponent_speed  = 0
opponent_stamina = 0





class IdPayload(BaseModel):
    id: int
    opponent_id: int

@app.post('/init_stats')
def get_charachter(payload: IdPayload):
    # 1. Fetch matching active room state variables from global/state parameters if needed
    # For this function, we pull IDs directly from the incoming payload
    player_char_id = payload.id
    opp_char_id = payload.opponent_id
    
    # 2. FIX: Call the database function TWICE separately using 1 argument each
    player_data = requests.get(url=f'http://127.0.0.1:8800/database/{player_char_id}')
    opponent_data = requests.get(url=f'http://127.0.0.1:8800/database/{opp_char_id}')
    
    global charach_attack, charach_defence, charach_speed, charach_stamina, selected_char
    global opponent_attack, opponent_defence, opponent_speed, opponent_stamina, opponent
    
    # 3. Unpack your own character statistics safely
    selected_char = {}
    selected_char['player_name']   = player_data.json()['output'][1]
    selected_char['curr_health']   = player_data.json()['output'][2]
    selected_char['curr_attack']   = player_data.json()['output'][3]
    selected_char['curr_defence']  = player_data.json()['output'][4]
    selected_char['curr_speed']    = player_data.json()['output'][5]
    selected_char['curr_stamina']  = player_data.json()['output'][6]

    charach_health  = selected_char['curr_health']
    charach_attack  = selected_char['curr_attack']
    charach_defence = selected_char['curr_defence']
    charach_speed   = selected_char['curr_speed']
    charach_stamina = selected_char['curr_stamina']

    # 4. Unpack your opponent's character statistics safely
    opponent = {}
    opponent['player_name']   = opponent_data.json()['output'][1]
    opponent['curr_health']   = opponent_data.json()['output'][2]
    opponent['curr_attack']   = opponent_data.json()['output'][3]
    opponent['curr_defence']  = opponent_data.json()['output'][4]
    opponent['curr_speed']    = opponent_data.json()['output'][5]
    opponent['curr_stamina']  = opponent_data.json()['output'][6]

    opponent_health  = opponent['curr_health']
    opponent_attack  = opponent['curr_attack'] 
    opponent_defence = opponent['curr_defence'] 
    opponent_speed   = opponent['curr_speed']
    opponent_stamina = opponent['curr_stamina']
    
    return {
        "status": "success", 
        "player": selected_char, 
        "opponent": opponent
    }

# 1. State Store to track the current active attacker ID globally across endpoints
game_state = {
    "current_attacker_id": None
}
# 1. State Store to track the current active attacker ID globally across endpoints
game_state = {
    "current_attacker_id": None
}

class CurrAttackerPayload(BaseModel):
    id: str
    opponent_id: str

@app.post('/who_will_attacker')
def get_current_attacker(payload: CurrAttackerPayload):
    # Initialize turn only if the game just started or hasn't been set yet
    if game_state["current_attacker_id"] is None:
        game_state["current_attacker_id"] = random.choice([payload.id, payload.opponent_id])
    
    return {'attacker': game_state["current_attacker_id"]}


class AttackPayload(BaseModel):
    attack: str
    attacker: str       
    opponent_str: str   
    attacker_id: str    
    opponent_id: str    

memory = [] 

@app.post('/give_attack')
def process_attack(payload: AttackPayload):
    global charach_attack, charach_defence, charach_speed, charach_stamina, selected_char
    global opponent_attack, opponent_defence, opponent_speed, opponent_stamina, opponent
    
    query = payload.attack
    current_attacker_name = payload.attacker
    current_opponent_name = payload.opponent_str

    print('success 1')

    # Memory Tracking Logic
    window_size = 2     
    memory.append(f'attacker:{current_attacker_name},attacker_attack_:{query}')        
    if len(memory) > window_size:       
        memory.pop(0)            

    # Retriever Logic
    retriever = db.as_retriever(            
        search_type='similarity_score_threshold',
        search_kwargs={'k': 1, 'score_threshold': 0.3}         
    )           
    relevant_docs = retriever.invoke(query)          
    
    # FIX 1: Removed the duplicated crash-prone statement and wrapped safely
    context = relevant_docs[0].page_content if relevant_docs else "Standard physical confrontation environment."

    # Dynamic attribute targeting based on active attacker profile name
    if current_attacker_name == selected_char['player_name']:
        current_att_health = charach_health
        current_opp_health = opponent_health
        att_max = {'attack': selected_char['curr_attack'], 'defence': selected_char['curr_defence'], 'speed': selected_char['curr_speed'], 'stamina': selected_char['curr_stamina']}
        opp_max = {'attack': opponent['curr_attack'], 'defence': opponent['curr_defence'], 'speed': opponent['curr_speed'], 'stamina': opponent['curr_stamina']}
        
        a_att, a_def, a_spd, a_stm = charach_attack, charach_defence, charach_speed, charach_stamina
        o_att, o_def, o_spd, o_stm = opponent_attack, opponent_defence, opponent_speed, opponent_stamina
    else:
        current_att_health = opponent_health
        current_opp_health = charach_health
        att_max = {'attack': opponent['curr_attack'], 'defence': opponent['curr_defence'], 'speed': opponent['curr_speed'], 'stamina': opponent['curr_stamina']}
        opp_max = {'attack': selected_char['curr_attack'], 'defence': selected_char['curr_defence'], 'speed': selected_char['curr_speed'], 'stamina': selected_char['curr_stamina']}
        
        a_att, a_def, a_spd, a_stm = opponent_attack, opponent_defence, opponent_speed, opponent_stamina
        o_att, o_def, o_spd, o_stm = charach_attack, charach_defence, charach_speed, charach_stamina

    def get_attributes(current, base):
        if current <= 0.25 * base:     
            return 'very very low'      
        elif current <= 0.5 * base:        
            return 'very low'       
        elif current <= 0.75 * base:       
            return 'low'        
        elif current <= base:        
            return 'normal'     
        else:       
            return 'high'   
    
    attacker_attack_chng  = get_attributes(a_att, att_max['attack'])
    attacker_defence_chng = get_attributes(a_def, att_max['defence'])
    attacker_speed_chng   = get_attributes(a_spd, att_max['speed'])
    attacker_stamina_chng = get_attributes(a_stm, att_max['stamina'])

    opponent_attack_chng  = get_attributes(o_att, opp_max['attack'])
    opponent_defence_chng = get_attributes(o_def, opp_max['defence'])
    opponent_speed_chng   = get_attributes(o_spd, opp_max['speed'])
    opponent_stamina_chng = get_attributes(o_stm, opp_max['stamina'])

    # Build Prompt
    prompt = f"<|im_start|>system\nYou are a smart scenario predictor of a versus battle game.<|im_end|>\n<|im_start|>user\n'just give prediction in under 20 words and change in current_attributes in 'percentage' in opponent and attacker by carefully analyzing all parameters in the format:{{'prediction': '...', 'change_in_attacker_attributes': ['attack':,'defence':,'speed':,'stamina':],'change_in_opponent_attributes':['attack':,'defence':,'speed':,'health':]}}'; attacker: {current_attacker_name} ,attacker_attributes :[attack={attacker_attack_chng},stamina={attacker_stamina_chng},speed={attacker_speed_chng}]; opponent: {current_opponent_name} ,opponent_attributes :[health={current_opp_health},speed={opponent_speed_chng},def={opponent_defence_chng}],{current_attacker_name}'s_attack:{query},attacker's attack_info:{context},previous_actions:{memory},attribute_behaviour-'effects occur all time:attack consumes stamina based on its power, effects occur based on attack:depends on type and power of attack'.<|im_end|>\n<|im_start|>assistant\n"          

    # LLM Execution
    output = llm(prompt, max_tokens=128, stop=["<|im_end|>"], echo=False)           
    result = output['choices'][0]['text']

    # FIX 2: Safely pass turn alternation based on tracking context matching strings
    if game_state["current_attacker_id"] == payload.attacker_id:
        game_state["current_attacker_id"] = payload.opponent_id
    else:
        game_state["current_attacker_id"] = payload.attacker_id

    return {
        'result': result,
        'attacker': current_attacker_name,
        'opponent': current_opponent_name
    }


codes = {}
users = set()
class gen_code(BaseModel):
    code_set:int
    user_id:str
@app.post('/code_check')
def gen_code(payload:gen_code):
    global codes
    code = payload.code_set
    if code not in codes:
        codes[code] = payload.user_id
        return {'result':'passed'}
    else:
        return {'result':'failed'}

class user_payload(BaseModel):
    user_id:str
@app.post('/user_check')
def user_check(payload:user_payload):
    if payload.user_id in users:
        return {'result':'success'}
    else:
        return {'result':'failed'}

class code_payload(BaseModel):
    received_code:int
    user_id:str
@app.post('/match_code')
def code_match(payload:code_payload):
    global codes,users
    received_code = payload.received_code
    if received_code in codes:
        #adding both users to users set
        users.add(codes[received_code])
        users.add(payload.user_id)
        del codes[received_code]
        return {'result':'success'}
    else:
        return {'result':'failed'}

@app.post('/init_players_set')
def set_player():
    global player_set

class assign_payload(BaseModel):
    player_id: str

from typing import Dict

# Track active queueing players with their last known timestamp {player_id: timestamp}
waiting_pool: Dict[str, float] = {}

# Symmetrically maps Player ID -> Opponent Player ID
active_rooms: Dict[str, int] = {}

class AssignPayload(BaseModel):
    player_id: str

@app.post('/assigning_players')
def assign(payload: AssignPayload):
    pid = payload.player_id
    current_time = time.time()
    
    # 1. If this player is already inside a matched room, report success instantly
    if pid in active_rooms:
        return {'status': 'joined'}
        
    # 2. HOUSEKEEPING: Remove any dead ghost players who haven't polled in over 3 seconds
    # This automatically cleans up players who refreshed or closed their tab!
    dead_players = [p for p, t in waiting_pool.items() if current_time - t > 3.0]
    for p in dead_players:
        waiting_pool.pop(p, None)
        
    # 3. Register or update this player's active heartbeat timestamp
    waiting_pool[pid] = current_time
        
    # 4. Check if there is another valid waiting opponent in the pool
    # Filter out our own ID to find a true matchmaking peer
    opponents = [p for p in waiting_pool.keys() if p != pid]
    
    if len(opponents) >= 1:
        opponent_id = opponents[0]
        
        # Pull both cleanly out of the waiting matchmaking pool
        waiting_pool.pop(pid, None)
        waiting_pool.pop(opponent_id, None)
        
        # Link them symmetrically into an active match instance
        active_rooms[pid] = opponent_id
        active_rooms[opponent_id] = pid
        
        return {'status': 'joined'}
        
    return {'status': 'waiting'}

@app.post('/leave_queue')
def leave_queue(payload: assign_payload):
    if payload.player_id in waiting_pool:
        waiting_pool.remove(payload.player_id)
    return {'status': 'removed'}

# Add this endpoint to your backend file
@app.get('/get_opponent/{player_id}')
def get_opponent(player_id: str):
    # active_rooms maps your player_id -> opponent_id
    if player_id in active_rooms:
        return {'status': 'success', 'opponent_id': active_rooms[player_id]}
    return {'status': 'error', 'message': 'Match room not found'}

characters = {}
class up_char(BaseModel):
    player_id: str
    char_id : int
@app.post('/upload_char')
def get_char(payload:up_char):
    global characters
    # active_rooms maps your player_id -> opponent_id
    characters[payload.player_id] = payload.char_id
    print(characters)

class select_char(BaseModel):
    player_id: str
@app.post('/selected_char')
def get_char(payload:select_char):
    global characters
    # active_rooms maps your player_id -> opponent_id
    print(characters)
    if payload.player_id in characters:
        return {'status': 'success', 'char_id': characters[payload.player_id]}
    return {'status': 'error', 'message': 'char_id not found'}

         
