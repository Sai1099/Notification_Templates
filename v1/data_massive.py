import pandas as pd
from pandasql import sqldf
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import requests
import io




def compute_file(output_file):
 df = pd.read_csv(io.StringIO(output_file.getvalue().decode('utf-8')))




 df['Merged'] = df['Message_title'] + ' ' + df['Message_body']

 df.drop(['Identity','Message_title','Message_body','Event_Captured_DT'],axis=1,inplace=True)

 #print(df.head())

 query = "SELECT SUM(Notification_Clicked) as Notification_Clicked,SUM(PUSH_IMPRESSION) as Push_Imp,Merged FROM df GROUP BY Merged;"

 pysql = sqldf(query)
 
 pysql['CTR'] = pysql['Notification_Clicked'] / pysql['Push_Imp'].replace(0, 1)

 query_1 = "SELECT Notification_Clicked,Push_Imp,Merged,CTR FROM pysql WHERE Notification_Clicked >= 5 AND Push_Imp >= 5 ORDER BY CTR DESC;"
 main_df = sqldf(query_1)

 print(main_df)
 main_df.to_csv("get_things.csv")

 features  = main_df[['Notification_Clicked','Push_Imp','CTR']]


 scaler = StandardScaler()

 scaled_features = scaler.fit_transform(features)

 kmean_algo = KMeans(n_clusters=3,random_state=42)

 main_df['Cluster'] = kmean_algo.fit_predict(scaled_features)
 list_no = []  # Initialize as a list

 if (main_df['Cluster'] == 2).any():
    
    if df['Merged'].count() >= 5:
        predicted_template = main_df.head(5)
    else:
        predicted_template = main_df.head(df['Merged'].count())

 list_no.extend(predicted_template['Merged'].tolist())  

 prompt = f"""You are an assistant that rewrites messages professionally.

Message: {list_no}

Generate Similar Messages as Above and be professional. Respond with:
- Message Title:
- Message Body:"""

 response = generate_with_llama2(prompt)


 return f"**Predicted Template:** {predicted_template}\n\n**Generated Content:**\n{response}"
#
# print(main_df.groupby('Cluster').mean()) 