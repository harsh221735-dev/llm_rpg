import load_models
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import json
import database

llm, db = load_models.loaded_models()

load_dotenv()
app = FastAPI()

curr_attack_attacker = 0 
curr_defence_opponent = 0    
curr_speed_opponent = 0  
curr_stamina_attacker = 0    

class IdPayload(BaseModel):
    id: int
    opponent_id: int

@app.post('/charachter')
def get_charachter(payload:IdPayload):
    id = payload.id
    opponent_id = payload.opponent_id
    result = database.load_player_info(id,opponent_id)
    global attack_attacker, defence_opponent, speed_opponent, stamina_attacker
    global curr_attack_attacker, curr_defence_opponent, curr_speed_opponent, curr_stamina_attacker
    attack_attacker = result[0]

    defence_opponent = result[1]
  
    speed_opponent = result[2]
 
    stamina_attacker= result[3]

    curr_attack_attacker = attack_attacker 
    curr_defence_opponent = defence_opponent   
    curr_speed_opponent = speed_opponent   
    curr_stamina_attacker = stamina_attacker   

class AttackPayload(BaseModel):
    attack: str
    attacker: str
    opponent: str
memory = [] 
@app.post('/give_attack')
def attack(payload: AttackPayload):
    global attack_attacker, defence_opponent, speed_opponent, stamina_attacker
    global curr_attack_attacker, curr_defence_opponent, curr_speed_opponent, curr_stamina_attacker
    query = payload.attack
    attacker = payload.attacker
    opponent = payload.opponent
       

    window_size = 2     
    memory.append(f'attacker:{attacker},attack_attacker:{query}')        
    if len(memory) > window_size:       
        memory.pop(0)            
    print('memory: ',memory)        
    print('attacker: ',attacker)        
    print('opponent: ',opponent)        
    #retrieving         

    retriever = db.as_retriever(            
        search_type = 'similarity_score_threshold',  #use mmr method for diverse retrivation of content         
        search_kwargs={'k':1,'score_threshold':0.3}         
        )           
    relevant_docs =retriever.invoke(query)          
    #print('user query : ',query)           
    print('context: \n')            
    for i,doc in enumerate(relevant_docs):          
        print(f'document {i+1} :')          
        print(f'content : {doc.page_content[:100]}')            
        print(f'characters : {len(doc.page_content)}')          


    import time         

    context = relevant_docs[0].page_content         

    # instead of passing whole attributes like health= 100/100, speed120/120 etc just use threshold and pass high,normal,low,very_low

    if curr_attack_attacker <= 0.25*attack_attacker:
        attack_chng = 'very very low'
    
    elif curr_attack_attacker <= 0.5*attack_attacker:
        attack_chng = 'very low'
    
    elif curr_attack_attacker <= 0.75*attack_attacker:
        attack_chng = 'low'
    
    elif curr_attack_attacker <= attack_attacker:
        attack_chng = 'normal'
    else:
        attack_chng = 'high'

    if curr_defence_opponent <= 0.25*defence_opponent:
        defence_chng = 'very very low'   
    elif curr_defence_opponent <= 0.5*defence_opponent: 
        defence_chng = 'very low'    
    elif curr_defence_opponent <= 0.75*defence_opponent:    
        defence_chng = 'low' 
    elif curr_defence_opponent <= defence_opponent: 
        defence_chng = 'normal'  
    else:   
        defence_chng = 'high'    

    if curr_speed_opponent <= 0.25*speed_opponent:
        speed_chng = 'very very low'       
    elif curr_speed_opponent <= 0.5*speed_opponent:     
        speed_chng = 'very low'        
    elif curr_speed_opponent <= 0.75*speed_opponent:        
        speed_chng = 'low'     
    elif curr_speed_opponent <= speed_opponent:     
        speed_chng = 'normal'      
    else:       
        speed_chng = 'high'    

    if curr_stamina_attacker <= 0.25*stamina_attacker:
        stamina_chng = 'very very low'       
    elif curr_stamina_attacker <= 0.5*stamina_attacker:     
        stamina_chng = 'very low'        
    elif curr_stamina_attacker <= 0.75*stamina_attacker:        
        stamina_chng = 'low'     
    elif curr_stamina_attacker <= stamina_attacker:     
        stamina_chng = 'normal'      
    else:       
        stamina_chng = 'high'    
    
    prompt = f"<|im_start|>system\nYou are a strict referee of a versus battle game.<|im_end|>\n<|im_start|>user\n'just predict what will happen in under 20 words and change in current_attributes in 'percentage' in opponent by carefully analyzing all parameters given in the format:{{'prediction': '...', 'change': '...'}}'; attacker: {attacker} ,attacker_attributes :[attack_attacker={attack_chng},stamina_attacker={stamina_chng}]; opponent: {opponent} ,opponent_attributes :[speed_opponent={speed_chng},def={defence_chng}],attack_attacker:{query},attacker's attack_info:{context},previous_actions:{memory}.<|im_end|>\n<|im_start|>assistant\n"          

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
    try:
        data = json.loads(result)         
        attribute_change = data.get('change', '0%')
        output_text = data.get('prediction', result)
    except Exception as e:
        print(f"JSON Parsing failed: {e}")
        output_text = result
 
    return {'result': output_text,'attacker':attacker,'opponent':opponent}


# 2. Format the prompt using Qwen's Chat Template

         
