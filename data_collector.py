from flask import Flask,render_template,send_file
from flask import send_from_directory
app = Flask(__name__)

# send request to umoney
lines = [{"id":"11200020","name":"T-2 (Ботаник-5 Шар)"}]
print("Нийт маршрутын тоо :",len(lines))
import requests,json,time
# bus line and location data
class RoutineList:
    def __init__(self,route_name,stations,routines,id):
        self.id = id
        self.routines=routines
        self.route_name = route_name.split()[0]
        self.stations = stations
# bus location data
class StationLocation:
    def __init__(self,station,long,lat,station_seq,exists):
        self.station = station
        self.long = long
        self.lat = lat
        self.index = station_seq
        self.bus_exists = exists
# Bus Count storing object
class BusNumber:
    def __init__(self,count):
        self.bus_cound=count
# object to dictionary
def parse_to_dic(obj):
    return obj.__dict__
# retreave data from ub bus
def get_data():
    print("function fired")
    loop = ["start","end"]
    bus_number=0
    route_lists =[]
    for routine in loop:
        print(routine)
        for bus_stops in lines:
            url = "https://api.u-money.mn/travel/bus_line_detail/"+bus_stops["id"]+"/"+routine
            res = requests.post(url)
            stations = res.json()
            bus_stop_details = []
            for station in stations["station_list"]:
                print(station)
                bus_stop_details.append(StationLocation(station["station_name"],station["longitude"],station["latitude"],station["station_seq"],station["exist_bus"]))
                if station["exist_bus"] == "Y":
                    bus_number += 1
            route_lists.append(RoutineList(bus_stops["name"],bus_stop_details,routine,bus_stops["id"]))
    route_lists.append(BusNumber(bus_number))
    # save to reports
    with open("./report/"+time.strftime("%m-%d-%Y-%H-%M-%S")+'-station-data.json', 'w', encoding='utf-8') as f:
        json.dump(route_lists,f, ensure_ascii=False, indent=4,default=parse_to_dic)

from apscheduler.schedulers.background import BackgroundScheduler
import atexit,time,os
scheduler = BackgroundScheduler()
scheduler.add_job(func=get_data, trigger="interval", seconds=100)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())
# seporate threads multi threading
# cron job schedule
@app.route("/",defaults={'req_path': ''})
@app.route('/<path:req_path>')
def files(req_path):
    BASE_DIR = './report'
    abs_path = os.path.join(BASE_DIR, req_path)
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = os.listdir(abs_path)
    return render_template('files.html', files=files)
if __name__ == '__main__':
    app.run(use_reloader=False)