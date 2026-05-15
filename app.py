import os
from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory,session
from datetime import datetime,timedelta
import uuid
from zoneinfo import ZoneInfo
import json
import copy


print('ADMIN_PASSWD  '+str(os.environ.get('ADMIN_PASSWD')))

historyDays = -7
app = Flask(__name__)
app.json.sort_keys = False
app.secret_key = b'Chai'

users = {
    'admin' : {'passwd': 'admin123','role':'admin'},
    'kitchen' :{'passwd': 'kitchen123','role':'admin'},
    'cashier' :{'passwd': 'cashier123','role':'admin'},
}

def generate_unique_id():
    return str(uuid.uuid4())

@app.route('/')
@app.route('/<page>')
def index(page = 'login'):
    return render_template(page+'.html',session=session)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users:
            print('username '+str(username)+' password '+str(password)+' real pass '+str(users[username]['passwd']))
            if username in users and password == users[username]['passwd']:
                session['username'] = username
                session['sessionid'] = generate_unique_id()
                return render_template('cashier_menu.html',session=session)
        session['status'] = 'Invalid User or Password'
    else:
        session.pop('status',None)
    
    return render_template('login.html',session=session)


@app.route('/logout',methods=['POST'])
def logout():
    data = request.get_json()
    username = data.get('username')
    sessionid = data.get('sessionid')

    print('username '+str(username)+' users '+str(users)+' session '+str(session))
    if username in users and 'username' in session and session['username'] == username \
        and 'sessionid' in session and session['sessionid'] == sessionid:
        print('valid signout request will logout the user')
        session.pop('username',None)
        session.pop('sessionid',None)
        session.pop('status',None)
        return {'redirect_url':'login','status': 'logged out successfully.'}
    session['status'] = 'Invalid User or Password'
    
    return {'status': 'logged out failed'}

initOrderNum = 0
def getOrderNum():
    global initOrderNum
    initOrderNum+=1
    return initOrderNum

orders = []

@app.route('/getOrders',methods=['GET'])
def getOrders():
    return orders

@app.route('/placeOrder',methods=['POST'])
def placeOrder():
    data = request.get_json()
    order = {'ordernum' : getOrderNum() ,'items' : data["cart"] }
    orders.append(order)
    print(f'orders {orders}')
    retObj = {'redirect_url':'view_orders','status': 'Order placed Successfully.'}
    return retObj


print('All app code inited ')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=5001)