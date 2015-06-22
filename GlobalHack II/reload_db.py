import os, sys

"""
HEROKU STAGING
$ heroku pg:reset DATABASE
$ heroku run python reload_db.py
SETUP MIGRATIONS
$ heroku run python manage.py syncdb
$ heroku run python manage.py convert_to_south api
$ heroku run python manage.py migrate api
"""
import socket

def isOpen(ip,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
     s.connect((ip, int(port)))
     s.shutdown(2)
     return True
    except:
     return False
postgres = isOpen('127.0.0.1', '5432')

message = sys.argv[1:]
full = False
if len(message) > 0 and message[0] == "full":
    full = True

if full:
    if postgres:
        print "Wiping postgres database..."
        os.system("dropdb gb2")
        os.system("createdb gb2")
    else:
        print "Removing sqlite database..."
        os.system("rm db.sqlite3")
        os.system("rm generic_app/db.sqlite3")
os.system("python manage.py syncdb --noinput")
if full:
    os.system("python manage.py loaddata fixtures/superuser.json")
