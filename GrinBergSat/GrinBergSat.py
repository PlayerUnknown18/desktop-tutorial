import datetime
import time
import port_communication
import threading
import jsonloader
from skyfield.api import Topos, load, utc
import pyorbital.orbital
import socket
import requests
import json

class DoplerCorrection:
    def __init__(self,jinfo_object):
        self.config_data = jinfo_object
        self.satellite_freq = float(jinfo_object.hdsdr_freq)
        self.rfcb_freq = float(jinfo_object.rfcb_freq)
        self.__speed_of_light = 299792458
        self.port = jinfo_object.hdsdr_port
        self.port_comm = port_communication.DoplerPortCommunication(self.port, self.satellite_freq)
        self.__offset = jinfo_object.offset
        self.__flip_dopler_number = -1
        self.satellite_name = get_sat_name(int(self.config_data.norad_id))
        self.doppler_satellite = load.tle("https://celestrak.com/NORAD/elements/active.txt",reload=False)[self.satellite_name]
        self.dopler_station = Topos(jinfo_object.station_lat,jinfo_object.station_lon)

    def calculate_dopler(self,freq):
        timescale = load.timescale(builtin=True)
        t = timescale.utc(datetime.datetime.utcnow().replace(tzinfo=utc))
        t1 = timescale.utc(t.utc_datetime() + datetime.timedelta(seconds=1))
        diff = (self.doppler_satellite - self.dopler_station).at(t)
        diff1 = (self.doppler_satellite - self.dopler_station).at(t1)
        range1 = diff.distance().km
        range2 = diff1.distance().km
        change = (range1 - range2) * 1000
        dopler_corr = (freq * (self.__speed_of_light + change) / self.__speed_of_light) - self.__offset
        return dopler_corr


    def update_dopler_hdsdr(self):
        while True:
            time.sleep(0.3)
            dopler_freq = self.calculate_dopler(self.satellite_freq)
            print(dopler_freq)
            self.port_comm.write_dopler_corr_to_port(str(dopler_freq))

    def update_dopler_rfcb(self,sock_io):
        get_freq = float(self.rfcb_freq)
        while True:
            freq = get_freq
            data = [7,13,0,0,0]
            data = bytearray(data)
            i = 0
            while i < 8 or freq > 0:
                data.append(int(freq % 256))
                freq = int(freq / 256)
                i += 1
            try:
                sock_io.send(data)
                print(get_freq)
            except:
                print("except")
                sock_io = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock_io.connect(("127.0.0.1", 4532))

            get_freq = self.calculate_dopler(self.rfcb_freq) * 10 ** 6
            time.sleep(2)


class UpdateSatelliteCords:
    def __init__(self,jinfo_object):
        self.config_data = jinfo_object
        self.port = jinfo_object.antenna_port
        self.time_for_tuning_antennas = jinfo_object.time_for_tuning_antennas
        self.port_comm = port_communication.AntennaPortCommunication(self.port)
        self.azimuth = 18.9
        self.elevation = 20.1
        self.__elevation_to_radians_number = 180
        self.satellite_name = get_sat_name(int(self.config_data.norad_id))
        self.satellite = load.tle("https://celestrak.com/NORAD/elements/active.txt",reload=False)[self.satellite_name]
        self.station_lon = jinfo_object.station_lon
        self.station_lat = jinfo_object.station_lat
        self.station_alt = jinfo_object.station_elev
        self.station = Topos(jinfo_object.station_lat,jinfo_object.station_lon)

    def check_if_real_cords(self, azimute, elevation):
        if azimute > 0 and elevation > 0:
            return True
        else:
            return False

    def update_satellite_cords(self):
        last_elevation = 0
        last_azimuth = 0
        while True:
            time.sleep(self.time_for_tuning_antennas)
            utc_time_now = datetime.datetime.utcnow()
            orbital_object = pyorbital.orbital.Orbital(self.satellite_name,"active.txt")
            self.azimuth,self.elevation = orbital_object.get_observer_look(utc_time_now,self.station_lon,self.station_lat,self.station_alt)
            print(f"satellite azimuth now:{self.azimuth}")
            print(f"satellite elevation now:{self.elevation}")
            if int(last_azimuth) != int(self.azimuth) or int(last_elevation) != int(self.elevation):
                last_elevation = self.elevation
                last_azimuth = self.azimuth
                print(self.port_comm.read_antena_coordinates_from_port())
                if self.check_if_real_cords(self.azimuth,self.elevation):
                    self.azimuth,self.elevation = self.port_comm.convert_to_format(self.azimuth,self.elevation)
                    self.port_comm.write_antena_coordinates_to_port(self.azimuth,self.elevation)
                    



class UpdateSatelliteCordsThread(threading.Thread):
    def __init__(self,jinfo_object):
        threading.Thread.__init__(self)
        self.jinfo_object = jinfo_object

    def run(self):
        ant = UpdateSatelliteCords(self.jinfo_object)
        ant.update_satellite_cords()


def update_modulation(sock_io):
    FSK_CODE = [9, 19, 0, 0, 0, 9, 70, 83, 75, 45, 71, 51, 82, 85, 72, 128, 37, 0, 0]
    FSK_CODE = bytearray(FSK_CODE)
    sock_io.send(FSK_CODE)



def connect_to_sock():
    socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            socket_conn.connect(("127.0.0.1",4532))
            print("connected to rfcb")
            break
        except:
            print("cant connect to rfcb,please run the rf checkout box\rtry again in 5 seconds")
            time.sleep(5)
    return socket_conn


def get_sat_name(norad):
    sat_list = requests.get("https://db.satnogs.org/api/satellites/").text
    sat_list = json.loads(sat_list)
    for i in sat_list:
        if i.get("norad_cat_id") == norad:
            return i.get("name")



def main():
    #create socket connection with the rfcb
    socket_conn = connect_to_sock()
    #loads data from the config file
    load_json_object = jsonloader.JsonLoad()
    json_info = load_json_object.return_jinfo_object()
    print("got config data from json")
    dp = DoplerCorrection(json_info)
    rfcbDpThread = threading.Thread(target=dp.update_dopler_rfcb,args=(socket_conn,))
    print("Create dopler correction threads")
    update_modulation(socket_conn)
    print("modulation update:succsess")
    ant = UpdateSatelliteCordsThread(json_info)
    ant.start()
    rfcbDpThread.start()
    dp.update_dopler_hdsdr()



if __name__ == '__main__':
    main()
