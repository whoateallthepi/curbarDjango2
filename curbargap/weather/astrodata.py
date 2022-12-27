from datetime import timedelta, datetime
from decimal import Decimal
from django.utils import timezone

from skyfield import almanac
from skyfield.api import N, W, wgs84, Loader
from skyfield.framelib import ecliptic_frame


class AstroData(object):
    def __init__(self, latitude, longitude, date):
        self.midnight = datetime.combine(date, datetime.min.time().replace(tzinfo=timezone.utc))
        self.next_midnight = self.midnight + timedelta(days=1)
        self.latitude = latitude
        self.longitude = longitude
        self.here = wgs84.latlon(float(self.latitude) * N, float(self.longitude) * W)

        # create a loader
        load = Loader('media/skyfield')

        self.eph = load('de421.bsp')
        self.ts = load.timescale()
        self.t0 = self.ts.from_datetime(self.midnight)
        self.t1 = self.ts.from_datetime(self.next_midnight)
    
    @property
    def sun_times(self):
        
        time, event = almanac.find_discrete(self.t0, self.t1, almanac.sunrise_sunset(self.eph, self.here))

        sun_data = {'rise':0, 'set' : 0}
        
        for t, e in zip(time,event):
            if e == 1: # 1 is sunrise
                sun_data.update(rise=(t.astimezone(timezone.utc)))
            elif e == 0:
                sun_data.update(set=(t.astimezone(timezone.utc)))
                
        return sun_data

    @property
    def moon_times(self):
        sun, moon,earth = self.eph['sun'], self.eph['moon'], self.eph['earth']
        
        #assume time of next midnight
        
        moon_data = {'phase': 0, 'percent': 0, 'rise': 0, 'set' : 0}

        e = earth.at(self.ts.utc(self.next_midnight))
        s = e.observe(sun).apparent()
        m = e.observe(moon).apparent()

        _, slon, _ = s.frame_latlon(ecliptic_frame)
        _, mlon, _ = m.frame_latlon(ecliptic_frame)

        degrees = (mlon.degrees - slon.degrees) % 360.0
        
        moon_data.update(phase = round(Decimal(degrees),2)) # rounded decimal for compatibility with database
        
        moon_data.update(percent = (100.0 * m.fraction_illuminated(sun))) # not currently used 
        
        # try calc rise and set

        f = almanac.risings_and_settings(self.eph, self.eph['Moon'], self.here)

        time, event = almanac.find_discrete(self.t0, self.t1, f)
        
        for t,e in zip(time,event):
            if e == 1: #a rise
                moon_data.update(rise=t.astimezone(timezone.utc))
            elif e == 0:
                moon_data.update(set=t.astimezone(timezone.utc))
       
        return moon_data
        