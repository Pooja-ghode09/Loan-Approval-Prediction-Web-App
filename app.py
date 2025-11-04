import streamlit as st
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
from mysql.connector import Error

st.markdown("""
<style>
    .main {
        background-color: #f9fafc;
    }
    .css-1d391kg {
        background-color: #e8f0fe;
    }
    h1, h2, h3 {
        color: #0a66c2;
    }
</style>
""", unsafe_allow_html=True)


# Load trained model
model = joblib.load('loan_model.pkl')

st.title("Loan Approval Prediction App")

# -------------------------------
#  File Upload Section
# -------------------------------
st.sidebar.header("Upload Loan Data (CSV)")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.write("### Uploaded Data Preview:")
    st.dataframe(data.head())
else:
    st.info("Upload a CSV file to see visualizations.")

# -------------------------------
#  Optional: Filter Section
# -------------------------------
if uploaded_file is not None:
    st.sidebar.subheader("Filter Data")

    # Handle NaN safely
    credit_options = data['Credit_History'].dropna().unique().tolist()

    credit_filter = st.sidebar.multiselect(
        "Select Credit History:",
        options=credit_options,
        default=credit_options
    )

    # Filter dataset
    filtered_data = data[data['Credit_History'].isin(credit_filter)]

    st.write("### Filtered Data")
    st.dataframe(filtered_data)


# -------------------------------
#  Data Visualization Section
# -------------------------------
if uploaded_file is not None:
    st.subheader("Data Visualization")

    # Loan Approval Distribution
    if 'Loan_Status' in filtered_data.columns:
        st.write("### Loan Approval Distribution")
        fig1, ax1 = plt.subplots()
        sns.countplot(x='Loan_Status', data=filtered_data, palette='Set2', ax=ax1)
        st.pyplot(fig1)

    # Income vs Loan Amount
    if 'ApplicantIncome' in filtered_data.columns and 'LoanAmount' in filtered_data.columns:
        st.write("### Applicant Income vs Loan Amount")
        fig2, ax2 = plt.subplots()
        sns.scatterplot(x='ApplicantIncome', y='LoanAmount', hue='Loan_Status', data=filtered_data, ax=ax2)
        st.pyplot(fig2)

    # Average Income Bar Chart
    st.write("### Average Applicant Income by Loan Status")
    avg_income = filtered_data.groupby('Loan_Status')['ApplicantIncome'].mean().reset_index()
    fig3, ax3 = plt.subplots()
    sns.barplot(x='Loan_Status', y='ApplicantIncome', data=avg_income, palette='coolwarm', ax=ax3)
    st.pyplot(fig3)

# -------------------------------
#  Prediction Section
# -------------------------------
st.subheader("Predict Loan Approval")

income = st.number_input("Applicant Income", min_value=0)
loan_amount = st.number_input("Loan Amount", min_value=0)
credit_history = st.selectbox("Credit History", [0, 1])

if st.button("Predict"):
    features = np.array([[income, loan_amount, credit_history]])
    prediction = model.predict(features)
    result = "Approved" if prediction[0] == 1 else "Rejected"

    # Display result
    if result == "Approved":
        st.success(" Loan Approved!")
        st.info(f"Reason: Good Credit History ({credit_history}) and Sufficient Income ({income})")
    else:
        st.error("Loan Rejected!")
        st.warning(f"Reason: Low Credit History ({credit_history}) or High Loan Amount ({loan_amount})")

    # Save to MySQL
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Sveri#67717713",  # change this
            database="loan_db"
        )
        cursor = connection.cursor()
        query = "INSERT INTO loan_predictions (income, loan_amount, credit_history, prediction) VALUES (%s, %s, %s, %s)"
        data = (income, loan_amount, credit_history, result)
        cursor.execute(query, data)
        connection.commit()
        st.success(" Data saved successfully to MySQL!")
    except Exception as e:
        st.error(f"Database Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


 

