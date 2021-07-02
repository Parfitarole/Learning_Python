from dotenv import load_dotenv
from mysql.connector import errorcode
import os
import mysql.connector as con

load_dotenv()

host     = os.environ.get('db_host')
port     = os.environ.get('db_port')
database = os.environ.get('db_database')
username = os.environ.get('db_username')
password = os.environ.get('db_password')

global db
global cursor
db     = None
cursor = None

def connect(db, cursor):
    if not db:
        try:
            print('Attempting to connect to database...')
            db = con.connect(
                host=host,
                port=port,
                database=database,
                username=username,
                password=password,
            )
        except con.Error as e:
          if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("*ERROR* Something is wrong with your user name or password")
          elif e.errno == errorcode.ER_BAD_DB_ERROR:
            print("*ERROR* Database does not exist")
          else:
            print(e)
        else:
            print('Connected to database!')
            cursor = db.cursor()
            return db, cursor
    else:
        print('*ERROR* Already connected to database')
        return db, cursor

def disconnect(db):
    if db:
        try:
            db.close()
        except Exception as e:
            print('Error: ', e)
        else:
            print('Disconnected from database')
    else:
        print('*ERROR* No database connection')

def status(db):
    if db:
        print('Connected to database')
    else:
        print('No database connection')

def quit(db):
    if (db):
        disconnect(db)
    exit()

def read(db):
    if not (db):
        print('No database connection')
    else:
        cursor.execute("Show tables;")
        tables = cursor.fetchall()

        while True:
            print('Available tables:')
            print('-------------------')
            for table in tables:
                print(table)
            new_line()
            print('Or type "back" to go back')
            new_line()
            user_input = input('| From what table? ')
            new_line()
            if (user_input in tables):
                print('| Available read options:')
                print('-------------------------')
                print('all')
                print('first')
                print('last')
                print('random')
                new_line()
                print('Or type "back" to go back')
                new_line()
                user_input = input('| What would you like to read? ')
                if user_input == 'all':
                    query = 'SELECT * FROM' + user_input + ';'
                    print(query)
                    # values = cursor.execute(query)
                elif user_input == 'back':
                    break
            elif user_input == 'back':
                break
            else:
                print('*ERROR* Table: "', user_input, '" does not match any table in the database, please try again')
                new_line()


# Print new line
def new_line():
    print('\n')

def help():
    print('Command:    | Description:')
    print('------------------------------------------------------')
    print('status:     | Checks database connection status')
    print('connect:    | Attempts to connect to the database')
    print('disconnect: | Attempts to disconnect from the database')
    print('exit:       | Exits the application')
    print('create:     | Unavailable')
    print('read:       | Read values form the database')
    print('update:     | Unavailable')
    print('delete:     | Unavailable')

# Program starts here
new_line()
print('Weclome To My Database Manager')
print('------------------------------')
new_line()

# Main loop
while True:
    user_input = input('| Enter command: ')

    new_line()

    if user_input == "exit":
        quit(db)
    elif user_input == "help":
        help()
    elif user_input == "status":
        status(db)
    elif user_input == "connect":
        db, cursor = connect(db, cursor)
    elif user_input == "disconnect":
        disconnect(db)
    elif user_input == "create":
        continue
    elif user_input == "read":
        read(db)
    elif user_input == "update":
        continue
    elif user_input == "delete":
        continue
    else:
        print('*ERROR* Unknown command: "', user_input, '" Enter "help" to see list of available commands')

    new_line()

# cursor.execute('INSERT INTO Person (name, age) VALUES (%s,%s)', ('david', 30))
# db.commit()
# print('Closing connection to database')
# db.close()
