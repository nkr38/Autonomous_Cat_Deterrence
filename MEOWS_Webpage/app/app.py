import datetime
import random
from flask import Flask, render_template, request, jsonify, render_template_string
from db import DataBase
from constants import *
from model import Model

app = Flask(__name__, template_folder='./template/html')
db = DataBase()
db.connect_DB()

modelObj = Model()

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/monitor")
def monitor():
    if(modelObj.auth):
        update_model()
        return render_template("monitor.html")
    else:
        return render_template_string('PageNotFound {{ errorCode }}', errorCode='404'), 404 

@app.route("/login", methods=['POST'])
def login():
    #db.connect_DB()
    modelObj.auth = False
    data = request.json
    record = db.get_device_info('device', data['serial_number'])
    if not record:
        return jsonify({'error': 'Serial Number Invalid'}), 404
    else:
        #return redirect('/monitor')
        modelObj.auth = True
        modelObj.serialNum = data['serial_number']
        modelObj.deviceName = record[1]
        return jsonify({}), 200
    
@app.route("/logout", methods=['POST'])
def logout():
    modelObj.auth = False
    modelObj.serialNum = None
    return jsonify({}), 200

@app.route("/get_model", methods=['GET'])
def get_model():
    deviceInfo = db.get_device_info('device', modelObj.serialNum)
    returnObj = {'serial_number': modelObj.serialNum, 'device_name': modelObj.deviceName, 'active': bool(deviceInfo[2])}
    return jsonify(returnObj), 200

@app.route("/active_state", methods=['POST'])
def active_state():
    data = request.json
    activeStatus = data['active_state']
    sqlStatement = """UPDATE device SET active = ? WHERE serial_number = ?"""
    parameters = (activeStatus, modelObj.serialNum)
    db.execute(sqlStatement, parameters=parameters)

    print(db.get_rows('device'))
    return jsonify({}), 200

@app.route("/set_device_name", methods=['POST'])
def set_device_name():
    data = request.json
    deviceName = data['device_name']
    sqlStatement = """UPDATE device SET device_name = ? WHERE serial_number = ?"""
    parameters = (deviceName, modelObj.serialNum)
    db.execute(sqlStatement, parameters=parameters)

    print(db.get_rows('device'))
    return jsonify({}), 200

@app.route("/get_past_day_data", methods=['GET'])
def get_past_day_data():
    current_date = datetime.datetime.now()
    start_of_day = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    sqlStatement = """SELECT * FROM detection WHERE detection_datetime >= ? AND detection_datetime < ? AND serial_number = ?"""
    parameters = (start_of_day, current_date, modelObj.serialNum)
    records = db.get_data(sqlStatement, parameters=parameters)
    return jsonify({'records': records}), 200

@app.route("/get_past_month_data", methods=['GET'])
def get_past_month_data():
    current_date = datetime.datetime.now()
    past_30_days = current_date - datetime.timedelta(days=30)
    sqlStatement = """SELECT * FROM detection WHERE detection_datetime >= ? AND detection_datetime < ? AND serial_number = ?"""
    parameters = (past_30_days, current_date, modelObj.serialNum)
    records = db.get_data(sqlStatement, parameters=parameters)
    return jsonify({'records': records}), 200

@app.route("/get_past_week_data", methods=['GET'])
def get_past_week_data():
    current_date = datetime.datetime.now()
    past_7_days = current_date - datetime.timedelta(days=7)
    sqlStatement = """SELECT * FROM detection WHERE detection_datetime >= ? AND detection_datetime < ? AND serial_number = ?"""
    parameters = (past_7_days, current_date, modelObj.serialNum)
    records = db.get_data(sqlStatement, parameters=parameters)
    return jsonify({'records': records}), 200

def update_model():
    record = db.get_device_info('device', modelObj.serialNum)
    if not record:
        return
    else:
        modelObj.deviceName = record[1]

def add_test_data():
    for i in range(100):
        today = datetime.datetime.now()
        pastDay = today - datetime.timedelta(days=40)
        randData = pastDay + datetime.timedelta(seconds=random.randint(0, 40*24*60*60))
        db.add_rows('detection', {'serial_number': AVAILABLE_SERIALS[0], 'detection_datetime': randData})

if __name__ == "__main__":
    db.create_table(DEVICE_TABLE)
    db.create_table(DETECTION_TABLE)

    for i in range(len(AVAILABLE_SERIALS)):
        db.add_rows('device', {'serial_number': AVAILABLE_SERIALS[i], 'device_name': f'device{i+1}', 'active': True})

    add_test_data()
    #db.get_rows(db.conn.cursor())
    #print(db.get_rows('device'))
    print(db.get_rows('detection'))
    app.run(debug=True)
    db.disconnect_DB()