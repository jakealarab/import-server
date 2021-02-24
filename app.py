import os
import flask, math, csv, re, io, datetime, requests
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
  return "<h1>Import Server</h1><p>"

@app.route('/import', methods=['POST'])
def import_file():
  files = request.files
  csv_file = files['file']
  if csv_file == None:
    return 'Success'
  raw_bytes = csv_file.read()
  arr = numpy_array_from_bytes(raw_bytes)
  shifts = parse_schedule(arr)
  for shift in shifts:
    add_shift(shift)
  return 'Sucess'



def is_date(cell):
  if not isinstance(cell, str):
    return False
  return cell.startswith('Mon') or \
  cell.startswith('Tue') or \
  cell.startswith('Wed') or \
  cell.startswith('Thur') or \
  cell.startswith('Fri') or \
  cell.startswith('Sat') or \
  cell.startswith('Sun')

def is_name(cell):
  if len(cell) < 2:
    return False
  return cell[1] == '.'

def is_time(cell):
  if len(cell) < 2:
    return False
  return cell[0:2].isdigit()

def parse_schedule(arr):
  columns = arr.shape[1]
  times = {}
  time = None
  for rown, row in enumerate(arr):
    for cell in row:
      if is_time(cell):
        time = cell
      times[rown] = time
  shifts = []
  date = None
  for i in range(columns):
    col = arr[:, i]
    for rown, cell in enumerate(col):
      if is_date(cell):
        date = cell
      if is_name(cell):
        name_cell = cell
        role_cell = arr[rown][0] if arr[rown][0] != "" else "default"
        date_cell = date
        time_cell = times[rown]
        shifts.append(get_shift_info(name_cell, role_cell, date_cell, time_cell))
  return shifts

def numpy_array_from_bytes(raw_bytes):
  io_string = io.StringIO(raw_bytes.decode('UTF-8'))
  csv_reader = csv.reader(io_string, delimiter=',', quotechar='"')
  data = []
  for row in csv_reader:
      data.append(row)
  return np.array(data)

def get_shift_info(name_cell, role_cell, date_cell, time_cell):
  db = {}
  db['name'] = name_cell
  db['role'] = role_cell
  date = date_cell
  time = time_cell
  #recall that start is 4 numbers in a string and so is end
  start = date.split(', ')[1] + ' 2021 ' + time.split('-')[0][0:2]
  end = date.split(', ')[1] + ' 2021 ' + time.split('-')[1][0:2]
  startTime = datetime.datetime.strptime(start, '%B %d %Y %H')
  endTime = datetime.datetime.strptime(end, '%B %d %Y %H')
  db['start'] = str(startTime)
  db['end'] = str(endTime)
  return db


def add_shift(shift):
  url = 'https://mert-app-server.herokuapp.com/addshiftfromname/' + shift['name'] + \
  '/' + shift['role'] + '/' + shift['start'] + '/' + shift['end'] 
  res = requests.get(url)
  print(res.text)

def print(thing):
  app.logger.info(thing)

if __name__ == '__main__':
  port = int(os.environ.get("PORT", 5000))
  app.run(debug=True, port=port)
