with tab1:
    st.header("📃金融資産一覧表")
    #* connect to finance.db
    conn = get_connection()
    cursor = conn.cursor()
    #* SELECT all values from finance table and store the data into finance.db 
    query = "SELECT * FROM finance"
    df = pd.read_sql_query(query, conn)
    
    #* Disconnect the database connection 
    conn.close()
    #* Dispaly a list of financial asset extracted from finance table and stored into df
    df_styled = df.style.format({"total_price": "{:,.0f}", "unit_price": "{:.0f}"})
    st.dataframe(df_styled, use_container_width=True, hide_index=True)

    #* store total values of each category2 in df_sum
    df_sum = df[["category2", "total_price"]].groupby("category2").sum()
    df_sum2 = df[["category1", "total_price"]].groupby("category1").sum()
    
    
    #* sort values stored in df_sum in descending order 
    df_sum = df_sum.sort_values(by="total_price", ascending=False)
    df_sum2 = df_sum2.sort_values(by="total_price", ascending=False) # df_sum2もソートしておきます

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

    # --- ▼▼▼ ここから修正 ▼▼▼ ---

    def create_pie_chart(df_grouped, title):
        """円グラフを作成して表示する関数"""
        
        # データが空の場合は何もしない
        if df_grouped.empty:
            st.warning(f"{title}のデータがありません。")
            return

        # 閾値を設定（例：合計の4%未満を「その他」にまとめる）
        threshold_percentage = 4.0
        total_value = df_grouped["total_price"].sum()
        
        # 割合が閾値未満の項目を「その他」として集約
        small_items = df_grouped[df_grouped["total_price"] / total_value * 100 < threshold_percentage]
        main_items = df_grouped[df_grouped["total_price"] / total_value * 100 >= threshold_percentage]

        plot_data = main_items.copy()
        if not small_items.empty:
            other_sum = small_items["total_price"].sum()
            other_row = pd.DataFrame({"total_price": [other_sum]}, index=["その他"])
            plot_data = pd.concat([plot_data, other_row])

        # 円グラフ描画用の値とラベルを準備
        value = plot_data["total_price"]
        label = plot_data.index

        # 「その他」があればそれを少し引き出す（explode）
        explode = [0.1 if i == "その他" else 0 for i in label]
        
        # 円グラフの描画
        fig, ax = plt.subplots(figsize=(8, 6)) # 少し大きめのサイズに

        def func(pct, allvals):
            absolute = int(round(pct/100.*sum(allvals)))
            return f"{pct:.1f}%\n({absolute:,d}円)"

        # autopctで値が小さいラベルは表示しないようにする
        wedges, texts, autotexts = ax.pie(
            value, 
            autopct=lambda pct: func(pct, value) if pct > threshold_percentage else '', # 閾値以下のラベルは非表示
            shadow=False, 
            startangle=90,
            explode=explode, # explodeを適用
            pctdistance=0.85 # ラベルの位置を内側に調整
        )
        
        # グラフ内のテキストのスタイルを設定
        plt.setp(autotexts, size=10, weight="bold", color="white")

        ax.axis("equal")
        ax.legend(label, loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=10) # 凡例をグラフの右外側に配置
        plt.title(title, {"fontsize": 20})
        st.pyplot(fig)

    # 1つ目の円グラフ（用途別）を描画
    create_pie_chart(df_sum, "用途別円グラフ")

    st.subheader("用途別合計金額一覧表")
    df_styled_total = df_sum.style.format({"total_price": "{:,.0f}"})
    st.dataframe(df_styled_total)

    # 2つ目の円グラフ（資金別）を描画
    create_pie_chart(df_sum2, "資金別円グラフ")

    # --- ▲▲▲ ここまで修正 ▲▲▲ ---

    with tab2:
      # (tab2以下のコードは変更なし)
      ...
    
    with tab3:
      # (tab3以下のコードは変更なし)
      ...
