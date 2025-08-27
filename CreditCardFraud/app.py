import streamlit as st 
import pandas as pd
import numpy as np
import joblib
import lightgbm as lgb
from geopy.distance import geodesic
from pathlib import Path

model = joblib.load(Path('model/CC_fraud_model.jb'))
encode = joblib.load(Path('model/encoders.jb'))

def haversine(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

st.title('Credit Card  fraud detection')
st.write('Enter the transaction details below')

merchant  = st.text_input('merchant Name')
category = st.text_input('Category')
amt  = st.number_input('Amount')
gender = st.selectbox('gender',['Male', 'Female'])
lat  = st.number_input('latitude')
lon = st.number_input('Longitube')
merch_lat  = st.number_input('merchant latitude')
merch_long = st.number_input('marchant longitude')
hour = st.slider('transaction hour', 0, 23, 12)
month = st.slider('transaction month',1, 12, 6 )
day = st.slider('transaction day', 1, 31, 15)
cc_num = st.number_input('Credit card number')

distance = haversine(lat, lon, merch_lat, merch_long)

if st.button('Check the Fraud'):
    if merchant and category and cc_num:
        input_data = pd.DataFrame([[hour, month, day,cc_num, merchant, category, amt, gender, distance]], 
                                    columns=['hour', 'month', 'day', 'cc_num', 'merchant', 'category', 'amt', 'gender', 'distance'])
        
        catgorical_col = ['merchant', 'gender', 'category']
        for col in catgorical_col:
            try:
                input_data[col] = encode[col].transform(input_data[col])
            except ValueError:
                input_data[col] = -1
        input_data['cc_num'] = input_data['cc_num'].apply(lambda x: hash(x) % (10 ** 2))
        predcition = model.predict(input_data)[0]
        st.write(f'Prediction made by the model: {predcition}')

        result = 'Farudulant transaction' if predcition == 1 else 'legitimate transaction'
        st.subheader(f'Prediction: {result}')
    else:
        st.error('Please fill all the required values')