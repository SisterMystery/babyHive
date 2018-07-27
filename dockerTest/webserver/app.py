from __future__ import print_function
from flask import Flask, request
from werkzeug.utils import secure_filename
import os
import redis
import sys
import io
import json
import socket
import time

app = Flask(__name__)

redis_host = "redis"
redis_port = 6379
redis_password = ""

r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

def read_log(key='out_data', retries=8, storage=r):
	while retries > 0:
		try:
			d = storage.get(key)
			if d == None:
				return "no Data yet"
			return d
		except:
			time.sleep(0.5)
			retries -= 1
	return "no Data yet"

def write_log(data, key='in_data', retries=8, storage=r):
	old = read_log(key)
	while retries > 0:
		try:
			return storage.set(key, old+ "<p>" + data +"</p>")
		except:
			time.sleep(0.5)
			retries -= 1

@app.route("/", methods=['GET', 'POST'])
def hello():
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file part')
			return "Sooorryyyy, try again"
		file = request.files['file']
		if file.filename == '':
			flash('No selected file')
			return "sorry, no filename"
		if file:
			filename = secure_filename(file.filename)
			contents = file.read()
			r.set("in_data", contents)

	return '''
    <!doctype html>
    <h1>Upload Time!</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route("/output")
def get_output():
	if request.method == 'GET':
		return read_log()




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
