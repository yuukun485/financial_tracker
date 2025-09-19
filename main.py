#* 【ライブラリのインポート】
#* streamlit: UI構築, pandas: DBの操作・分析, matplotlib.pyplot: グラフの描画, matplotlib.font_manager: グラフ文字の日本語フォント対応
#* datetime: 日付・時刻を扱う, sqlite3: SQliteDBへの接続・SQLクエリの実行
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import datetime
import sqlite3

#* 【DBとの接続】
#* "finance.db"との接続を"get_connection"という関数で定義。
def get_connection():
    return sqlite3.connect("finance.db")

#*　【ブラウザタブの表示設定】
#* "page_icon"はブラウザタブに表示される"page_title"の左側に表示される
#* initial_sidebar_state ="auto"ではスマホサイズの時はサイドバーを表示しない | 今回のアプリではサイドバーはないので関係ない
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon=":moneybag:",
    layout="centered",
    initial_sidebar_state="auto"
)

#* 【セッション状態の管理】
#* セッションとは、アプリにユーザーがログインした瞬間から、ブラウザタブを閉じる or タイムアウトするまでの一連の期間を指す。
#* アプリにログイン時に"st.session_state"の中に、"data_updated"というフラグがないかを確認している。"data_updated"のフラグ名は開発者が任意で決めてOK。
#*  "st.session_state.data_updated = False"はDBがまだ更新されていない状態に設定している。
#* "tab2","tab3"でデータの登録・削除をする際に"st.session_state.data_updated = True"とすることで、DBに変更があったことをアプリ全体で共有する。
if "data_updated" not in st.session_state:
    st.session_state.data_updated = False

#* 【DBのデータをアプリ側のキャッシュに保存】
#* "@"はpythonのデコレーターという構文で、既存の関数に対して、関数の中身を一切変えることなく、新機能を追加できる役割を有している。
#* DBの"finance"テーブルから取得したデータをアプリケーションレベルのキャッシュとして保存している（ハードウェア側ではRAM「メインメモリ」に保存)
#* "ttl=600"では600秒間"finance"テーブルから取得した値をキャッシュに保持しており、10分間の内、キャッシュがクリアされない限りは新規でDBへアクセスが必要なくなる。
#* "tab2","tab3"でデータの登録・削除をした直後に"get_finance_data.clear()"でキャッシュを強制的に削除している。
#* キャッシュのクリア後には"st.rerun()"でアプリ全体を再実行しているため、再度"get_finance_data()"が呼び出され、DBから最新のデータを取得している
#* メリット1: 一度RAMに読み込んだデータを保存し、10分間はデータが更新されない限りDBに接続しなくていいので、DBへの接続負荷が下がる。
#* メリット2: DBがクラウド上 or 外部ディスク内に存在する場合に比べて、RAMからの読み込みは圧倒的に速い。

@st.cache_data(ttl=600)
def get_finance_data():
    conn = get_connection()
    query = "SELECT * FROM finance"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

#* 【メインタイトルとタブ】
#* "st.title()"はアプリ全体のメインタイトルを表示する。
#* "st.tabs"はページ移動を伴わずにタブの切り替えが可能である。
#* "tab1","tab2","tab3"には、"st.tabs()"ないの[リスト]ないの各値が格納される。
st.title("金融資産管理アプリ")
tab1, tab2, tab3 = st.tabs(["金融資産一覧表","金融資産登録フォーム","金融資産更新・削除"])

#* 【tab1: 金融資産一覧表・グラフの表示】
#* "st.header"でセクションのタイトルを表示する。
#* "get_finance_data()"関数を呼び出し、DBから取得したデータを"df"という変数に格納する。
#* この後、10分間はDBへの接続は行われず、アプリ側のキャッシュに保存されたデータを使用する。
with tab1:
    st.header("📃金融資産一覧表")
    df = get_finance_data()
#* 【グラフ用データの前準備】
#* "df.index[df["category1"] == "投資信託"]"は"category1"列の値が"投資信託"である行を特定し、各行のインデックス番号を"rakuten_rows"に格納している。
#* "df.index[df["category1"] != "投資信託"]"は"category1"列の値が"投資信託"以外である行を特定し、各行のインデックス番号を"other_rows"に格納している。
#* "df.index"でインデックス番号で取得している理由は、"df_styled"内の"subset"でインデックス番号を元に書式設定をするため。
    rakuten_rows = df.index[df["category1"] == "投資信託"]
    other_rows = df.index[df["category1"] != "投資信託"]
#* "df.style.format"はDataframeの表示スタイルを調整する構文であり、"category1"が"投資信託"の場合と、"投資信託"以外の場合で表示形式を変えている。
#* "total_price"部分は共通で、"{:,.0f}"で表記。 ","は千の位を区切るカンマを追加。".0"は小数点以下を0桁にするため、整数として表示。"f"は"float"として書式設定。
#* "unit_price"は"{:.6f}"で表記。".6"は小数点6位までを表示。"f"はfloatとして表記。
#* "subset=pd.IndexSlice[行の条件, :]"として指定することで、"unit_price"の表示を"投資信託"の種別毎に分類している。
    df_styled = df.style.format({"total_price": "{:,.0f}"}).format({"unite_price": "{:.6f}"}, subset=pd.IndexSlice[rakuten_rows,:]).format({"unit_price": "{:,.0f}"},subset=pd.IndexSlice[other_rows,:])
    st.dataframe(df_styled, use_container_width=True, hide_index=True)
#* "df_sum"には"category2"の項目別に"total_price"の合計額を格納。
#* "df_sum2"には"category1"の項目別に"total_price"の合計額を格納。    
    df_sum = df[["category2", "total_price"]].groupby("category2").sum()
    df_sum2 = df[["category1", "total_price"]].groupby("category1").sum()
#* "df_sum.sort_values"では、"total_price"を基準に降順に並び替えた結果を"df_sum"に格納。
#* "df_sum.sort_values"では、"total_price"を基準に降順に並び替えた結果を"df_sum2"に格納。
    df_sum = df_sum.sort_values(by="total_price", ascending=False)
    df_sum2 = df_sum2.sort_values(by="total_price", ascending=False)

#* 【金融資産合計額の表示】
#* "st.subheader"はセクションのサブタイトルを表示。
#* "df_sum_all"には"total_price"の総計が格納される。
#* "formatted_total"では、"f-string"を使うことで、"df_sum_all"という変数の千のくらいに","・末尾に"円"を付ける形で表示している。
#* "st.markdown"内で"<div></div>"というHTMLタグを使用して、36pxのフォントサイズ・合計値の下に30pxの空白を付けている。
#* "unsafe_alllow_html=True" はStreamlitにレンダリング時にHTML文字列を使っていることを教えるために必要となる。  
    st.subheader("全項目合計額")
    df_sum_all = df["total_price"].sum()
    formatted_total = f"{df_sum_all:,}円"
    st.markdown(f"<div style='font-size: 36px;'>{formatted_total}</div>",unsafe_allow_html=True)
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

#* 【matplotlibのグラフを日本語対応化】
#* "plt.rcParams['font.family']"では下記全てのグラフで使うデフォルトの文字をIPゴシック体に変更しており、セッションの間適応が継続される。
#* "@st.cache_resource"ではフォントの設定をアプリ側のキャッシュに保存しており、セッションの間適応が継続される。
#* "register_font()"という関数内でグラフで使用するフォントのパスを指定している。
#* "font_path"変数では同一フォルダ内にある"ipaexg.ttf"というフォント情報が記載されたTTFファイルを格納している。
#* "fm.fontManager.addfont(font_path)"では"ipaexg.ttf"で指定されたフォント情報をmatplotlibに一時的に登録し、グラフ描画時に使用している。
#* "register_font()"で関数を呼び出し、実行している。
    plt.rcParams['font.family'] = 'IPAexGothic'
    @st.cache_resource
    def register_font():
        font_path = 'ipaexg.ttf'
        fm.fontManager.addfont(font_path)
    register_font()

#*【グラフ描画用のデータ準備】
#* "category2"の各項目の合計額を"value"変数に代入する
#* "category2"の合計額で使われているインデックス番号を"label"に代入する
#* ".index"で各扇の名称が抜けるのは、"df.groupby("category2").sum()"を行った時点で各項目別合計額に対してのインデックス番号が振られているからである。
    value = df_sum["total_price"]
    label = df_sum.index
#* "category1"の各項目の合計額を"value2"変数に代入する
#* "category1"の合計額で使われているインデックス番号を"label2"に代入する
#* ".index"で各扇の名称が抜けるのは、"df.groupby("category1").sum()"を行った時点で各項目別合計額に対してのインデックス番号が振られているからである。
    value2 = df_sum2["total_price"]
    label2 = df_sum2.index

#* 【円グラフの描画】
#* "fig, ax = plt.subplots()"は定型分で"fig"が額縁として機能し、グラフそのものではなく、グラフが描かれるエリア全体となり、"ax"がキャンバスとなり、キャンバスに円グラフを描いていくことになる。
#* "def func(pct, allavals)"ではグラフの各項目毎にパーセント表示に加え、実数値での表示を行えるように定義している。
#* "pct"には"ax.pie"が自動的に計算したパーセントの値が格納される。(例:80.6)
#* "allvals"には"value"で取得済のカテゴリ2の各項目の合計額が渡される。
#* "absolute"変数には"sum(allvals)"で計算されたカテゴリ2の全項目合計額と"pct/100(80.6→0.86)"で計算された各扇の比率を掛け合わせた値を四捨五入した結果を整数として格納している。
#* "absolute"変数に格納されている値は扇の数分繰り返し変更して返される。
#* "{pct: .1f}"では小数点以下1桁までの値をパーセントで表示。(80.6%) "\n"は改行 "({absolute:,d}"円)"では千くらいで","区切りをしている。"d"はデータ型が10進数の整数(decimial integer)であることを規定している。
#* "ax.pie"の"value"にはCategory2の各項目別合計額が渡される。
#* "autopct=lambda pct: func(pct, value)"では"lamnbda pct(変数)"でパーセントの値を受け取り、その値をfunc関数に渡している。
#* func(pct, value)"では"pct"にパーセントの値、"value"にCategory2の各項目別合計額が渡される。
#* "shadow=False"はグラフに影を付けない設定。"startangle=90"は時計の12時の方向からグラフを開始する設定。"textprops={'fontsize': 6}"ではフォントサイズを6に設定。
#*　"autopct"はグラフ内の扇のパーセントの表示形式を指定するものであり、本来は"%.1%%"のように指定するが、今回はパーセントの下に数字も表示したいので、func関数を使っている。
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
                st.session_state.data_updated = True
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
        st.session_state.data_update = True
        st.rerun() # アプリを再実行 (変更点5)
