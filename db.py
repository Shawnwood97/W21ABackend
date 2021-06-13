import mariadb
import dbcreds
import traceback


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


def api_request(qstr, params=[]):
  conn = openConnection()
  cursor = openCursor(conn)
  result = None
  try:
    cursor.execute(qstr, params)

    if(params != []):
      conn.commit()
    else:
      item = cursor.fetchall()

    result = loopItems(cursor, item)

  except:
    traceback.print_exc()
    print('Error getting items!')

  closeAll(conn, cursor)
  return result
