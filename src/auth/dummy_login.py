import sqlite3

def login_user(username, password):
    # DANGEROUS: Classic SQL Injection vulnerability!
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    
    user = cursor.fetchone()
    if user:
        return True
    return False
