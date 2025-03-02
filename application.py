import streamlit as st
import numpy as np
import pickle
import pandas as pd


with open("model_random_forest.pkl", "rb") as f:
    model = pickle.load(f)

# Set page configuration
st.set_page_config(
    page_title="Medicare Cost Predictor",
    page_icon="🏥",
    layout="centered"
)

# Sample user credentials (for demo)
USER_CREDENTIALS = {"admin": "password123", "user1": "1234", "user2":"56789"}

# Function to authenticate user
def authenticate(username, password):
    return USER_CREDENTIALS.get(username) == password

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- LOGIN PAGE ---
if not st.session_state.authenticated:
    st.title("Login To Predict your Procedure Cost")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.authenticated = True
            # st.experimental_rerun()
        else:
            st.error("Invalid Username or Password")
else:
    # --- PREDICTION PAGE ---
    st.title("Procedure Cost Predictor 🏥💳")

    # Select inputs
    #select box for DRG Code
    dict_drg={}
    df_drg_info=pd.read_csv('drg_info.csv')

    for i in range(0,len(df_drg_info)):
        dict_drg[df_drg_info['drg_code'][i]]=df_drg_info['drg_code_id'][i]
    drg_code = st.selectbox("Select your Procedure Name with Code 🩺", dict_drg, key='selectbox1')

    #selectbox for provider name
    #copy this and paste in application.py
    dict_provider_name={}
    df_provider_name_info=pd.read_csv('provider_name_info.csv')

    for i in range(0,len(df_provider_name_info)):
        dict_provider_name[df_provider_name_info['provider_name'][i]]=df_provider_name_info['provider_name_id'][i]
    provider_name = st.selectbox("Select the Hospital 🏥", dict_provider_name, key='selectbox2')

    #selectbox for Provider City
    dict_provider_city={}
    df_provider_city=pd.read_csv('provider_info.csv')

    for i in range(0,len(df_provider_city)):
        dict_provider_city[df_provider_city['provider_city'][i]]=df_provider_city['provider_city_id'][i]
    city = st.selectbox("Select the City 🌆", dict_provider_city, key='selectbox3')
  

    def validate(drg_code,city_nm,provider_nm):
        inpatient_data = pd.read_csv('Medicare_Provider_Charge_Inpatient_DRG100_FY2011.csv')
        cols=['DRG Definition','Provider Name','Provider City']
        data_req = inpatient_data[cols]

        city = data_req[data_req['DRG Definition']==drg_code]['Provider City']
        provider = data_req[data_req['DRG Definition']==drg_code]['Provider Name']

        city_list = city.values.tolist()
        provider_list = provider.values.tolist()

        if city_nm not in city_list:
            return "This Procedure is not supported in the given city"
        if provider_nm not in provider_list:
            return "This Procedure is not supported in the given Hospital"
        if city_nm in city_list:
            prov_df =  data_req[(data_req['DRG Definition']==drg_code) & (data_req['Provider City']==city_nm)]['Provider Name'] 
            prov_list = prov_df.values.tolist()
            if provider_nm not in prov_list:
                return "The Hospital is not present in the city."
            else:
                return ""
        else:
            return ""
    

    validation_val = validate(drg_code,city,provider_name)
    
        # Predict button
    if st.button("Predict Cost"):
        validation_val = validate(drg_code,city,provider_name)
        if validation_val == "":
            input_data = np.array([[dict_drg[drg_code],dict_provider_name[provider_name],dict_provider_city[city]]])
            prediction = model.predict(input_data)
            st.write(f"This Procedure will cost you approximately 💵 USD {prediction[0]:.2f}")
        else:
            st.write(validation_val)
    
       
    