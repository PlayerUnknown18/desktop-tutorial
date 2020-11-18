import requests
import re

class GetTLE:
    def __init__(self):
        b = requests.get("https://celestrak.com/NORAD/elements/active.txt").text#get the text from celestrak active satellite text file
        text = b[395600:396000]#I cut the string because it was to long for regex and if i try to put the full text it will take alot of time and at the end it will throw a MemoryError
        a = ''.join(text.splitlines())#I found that the re library can work only with one line text so I take the text and I convert it to one line
        result = re.search("DUCHIFAT-3(.*)LEMUR-2-JPGSQUARED", a).group(0)#here i extract the text that i need
        self.tle = [re.search("D(.*)-3",result).group(0),re.search("1(.*)2 44854",result).group(0),
                    re.search("2 44854(.*)LEMUR-2-JPGSQUARED",result).group(0)[:-18]]#and here i extract the TLE into 3 parts

    def return_tle(self):
        return self.tle



