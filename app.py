# app.py
import streamlit as st
import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load data
iris = load_iris()
X = iris.data
y = iris.target

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save model
joblib.dump(model, 'iris_model.joblib')

# Load model
model = joblib.load('iris_model.joblib')

# Judul aplikasi
st.title('Aplikasi Prediksi Iris')

# Input pengguna
st.header('Masukkan Karakteristik Bunga Iris')
sepal_length = st.slider('Panjang Sepal (cm)', 4.0, 8.0, 5.0)
sepal_width = st.slider('Lebar Sepal (cm)', 2.0, 4.5, 3.0)
petal_length = st.slider('Panjang Petal (cm)', 1.0, 7.0, 4.0)
petal_width = st.slider('Lebar Petal (cm)', 0.1, 2.5, 1.0)

# Prediksi
if st.button('Prediksi'):
    input_data = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
    prediction = model.predict(input_data)
    
    # Mapping prediksi ke nama spesies
    species = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
    st.subheader(f'Hasil Prediksi: {species[prediction[0]]}')
    
    # Tambahkan visualisasi (opsional)

    st.bar_chart(model.predict_proba(input_data)[0])


