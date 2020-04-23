import login
import csvScript

login.createLoginDb()
login.signup("admin","password")

csvScript.runScript()