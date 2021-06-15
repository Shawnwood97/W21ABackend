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

# dynamic function working for get requests!


def run_select(qstr, params=[]):
  conn = openConnection()
  cursor = openCursor(conn)
  result = None
  try:
    cursor.execute(qstr, params)
    item = cursor.fetchall()

    result = loopItems(cursor, item)

  except:
    traceback.print_exc()
    print('Error getting items!')

  closeAll(conn, cursor)
  return result


def run_insert_update(qstr, params=[]):
  result = None
  conn = openConnection()
  cursor = openCursor(conn)
  try:
    cursor.execute(qstr, params)

    # can't think of another way, I understand there's a slim chance that rowcount could be 1 in certain cases here, especially on conditional queries.
    # if(cursor.rowcount > 1):
    #   result = loopItems(cursor, cursor.fetchall())
    if(cursor.lastrowid != 0):
      conn.commit()
      result = cursor.lastrowid
    elif(cursor.rowcount == 1):
      conn.commit()
      result = cursor.rowcount

  except:
    traceback.print_exc()
    print('Error patching item!')

  closeAll(conn, cursor)

  return result


def run_delete(qstr, params=[]):
  result = None
  conn = openConnection()
  cursor = openCursor(conn)
  try:
    cursor.execute(qstr, params)
    conn.commit()
    result = cursor.rowcount

  except:
    traceback.print_exc()
    print('Error patching item!')

  closeAll(conn, cursor)

  return result
