from flask import Flask, session, render_template, redirect, url_for, request
from config import SECRET
import transactions

app = Flask(__name__)
app.secret_key = SECRET


@app.route("/")
def home():
    if 'username' not in session:
        return render_template("login.html")
    return render_template("home.html")


@app.route('/signup')
def signup():
    if 'username' not in session:
        return render_template('signup.html')
    else:
        return redirect(url_for('home'))


@app.route("/login", methods=['POST'])
def login(): 
    if request.method != 'POST':
        return 'invalid method!'

    form = request.form
    username = form['username']
    password = form['passw']

    # check username and password
    stat = transactions.check_username_password(username, password)
    if stat == "ok":
        session['username'] = username
        return redirect(url_for('home'))
    return stat

@app.route('/register', methods=['POST', 'GET'])
def register():

    if request.method != 'POST':
        return 'invalid method!'

    form = request.form
    password = form['passw']

    if password != form['repassw']:
        return 'invalid pass'

    username = form['username']
    email = form['email']
    
    # register user in db
    stat = transactions.create_user(username, email, password) 
    if stat == "ok":
        session['username'] = username
        return redirect(url_for('home'))
    else:
        return stat

    return "failed"
    
@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('home'))

@app.route('/search_user')
def search_user():
    if request.method != 'GET':
        return "invalid method!"
    
    if 'username' not in session:
        return redirect(url_for('home'))

    if 'username' not in request.args:
        return "invalid input"
    
    search_user = request.args['username']
    stat = transactions.search_users(session['username'], search_user)
    if stat != 'failed' and stat:
        if session['username'] in stat:
            stat.remove(session['username'])
        return render_template('add_contact.html', users=stat)

    return "failed"


@app.route("/add_con/<username>")
def add_contact(username):
    if 'username' not in session:
        return redirect(url_for('home'))
    
    if session['username'] == username:
        return "can not add yourself to your contacts."
    
    # add to contacts
    return transactions.add_contacts(session['username'], username)

if __name__ == "__main__":
    app.debug = True
    app.run()

