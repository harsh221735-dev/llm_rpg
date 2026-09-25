import load_models
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import time
import database
import requests

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
    opponent_data = requests.get(url=f'http://127.0.0.1:8800/database/{player_char_id}')
    
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


     

class AttackPayload(BaseModel):
    attack: str
    attacker: str
    opponent_str: str
memory = [] 
@app.post('/give_attack')
def attack(payload: AttackPayload):
    global charach_attack, charach_defence, charach_speed, charach_stamina,selected_char
    global opponent_attack, opponent_defence, opponent_speed, opponent_stamina,opponent
    query = payload.attack
    attacker = payload.attacker
    opponent_str = payload.opponent_str

    print('success 1')

    window_size = 2     
    memory.append(f'attacker:{attacker},attacker_attack_:{query}')        
    if len(memory) > window_size:       
        memory.pop(0)            
    print('memory: ',memory)        
    print('attacker: ',attacker)        
    print('opponent: ',opponent_str)        
    #retrieving         
    print('success 2')
    retriever = db.as_retriever(            
        search_type = 'similarity_score_threshold',  #use mmr method for diverse retrivation of content         
        search_kwargs={'k':1,'score_threshold':0.3}         
        )           
    relevant_docs =retriever.invoke(query)          
    #print('user query : ',query)      
    print('success 3')     
    print('context: \n')            
    for i,doc in enumerate(relevant_docs):          
        print(f'document {i+1} :')          
        print(f'content : {doc.page_content[:100]}')            
        print(f'characters : {len(doc.page_content)}')          

    context = relevant_docs[0].page_content         

    # instead of passing whole attributes like health= 100/100, speed120/120 etc just use threshold and pass high,normal,low,very_low
    if attacker == selected_char['player_name']:
        attacker_health = charach_health
        oppo_health = opponent_health
        att_max = {'attack': selected_char['curr_attack'], 'defence': selected_char['curr_defence'], 'speed': selected_char['curr_speed'], 'stamina': selected_char['curr_stamina']}
        opp_max = {'attack': opponent['curr_attack'], 'defence': opponent['curr_defence'], 'speed': opponent['curr_speed'], 'stamina': opponent['curr_stamina']}
    else:
        attacker_health = opponent_health
        oppo_health = charach_health
        att_max = {'attack': opponent['curr_attack'], 'defence': opponent['curr_defence'], 'speed': opponent['curr_speed'], 'stamina': opponent['curr_stamina']}
        opp_max = {'attack': selected_char['curr_attack'], 'defence': selected_char['curr_defence'], 'speed': selected_char['curr_speed'], 'stamina': selected_char['curr_stamina']}
    def get_attributes(current,base):
        if current <= 0.25*base:     
            attacker_attack_chng = 'very very low'      

        elif current <= 0.5*base:        
            attacker_attack_chng = 'very low'       

        elif current <= 0.75*base:       
            attacker_attack_chng = 'low'        

        elif current <= base:        
            attacker_attack_chng = 'normal'     

        else:       
           attacker_attack_chng = 'high'   
        return attacker_attack_chng   
    
    attacker_attack_chng  = get_attributes(charach_attack, att_max['attack'])
    attacker_defence_chng = get_attributes(charach_defence, att_max['defence'])
    attacker_speed_chng   = get_attributes(charach_speed, att_max['speed'])
    attacker_stamina_chng = get_attributes(charach_stamina, att_max['stamina'])

    opponent_attack_chng  = get_attributes(opponent_attack, opp_max['attack'])
    opponent_defence_chng = get_attributes(opponent_defence, opp_max['defence'])
    opponent_speed_chng   = get_attributes(opponent_speed, opp_max['speed'])
    opponent_stamina_chng = get_attributes(opponent_stamina, opp_max['stamina'])

    prompt = f"<|im_start|>system\nYou are a smart scenario predictor of a versus battle game.<|im_end|>\n<|im_start|>user\n'just give prediction in under 20 words and change in current_attributes in 'percentage' in opponent and attacker by carefully analyzing all parameters in the format:{{'prediction': '...', 'change_in_attacker_attributes': ['attack':,'defence':,'speed':,'stamina':],'change_in_opponent_attributes':['attack':,'defence':,'speed':,'health':]}}'; attacker: {attacker} ,attacker_attributes :[attack={attacker_attack_chng},stamina={attacker_stamina_chng},speed={attacker_speed_chng}]; opponent: {opponent} ,opponent_attributes :[health={oppo_health},speed={opponent_speed_chng},def={opponent_defence_chng}],{attacker}'s_attack:{query},attacker's attack_info:{context},previous_actions:{memory},attribute_behaviour-'effects occur all time:attack consumes stamina based on its power, effects occur based on attack:depends on type and power of attack'.<|im_end|>\n<|im_start|>assistant\n"          

    # 3. Generate the response          
    print("Thinking...")            
    output = llm(           
        prompt,         
        max_tokens=128,  # Limit output length to save time/RAM         
        stop=["<|im_end|>"],  # Stop generating when model finishes         
        echo=False          
    )           
    result = output['choices'][0]['text']
    # 4. Print the result           
    print("\nAnswer:")          
    print(result)
    return {'result': result}

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

         
