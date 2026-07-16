import sqlite3

def add_users(user_id,amount):
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("""INSERT INTO USERS(USER_ID,AMOUNT) VALUES(?,?)
                        ON CONFLICT(USER_ID)
                        DO UPDATE SET AMOUNT=AMOUNT+?""",(user_id,amount,amount))
        conn.commit()

def get_credentials(product):
        conn=sqlite3.connect('stock.db')
        cur=conn.cursor()
        if product=='GEMINI':
                cur.execute(f"""SELECT ID,LINK FROM {product} WHERE STATUS='available'""")
                cred=cur.fetchone()
        else:
                cur.execute(f"""SELECT ID,EMAIL,PASSWORD FROM {product} WHERE STATUS='available'""")
                cred=cur.fetchone()
        return cred

def fetch_funds(chat_id):
        conn=sqlite3.connect('users.db')
        cur=conn.cursor()
        cur.execute("SELECT AMOUNT FROM USERS WHERE USER_ID=?",(chat_id,))
        result=cur.fetchone()
        if result:
                return result[0]
        return 0

def update_funds(amount,chat_id):
        conn=sqlite3.connect('users.db')
        cur=conn.cursor()
        cur.execute("""UPDATE USERS SET AMOUNT=AMOUNT-? WHERE USER_ID=?""",(amount,chat_id))
        conn.commit()

def mark_sold(id,product):
        conn=sqlite3.connect('stock.db')
        cur=conn.cursor()
        cur.execute(f"UPDATE {product} SET STATUS='SOLD' WHERE ID=?",(id,))
        conn.commit()

def count_stock(product):
        conn=sqlite3.connect('stock.db')
        cur=conn.cursor()
        cur.execute(f"""SELECT COUNT(*) FROM {product} WHERE STATUS='available'""")
        count=cur.fetchone()[0]
        conn.close()
        return count

def store_order(chat_id,product,price,date,time):
        conn=sqlite3.connect('order_history.db')
        cur=conn.cursor()
        cur.execute("""INSERT INTO HISTORY(CHAT_ID,PRODUCT,PRICE,DATE,TIME) 
                VALUES(?,?,?,?,?)""",(chat_id,product,price,date,time))
        conn.commit()
        conn.close()

def get_order(chat_id):
        conn=sqlite3.connect('order_history.db')
        cur=conn.cursor()
        cur.execute("""SELECT PRODUCT,PRICE,DATE,TIME FROM HISTORY WHERE CHAT_ID=?""",(chat_id,))
        data=cur.fetchall()
        return data
