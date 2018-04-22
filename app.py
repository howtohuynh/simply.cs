from flask import Flask, render_template, json, request, session, redirect
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'spooky action at a distance-Einstein'
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'PReview11M'
app.config['MYSQL_DATABASE_DB'] = 'simplyCS'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def main():
    if session.get('user'):
        return render_template('index_in.html')
    else:
        return render_template('index_out.html')
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/Logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/Internships')
def showInternships():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM internships")
    internships = cursor.fetchall()
    return render_template('internships.html', internships=internships)

@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    try:
        _name = request.form['inputUsername']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:

            # All Good, let's call MySQL

            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser', (_name, _email, _hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message': 'User created successfully !'})
            else:
                return json.dumps({'error': str(data[0])})
        else:
            return json.dumps({'html': '<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')


@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

        # connect to mysql
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin', (_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][3]), _password):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html', error='Wrong Email address or Password.')
        else:
            return render_template('error.html', error='Wrong Email address or Password.')

    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        con.close()

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('index_in.html')
    else:
        return render_template('index_out.html')
    return render_template('index.html')

@app.route('/addInternship',methods=['POST'])
def addInternship():
    try:
        if session.get('user'):
            _position = request.form['inputPosition']
            _company = request.form['inputCompany']
            _description = request.form['inputDescription']
            _link = request.form['inputLink']
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addInternship',(_position, _company, _description, _link, _user))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return redirect('/Internships')
            else:
                return render_template('error.html',error = 'An error occurred!')

        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()



if __name__ == "__main__":
    app.run(port=5000)
