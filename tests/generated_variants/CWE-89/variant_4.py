import sqlite3
def cwe89_variant_4(user_input):
    conn = sqlite3.connect(':memory:')
    conn.execute(f'SELECT * FROM users WHERE name = {user_input}')

if __name__ == '__main__':
    cwe89_variant_4(input())
