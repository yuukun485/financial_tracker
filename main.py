import streamlit as st
import pandas as pd
import sqlite3
import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


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

# st.session_stateの初期化 (変更点1)
if "data_updated" not in st.session_state:
    st.session_state.data_updated = False

# データベースからデータを取得する関数をキャッシュ (変更点2)
@st.cache_data(ttl=600)
def get_finance_data():
    conn = get_connection()
    query = "SELECT * FROM finance"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

#! main parts of this application
st.title("金融資産管理アプリ")

# divide functions based on tabs
tab1, tab2, tab3 = st.tabs(["金融資産一覧表","金融資産登録フォーム","金融資産更新・削除"])

#Display a list of financial asset
with tab1:
    st.header("📃金融資産一覧表")
    #* connect to finance.db
    # データ取得関数を呼び出すように変更 (変更点3)
    df = get_finance_data()
    
    #* Disconnect the database connection
    # conn.close() は関数内に移動済み
    #* Dispaly a list of financial asset extracted from finance table and stored into df
    rakuten_rows = df.index[df["category1"] == "投資信託"]
    other_rows = df.index[df["category1"] != "投資信託"]
    
    df_styled = df.style.format({"total_price": "{:,.0f}"}).format({"unite_price": "{:.6f}"}, subset=pd.IndexSlice[rakuten_rows,:]).format({"unit_price": "{:,.0f}"},subset=pd.IndexSlice[other_rows,:])
    st.dataframe(df_styled, use_container_width=True, hide_index=True)

    #* store total values of each category2 in df_sum
    df_sum = df[["category2", "total_price"]].groupby("category2").sum()
    df_sum2 = df[["category1", "total_price"]].groupby("category1").sum()
    
    
    #* sort values stored in df_sum in descending order
    df_sum = df_sum.sort_values(by="total_price", ascending=False)
    df_sum2 = df_sum2.sort_values(by="total_price", ascending=False)

    st.subheader("全項目合計額")
    df_sum_all = df["total_price"].sum()
    formatted_total = f"{df_sum_all:,}円"
    st.markdown(f"<div style='font-size: 36px;'>{formatted_total}</div>",unsafe_allow_html=True)
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    #* how to correspond with japanese
    plt.rcParams['font.family'] = 'IPAexGothic'
    @st.cache_resource
    def register_font():
        font_path = 'ipaexg.ttf'
        fm.fontManager.addfont(font_path)
    register_font()

    #* Variables for pie chart
    value = df_sum["total_price"]
    label = df_sum.index

    value2 = df_sum2["total_price"]
    label2 = df_sum2.index

    fig, ax = plt.subplots()
    def func(pct, allvals):
        absolute = int(round(pct/100.*sum(allvals)))
        return f"{pct:.1f}%\n({absolute:,d}円)"
    ax.pie(value,autopct=lambda pct: func(pct, value), shadow=False, startangle=90, textprops={'fontsize': 6})
    ax.axis("equal")
    ax.legend(label, loc="center right", bbox_to_anchor=(1,0,0.5,1))
    plt.title("用途別円グラフ",{"fontsize": 20})
    st.pyplot(fig)
    
    st.subheader("用途別合計金額一覧表")
    df_styled_total = df_sum.style.format({"total_price": "{:,.0f}"})
    st.dataframe(df_styled_total)

    fig2, ax2 = plt.subplots()
    def func(pct, allvals):
        absolute = int(round(pct/100.*sum(allvals)))
        return f"{pct:.1f}%\n({absolute:,d}円)"
    ax2.pie(value2, autopct=lambda pct: func(pct, value2), shadow=False, startangle=90, textprops={'fontsize': 6})
    ax2.axis("equal")
    ax2.legend(label2, loc="center right", bbox_to_anchor=(1,0,0.5,1))
    plt.title("資産別円グラフ",{"fontsize": 20})
    st.pyplot(fig2)

    
    st.subheader("資産別合計金額一覧表")
    
    df_styled_total = df_sum2.style.format({"total_price": "{:,.0f}"})
    st.dataframe(df_styled_total)

    
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
        unit_price = st.number_input(label="単価", value=0.0, step=0.00001, format="%.6f")
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
                get_finance_data.clear() # キャッシュをクリア (変更点4)
                st.rerun() # アプリを再実行 (変更点5)
            else:
                st.warning("必須項目が未入力です")
with tab3:
    st.subheader("➖削除フォーム")
    # データ取得関数を呼び出すように変更 (変更点3)
    df = get_finance_data()
    rakuten_rows = df.index[df["category1"] == "投資信託"]
    other_rows = df.index[df["category1"] != "投資信託"]
    df_styled = df.style.format({"total_price": "{:,.0f}"}).format({"unite_price": "{:.6f}"}, subset=pd.IndexSlice[rakuten_rows,:]).format({"unit_price": "{:,.0f}"},subset=pd.IndexSlice[other_rows,:])
    st.dataframe(df_styled, use_container_width=True, hide_index=True)


    #* type an id number to delete from finance table
    id_number_to_delete = st.number_input("削除するid番号を入力", min_value = 0)

    #* if a button is clicked, an id number typed in the textbox is deleted
    if st.button("データを削除"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM finance WHERE id =?", (id_number_to_delete,))
        conn.commit()
        conn.close()
        st.success(f"id番号{id_number_to_delete}を削除しました。")
        get_finance_data.clear() # キャッシュをクリア (変更点4)
        st.rerun() # アプリを再実行 (変更点5)
