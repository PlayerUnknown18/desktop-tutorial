import serial
import time

class DoplerPortCommunication:
    def __init__(self,port,default_freq):
        self.open_port(port)
        self.ser.write(str(default_freq).encode())
        self.__convert_to_freq_number = 1000000
        self.default_mode = b"MD2;"

    def open_port(self,port):
        while True:
            try:
                self.ser = serial.Serial(port,timeout=1)
                break
            except:
                print("cannot open the port...\ntry again in 5 seconds")
                time.sleep(5)

    def write_dopler_corr_to_port(self, freq):
        if len(freq) >= 11:
            a = list(freq)[:13]
            freq = int(float(''.join(a)) * self.__convert_to_freq_number)
            freq = "FA0" + str(freq) + ";"
            self.ser.write(freq.encode())
            self.ser.write(self.default_mode)



class AntennaPortCommunication:
    def __init__(self,port):
        self.open_port(port)

    def open_port(self,port):
        while True:
            try:
                self.ser = serial.Serial(port,timeout=1)
                break
            except:
                print("cannot open the port...\rtry again in 5 seconds")
                time.sleep(5)

    def convert_to_format(self, az,el):
        el = int(el)
        az = int(az)
        print(len(str(el)))
        if len(str(el)) == 1:
            el = f"00{el}"
            print(f"elevation correction:{el}")

        elif len(str(el)) == 2:
            el = f"0{el}"
            print(f"elevation correction:{el}")

        elif len(str(el)) == 3:
            el = str(el)
            print(f"elevation correction:{el}")

        if len(str(az)) == 1:
            az = f"00{az}"

        elif len(str(az)) == 2:
            az = f"0{az}"

        elif len(str(az)) == 3:
            az = str(az)

        return az,el
        
    def write_antena_coordinates_to_port(self,az,el):
        data_to_write = "W"+str(az)+" "+str(el)+"\n\r"
        print(f"Az:{az}")
        print(f"El:{el}")
        print(data_to_write)
        if self.check_protocol(data_to_write):
            self.ser.write(data_to_write.encode())
        else:
            print("cant write")
    
    def write_only_azimuth(self,az):
        data_to_write = "W"+str(az)+" "+"000\n\r"
        if self.check_protocol(data_to_write):
            self.ser.write(data_to_write.encode())
        else:
            print("cant write")

    def read_antena_coordinates_from_port(self):
        self.ser.write(b"C2\n\r")
        return self.ser.read(15)

    def parse_antena_coordinates(self,antena_cords):
        elev = antena_cords[:5]
        azimuth = antena_cords[5:10:]
        return elev,azimuth
    
    def check_protocol(self,text):
        if text[4:5] == ' ':
            if len(text[1:]) == 9:
                return True
        else:
            print("[-]Wrong protocol")
            return False
        


        
