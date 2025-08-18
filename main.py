import streamlit as st 
import pandas as pd 
import sqlite3
import datetime
import matplotlib.pyplot as plt 

#* function to return a database created in Create_db.py
def get_connection():
    return sqlite3.connect("finance.db")

# Page Settings 
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon=":moneybag:",
    layout="centered",
    initial_sidebar_state="expanded"
)

#! main parts of this application
st.title("金融資産管理アプリ")

# divide functions based on tabs 
tab1, tab2, tab3 = st.tabs(["金融資産一覧表","金融資産登録フォーム","金融資産更新・削除"])

#Display a list of financial asset 
with tab1:
    st.subheader("📃金融資産一覧表")
    #* connect to finance.db
    conn = get_connection()
    #* SELECT all values from finance table and store the data into finance.db 
    query = "SELECT * FROM finance"
    df = pd.read_sql_query(query, conn)
    #* Disconnect the database connection 
    conn.close()
    #* Dispaly a list of financial asset extracted from finance table and stored into df
    st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("➕新規登録フォーム")
        #* allow users to input values in text boxes, submit them and register them into finance.db 
        with st.form("registration form", clear_on_submit=True):
            default_date = datetime.date(2025,8,1)
            date = st.date_input(label="日付", value=default_date)
            title = st.text_input(label="タイトル", max_chars=200)
            account_name = st.text_input(label="アカウント名", max_chars=200)
            category1 = st.text_input(label="カテゴリ1", max_chars=200)
            category2 = st.text_input(label="カテゴリ2", max_chars=200)
            purchased_number = st.number_input(label="数量", value=0, step=1)
            unit_price = st.number_input(label="単価", value=0, step=1)
            total_price = st.number_input(label="合計", value=0, step=1)

            submitted = st.form_submit_button("登録する")

            if submitted:
                if date and title and account_name and category1 and category2 and total_price:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO finance(date, title, account_name, category1, category2, purchased_number, unit_price, total_price) VALUES(?,?,?,?,?,?,?,?)",
                        (date, title, account_name, category1, category2, purchased_number, unit_price, total_price)
                    )
                    conn.commit()
                    conn.close()
                    st.success("登録完了")
                else:
                    st.warning("必須項目が未入力です")
with tab3:
    st.subheader("➖削除フォーム申請")
    conn = get_connection()
    query = "SELECT * From finance"
    df = pd.read_sql_query(query, conn)
    st.dataframe(df, use_container_width=True, hide_index=True)

