#* 【ライブラリのインポート】 | sqlite3はPython標準ライブラリのため、追加インストールは必要ない
import sqlite3

#*【DBへの接続】
#*"finance.db"というファイル名のDBに接続。 | "finance.db"というファイルが存在しなければ新規で作成。
#* "conn"という変数に"finance.db"への接続情報を格納。
conn = sqlite3.connect("finance.db")
#*カーソルの作成 | カーソルとはDBに対しSQLクエリ(命令文)を実行したり、結果を取得するためのもの。
c = conn.cursor()

#*【DB内に新規テーブルの作成】
#* "c.execute"文では"finance"というテーブル名がDB内にまだ存在しなければ作成する。
#* "PRIMARY KEY"は各行を一位に特定するための識別子で、"AUTOINCREMENT"で作成の度自動で連番が振られる。
#* INTEGER = 整数型(-922京~+922京まで格納可能), REAL = 少数型, TEXT = 文字列, NOT NULL = 空白禁止
c.execute("""
CREATE TABLE IF NOT EXISTS finance(
id INTEGER PRIMARY KEY AUTOINCREMENT,
date TEXT NOT NULL,
title TEXT NOT NULL,
account_name TEXT NOT NULL,
category1 TEXT NOT NULL,
category2 TEXT NOT NULL,
purchased_number INTEGER,
unit_price REAL,
total_price INTEGER NOT NULL
)
""")

#*"finance_data"という空のリストを作成し、この中に(タプル)で囲まれた各行のデータを格納する。
#* 実際には("date:2024-11-18","title:アステラス製薬","account_name:楽天証券_Y","category1:株式","category2:投資資金","purchased_number:5","unit_price:1,650","total_price:8,250")というvalueが記載されている
finance_data =[
]

#*"c.executemany"文は"finance_data"から1タプルずつ抜き出し、"?"に各値のデータを渡す。
#*"finance_data"の部分は[リスト内に(各タプルが存在する形式である必要がある),(),(),()...]
#* "values(?,?,?...)"の数と、"finance_data"リスト内の各タプル内の値の数が同一である必要がある。
#*"?"というプレースホルダーを使うのは値をただの文字列や数値として扱い、SQLインジェクションを防ぐため。
c.executemany("INSERT INTO finance (date, title, account_name, category1, category2, purchased_number, unit_price, total_price) VALUES(?,?,?,?,?,?,?,?)", finance_data)

#*テーブルの作成・データの挿入といった、DBへの変更を確定、保存する。
conn.commit()
#*DBとの接続を閉じる。メモリ側のリソースを解放するために必須。
conn.close()
print("データベースを作成しました。")

