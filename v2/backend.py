from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain.prompts import load_prompt
import getpass
import os
from dotenv import load_dotenv
from pandasql import sqldf
import pandas as pd
import json

load_dotenv()
google_api = os.getenv("GOOGLE_API_KEY")

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")


base_dir = os.path.dirname(os.path.abspath(__file__))


prompt_1_path = os.path.join(base_dir, "prompt_1.json")
prompt_2_path = os.path.join(base_dir, "prompt_2.json")







prompt_1 = load_prompt(prompt_1_path)
prompt_2 = load_prompt(prompt_2_path)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

input_msg = "for pl business I need the 7 best templates"
#input_msg = str(input())


formatted_prompt_1 = prompt_1.format(input_msg=input_msg)


messages = [
    ("system", "You are a helpful AI assistant that extracts parameters from user input."),
    ("human", formatted_prompt_1),
]

ai_msg = llm.invoke(messages)


def parse_response(response_content):
    params = {"day_param": 30, "no_of_temp_params": 5, "bussiness_type_param": "pl"}  # Default values
 
    try:
      
        response_content = response_content.strip()
        if response_content.startswith('```json'):
            response_content = response_content.replace('```json', '').replace('```', '').strip()
        elif response_content.startswith('```'):
            response_content = response_content.replace('```', '').strip()
        
        json_data = json.loads(response_content)
        
        if 'daY_param' in json_data:
            params["day_param"] = int(json_data['daY_param'])
        if 'no_of_temp' in json_data:
            params["no_of_temp_params"] = int(json_data['no_of_temp'])
        if 'bussiness_type_param' in json_data:
            params["bussiness_type_param"] = str(json_data['bussiness_type_param'])
            
        return params
    except (json.JSONDecodeError, KeyError, ValueError):
       
        print("JSON parsing failed, falling back to line parsing...")
        
 
    lines = response_content.split("\n")
    for line in lines:
        line = line.strip(',')
        if 'daY_param' in line:
            try:
                params["day_param"] = int(line.split(':')[1].strip())
            except (ValueError, IndexError):
                pass
        if 'no_of_temp' in line:
            try:
                params["no_of_temp_params"] = int(line.split(':')[1].strip())
            except (ValueError, IndexError):
                pass
        if 'bussiness_type_param' in line:
            try:
                params["bussiness_type_param"] = str(line.split(':')[1].strip().strip('"\''))
            except IndexError:
                pass

    return params

params = parse_response(ai_msg.content)

day_param = params["day_param"]
no_of_temp_params = params["no_of_temp_params"]
bussiness_type_params = params["bussiness_type_param"]

print(f"Extracted Parameters: day_param={day_param}, no_of_temp_params={no_of_temp_params}, bussiness_type_params={bussiness_type_params}")

def get_data_from_db(day_param, bussiness_type_params):
    query = f"""
        SELECT Message_title, Message_body, Event_Captured_DT, PUSH_IMPRESSION, Notification_Clicked 
        FROM db_table 
        WHERE Event_Captured_DT >= DATE_SUB(CURRENT_DATE(), INTERVAL {day_param} DAY) 
        AND business_type = '{bussiness_type_params}';
    """
   #examples
    return pd.DataFrame([
        {"Message_title": "Hello User", "Message_body": "Welcome to our service!", "Event_Captured_DT": "2024-06-01", "PUSH_IMPRESSION": 50, "Notification_Clicked": 10},
        {"Message_title": "Special Offer", "Message_body": "Exclusive deal inside!", "Event_Captured_DT": "2024-06-02", "PUSH_IMPRESSION": 100, "Notification_Clicked": 20},
        {"Message_title": "Limited Time", "Message_body": "Act now before it's gone!", "Event_Captured_DT": "2024-06-03", "PUSH_IMPRESSION": 75, "Notification_Clicked": 25},
        {"Message_title": "New Features", "Message_body": "Check out what's new!", "Event_Captured_DT": "2024-06-04", "PUSH_IMPRESSION": 80, "Notification_Clicked": 15},
        {"Message_title": "Weekend Sale", "Message_body": "Save big this weekend!", "Event_Captured_DT": "2024-06-05", "PUSH_IMPRESSION": 120, "Notification_Clicked": 30},
    ])

df = get_data_from_db(day_param, bussiness_type_params)

def compute_file(df):
    if df.empty:
        print("No data available.")
        return pd.DataFrame()

    df["Merged"] = df["Message_title"] + " " + df["Message_body"]
    df.drop(["Event_Captured_DT"], axis=1, inplace=True)

    query = """
        SELECT SUM(Notification_Clicked) as Notification_Clicked, 
               SUM(PUSH_IMPRESSION) as Push_Imp, 
               Merged 
        FROM df 
        GROUP BY Merged;
    """
    pysql = sqldf(query)
    pysql["CTR"] = pysql["Notification_Clicked"] / pysql["Push_Imp"].replace(0, 1)

    query_1 = "SELECT * FROM pysql WHERE Push_Imp >= 5 ORDER BY CTR DESC;"
    main_df = sqldf(query_1)

    return main_df


main_df = compute_file(df)


predicted_template = main_df.head(no_of_temp_params)


list_no = predicted_template["Merged"].tolist()


formatted_prompt_2 = prompt_2.format(reference_templates=str(list_no))


messages_2 = [
    ("system", "You are a creative AI assistant specialized in writing engaging notification templates."),
    ("human", formatted_prompt_2 + str(no_of_temp_params)),
]

ai_response = llm.invoke(messages_2)

print(f"\n**Predicted Templates:**\n{predicted_template}")
print(f"\n**Generated Content:**\n{ai_response.content}")