import pyodbc
import os
import sys

# if sys.argv() is None:
#     abs_path = os.getcwd()
# else:
#     abs_path = sys.argv()[0]

abs_path = os.getcwd() + '\\BookStore.accdb'

con_string = rf'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={abs_path};CHARSET=UTF8'

conn = pyodbc.connect(con_string)

cursor = conn.cursor()

# insert
# myUser = (

#     (6, 'data', 'email'),
#     (7, 'another data', 'email')
# )

# cursor.executemany('INSERT INTO users VALUES (?, ?, ?)', myUser)
# conn.commit()

# select
cursor.execute('SELECT * FROM Книги')
for row in cursor.fetchall():
    print(row)

# # update
# newName = "updatedData"
# uid = 14

# cursor.execute('UPDATE users SET name = ? WHERE id = ?'. (newName, uid))

# # delete
# cursor.execute('DELETE FROM users WHERE id = ?', (uid))
