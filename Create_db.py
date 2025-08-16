import sqlite3

#* Connect to a finance.db | If the database doesnt exsit, a new database is automatically created 
conn = sqlite3.connect("finance.db")

#* The mechanism to process search results of a database line by line 
c = conn.cursor()

#* execute is a method to execute sql-query | It is a common practice to write codes of SQL in capital letters
#* finance table is created within finance.db 
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

#* Add sample datas into finance table
finance_data =[
]

#* insert finance_data into finance table 
#* ? is a placeholder 
c.executemany("INSERT INTO finance (date, title, account_name, category1, category2, purchased_number, unit_price, total_price) VALUES(?,?,?,?,?,?,?,?)", finance_data)

#* terminate a transaction and confirm changes 
conn.commit()

#* disconnect the database connection
conn.close()
print("データベースを作成しました。")

