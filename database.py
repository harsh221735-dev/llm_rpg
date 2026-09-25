import os
from flask import Flask
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

# 1. Added <selected_player> to the URL path to map it to your function argument
@app.route('/database/<selected_player>')
def load_player_info(selected_player):
    
    # 2. Fetch the data from your table 
    response1 = supabase.table("players").select('*').eq('id',selected_player).execute()   

    print('attacker data raw:', response1.data)    
    
    # 3. CRITICAL FIX: Check if the database actually returned a player
    if not response1.data:
        return {'error': f'Player with ID {selected_player} not found'}, 404

    # 4. Extract data safely now that we know response1.data[0] exists
    player_data = response1.data[0]
    
    player_id1 = player_data['id']
    player_name = player_data['player_name']
    base_health = player_data['base_health']
    base_attack = player_data['base_attack']    
    base_defence = player_data['base_defence']  
    base_speed = player_data['base_speed']  
    base_stamina = player_data['base_stamina']  

    # 5. Return JSON output (Flask automatically turns dicts into JSON)
    return {
        'output': [
            player_id1,
            player_name,
            base_health,
            base_attack,
            base_defence,
            base_speed,
            base_stamina
        ]
    }


if __name__ == '__main__':
    # Change port from 5000 to 5050
    app.run(debug=True, port=8800)

