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
finance_data =[
]

c.executemany("INSERT INTO finance (date, title, account_name, category1, category2, purchased_number, unit_price, total_price) VALUES(?,?,?,?,?,?,?,?)", finance_data)

#* terminate a transaction and confirm changes 
conn.commit()

#* disconnect the database connection
conn.close()
print("データベースを作成しました。")

