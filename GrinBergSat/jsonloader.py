import json


class Jinfo:
    def __init__(self, json_data):
        self.hdsdr_freq = json_data['configs']['hdsdr_freq']
        self.rfcb_freq = json_data['configs']['rfcb_freq']
        self.hdsdr_port = json_data['configs']['hdsdr_port']
        self.station_lon = float(json_data['configs']['lon'])
        self.station_lat = float(json_data['configs']['lat'])
        self.station_elev = float(json_data['configs']['elev'])
        self.offset = float(json_data['configs']['offset'])
        self.time_for_tuning_antennas = int(
            json_data['configs']['Time_for_tuning_antennas'])
        self.antenna_port = json_data['configs']['antenna_port']
        self.norad_id = json_data['configs']['norad_id']
        self.rfcb_flag = json_data['configs']['rfcb']
        self.hdsdr_flag = json_data['configs']['hdsdr']
        self.antenna_flag = json_data['configs']['antenna']
        self.tle_type = json_data['configs']['tle_type']


class JsonLoad:
    def __init__(self):
        with open("config.json", "r") as config_file:
            json_data = json.loads(config_file.read())
        self.json_info = Jinfo(json_data)

    def return_jinfo_object(self):
        return self.json_info
