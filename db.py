import mariadb
import dbcreds
import traceback
from flask import Flask, request, Response


def openConnection():
  try:
    return mariadb.connect(
        user=dbcreds.user,
        password=dbcreds.password,
        host=dbcreds.host,
        port=dbcreds.port,
        database=dbcreds.database,
    )

  except:
    print("Error opening connextion to DB!")
    traceback.print_exc()
    return None


def closeConnection(conn):
  if(conn == None):
    return True
  try:
    conn.close()
    return True

  except:
    print("Error closing connection to DB!")
    traceback.print_exc()
    return False


def openCursor(conn):
  try:
    return conn.cursor()
  except:
    print("Error opening cursor on DB, closing connection!")
    traceback.print_exc()
    return None


def closeCursor(cursor):
  if(cursor == None):
    return True
  try:
    cursor.close()
    return True

  except:
    print("Error closing cursor on DB!")
    traceback.print_exc()
    return False


def closeAll(conn, cursor):
  closeCursor(cursor)
  closeConnection(conn)
  print('Cursor and connection closed!')


def loopItems(cursor, rows):
  headers = [i[0] for i in cursor.description]
  result = []
  for row in rows:
    result.append(dict(zip(headers, row)))
  return result


def run_query(qstr, params=[]):
  result = None
  data = None
  conn = openConnection()
  cursor = openCursor(conn)
  try:
    cursor.execute(qstr, params)

  except:
    traceback.print_exc()
    print('Error')
  try:
    data = cursor.fetchall()
#! Had an issue where SELECT was running, then hitting the elif for PATCH and since it had a rowcount of 1, it wwas updating the variable in app.py to 1
#! Added this conditional and return to full-stop on a SELECT query and return the result. Unsure if good, but works as a solution for now!
    result = loopItems(cursor, data)

  except:
    print(data)
    print('Not a SELECT')

  if(cursor.lastrowid != -1 and cursor.lastrowid != None and data == None):
    try:
      conn.commit()
      result = cursor.lastrowid
    except:
      print('Not a POST')

  elif(cursor.rowcount == 1 and data == None):
    try:
      conn.commit()
      result = cursor.rowcount
    except:
      print('Not a PATCH or DELETE')

  closeAll(conn, cursor)

  return result


# def run_delete(qstr, params=[]):
#   result = None
#   conn = openConnection()
#   cursor = openCursor(conn)
#   try:
#     cursor.execute(qstr, params)
#     conn.commit()
#     result = cursor.rowcount

#   except:
#     traceback.print_exc()
#     print('Error patching item!')

#   closeAll(conn, cursor)

#   return result
