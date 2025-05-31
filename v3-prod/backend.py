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

    
    st.write("Blended CTR:", blended_ctr)


no_of_temp = st.number_input("Enter your Desired Templates:", min_value=1, max_value=10)


other_additional_prompt = st.text_input("Enter your desired prompt to get the most relevant outcome")


list_no = tb_df["Merged"].tolist()

load_dotenv()
google_api = os.getenv("GOOGLE_API_KEY")



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

# Only show button and trigger generation if a user has typed a prompt

if st.button("Generate Templates"):
        formatted_prompt_2 = prompt_2.format(reference_templates=str(list_no))
        user_message = f"{formatted_prompt_2}\n\nNumber of templates to generate: {no_of_temp}\n\n{other_additional_prompt}"

        messages_2 = [
            ("system", "You are a creative AI assistant specialized in writing engaging notification templates."),
            ("human", user_message)
        ]

        # Invoke the model and display
        ai_response = llm.invoke(messages_2)
        st.subheader("Generated Notification Templates:")
        st.write(ai_response.content)

