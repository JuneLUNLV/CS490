import login
import csvScript
import sys

username = "admin"
password = "password"


if len(sys.argv) < 1:
    username = sys.argv[1]
    password = sys.argv[2]


login.createLoginDb()
login.signup(username,password)

csvScript.runScript()
