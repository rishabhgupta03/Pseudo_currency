import sqlite3


conn =sqlite3.connect("BANK_SYSTEM.db")
crsr = conn.cursor()
crsr.execute("""CREATE TABLE user(
                account_no integer(10),
                customer_first text,
                customer_last  text,
                account_bal real(20),
                account_type text,
                PRIMARY KEY(account_no))""")


crsr.execute("""CREATE TABLE passbook(
                date_time TEXT,
                account_no integer(10),
                amount real(20),
                trans  TEXT,
                account_bal real(20),
                FOREIGN KEY(account_no) REFERENCES user(account_no))""")

crsr.execute("""CREATE TABLE login(
                account_no integer(10),
                password integer(4),
                FOREIGN KEY(account_no) REFERENCES user(account_no))""")
print(crsr.fetchall())

conn.commit()
conn.close()