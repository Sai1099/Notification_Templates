import streamlit as st
import pandas as pd
from pandasql import sqldf
import os
import getpass
from langchain.prompts import load_prompt
from dotenv import load_dotenv
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
import json


st.set_page_config(page_title="Recommendation", page_icon="::fire::", layout="wide")

st.title("Recommending the best templates")

# Load Data
main_df = pd.read_csv("Notification_Data_4.csv")
businesses = main_df["Bussiness"].unique()

# Select Business
option = st.selectbox("Choose your Business:", businesses)

# Top Templates
top_template_count = st.number_input(
    "Enter how many top templates you want from the initial data:", value=1
)

if option:
    QUERY = f"SELECT * FROM main_df WHERE Bussiness = '{option}';"
    df = sqldf(QUERY)

    df["Merged"] = df["Message_title"] + " " + df["Message_body"]
    df.drop(["Event_Captured_DT", "Identity"], axis=1, inplace=True)

    query = """
        SELECT SUM(Notification_Clicked) as Notification_Clicked, 
               SUM(PUSH_IMPRESSION) as Push_Imp, 
               Merged 
        FROM df 
        GROUP BY Merged;
    """
    pysql = sqldf(query)
    pysql["CTR"] = pysql["Notification_Clicked"] / pysql["Push_Imp"]

    query_1 = "SELECT * FROM pysql ORDER BY CTR DESC;"
    main_df = sqldf(query_1)
    nad = sqldf(query_1)
    tb_df = nad.head(top_template_count)

    blended_ctr = tb_df["Notification_Clicked"].sum() / tb_df["Push_Imp"].sum()

    st.dataframe(tb_df)
    st.write("Blended CTR:", blended_ctr)
else:
    st.write("Select the option")

no_of_temp = st.number_input("Enter your Desired Templates:", min_value=1, max_value=10)

# Optional User Prompt
other_additional_prompt = st.text_input("Enter your desired prompt to get the most relevant outcome")

# Prepare the list of templates
list_no = tb_df["Merged"].tolist()

# Load environment variables and API key
load_dotenv()
google_api = os.getenv("GOOGLE_API_KEY")


# Load the JSON Prompt
base_dir = os.path.dirname(os.path.abspath(__file__))
prompt_2_path = os.path.join(base_dir, "prompt_2.json")
prompt_2 = load_prompt(prompt_2_path)

# Initialize the Language Model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# hey youuu
if other_additional_prompt:
    if st.button("Generate Templates"):
        formatted_prompt_2 = prompt_2.format(reference_templates=str(list_no))
        user_message = f"{formatted_prompt_2}\n\nNumber of templates to generate: {no_of_temp}\n\n{other_additional_prompt}"

        messages_2 = [
            ("system", "You are a creative AI assistant specialized in writing engaging notification templates.and please give me the output in the json format only "),
            ("human", user_message)
        ]

        # Invoke the model and display
        ai_response = llm.invoke(messages_2)
        st.subheader("Generated Notification Templates:")
        st.write(ai_response.content)
        json_content = ai_response.content
        if json_content:
          def parsing_lines(json_content):
           json_content = str(json_content)
           start_idx = json_content.find("[")
           end_idx = json_content.find("]")
           main_json = json_content[start_idx:end_idx+1]
           msn  = json.loads(main_json)
           return msn

main_json_file = parsing_lines(json_content)
max_templates_generated = len(main_json_file)
print(len(main_json_file))
print()
print(parsing_lines(json_content))                 
"""
def image_using_stablediffusion():
 api_key = os.getenv("API_KEY")
 api_url = os.getenv("API_URL")
no_of_des_img_temmp = st.number_input("Enter the Desired Images Templates",max_value=max_templates_generated,min_value=1)
style = st.selectbox("Select Your Style:",['Modern','Festive','Financial'])
if style == prompts[style]:
   for i in no_of_des_img_temmp:
      title = main_json_file[f"Template {i}"]["Message Title"]
      body = main_json_file[f"Template {i}"]["Message Body"]




"""

def prompts():
 prompts = {
        "modern": f"""
            Modern mobile notification card design, clean white background, 
            rounded corners, blue app icon on left, professional typography.
            Title text: "{title}"
            Body text: "{body}"
            Style: iOS notification interface, minimal design, proper spacing
        """,
        
        "festive": f"""
            Festive holiday notification card, warm colors, golden accents,
            celebration theme with sparkles and holiday elements.
            Title: "{title}"
            Message: "{body}"
            Style: Christmas theme, joyful colors, premium design
        """,
        
        "financial": f"""
            Professional banking notification, corporate blue colors,
            trustworthy design, clean layout, financial app interface.
            Notification title: "{title}"
            Transaction details: "{body}"
            Style: fintech app, secure design, business professional
        """,
        
        "vibrant": f"""
            Colorful gradient notification design, modern mobile interface,
            bright purple and pink gradients, energetic style.
            Alert title: "{title}"
            Alert message: "{body}"
            Style: social media app, trendy colors, engaging design
        """
       }
 return None