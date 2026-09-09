SUPABASE_URL='https://ehucijmriybfxqmbjwci.supabase.co'
SUPABASE_KEY='sb_publishable_G5qZqesljyBkGVZk4neg6g_UEIXTC9O'

from supabase import create_client, Client
import os
from dotenv import load_dotenv   # for temporary password

load_dotenv()
password = os.getenv("my_password")
# 1. Connect to your Supabase project
# Use your standard Project URL and Anon (Public) Key from the dashboard settings
url: str = SUPABASE_URL
public_anon_key: str = SUPABASE_KEY

supabase: Client = create_client(url, public_anon_key)


# 2. Log in as YOURSELF so the SELECT policy recognizes your ID
session = supabase.auth.sign_in_with_password({
    "email": "harsh28.sakhare@gmail.com",
    "password": password
})
#selected_player = 1
#opponent = 2
def load_player_info(selected_player,opponent):
    # 3. Fetch the data from your table 
    # Replace 'your_table_name' with the exact name of your table   
    response1 = (supabase.table("players").select("base_attack","base_stamina").eq('id',selected_player).execute())   
    response2 = (supabase.table("players").select("base_defence","base_speed").eq('id',opponent).execute())

    print('attacker:',response1.data)    
    print('opponent:',response2.data)
    
    base_attack = response1.data[0]['base_attack']    
    base_defence = response2.data[0]['base_defence']  
    base_speed = response2.data[0]['base_speed']  
    base_stamina = response1.data[0]['base_stamina']  
    # 4. View your data 
    return [base_attack,base_defence,base_speed,base_stamina]
#print(load_player_info(selected_player,opponent))
