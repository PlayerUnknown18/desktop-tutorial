from skyfield.api import Topos, load,utc
from skyfield.sgp4lib import EarthSatellite
import datetime
import time
C = 299792458
satellite = load.tle("https://celestrak.com/NORAD/elements/active.txt",reload=False)["DUCHIFAT-3"]
station = Topos(32.164646,34.826289,32)
freq = 436.400
while True:
    timescale = load.timescale(builtin=True)
    t = timescale.utc(datetime.datetime.utcnow().replace(tzinfo=utc))
    t1 = timescale.utc(t.utc_datetime()+datetime.timedelta(seconds=1))
    diff = (satellite - station).at(t)
    diff1 = (satellite - station).at(t1)
    range1 = diff.distance().km
    range2 = diff1.distance().km
    change = (range1 - range2)*1000
    dopler_corr = (freq * (C + change) / C)
    print(dopler_corr-0.008)

#C = 299792458
#t1 = timescale.utc()
