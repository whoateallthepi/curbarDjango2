import http.client
import feedparser
import json
from django.utils.dateparse import parse_datetime

from warning.models import Warning, Service

class Nswws(object):
    
    def __init__(self, api_key, base_url,feeds_url, service_id=1):
        self.headers = { 
            'x-api-key' : api_key
        }
        self.updates = []
        self.base_url = base_url
        self.feeds_url = feeds_url
        self.latest_list_url = ''
        self.service_id = service_id
                
        self._conn = http.client.HTTPSConnection(self.base_url)        
    
    def close(self):
        self._conn.close()

    def check(self, last_check):
        self.updates = []
         
        self._conn.request("GET", self.feeds_url, headers=self.headers)
        data = self._conn.getresponse().read()
        p = feedparser.parse(data)
        self.latest_list_url = p['feed']['links'][1]['href']
        self.feed_updated = parse_datetime(p['feed']['updated'])
        #
        # check if there has been an update since last check
        # If not we can quit
        # service = Service.objects.get(pk=self.service_id)
        
        if self.feed_updated <= last_check:
            print('no new updates')
            return False

        if 'entries' not in p:
            # means there are no updates but latest list will be available in 
            # self.latest_list_url
            return False
        
        for entry in p['entries']:
            for link in entry['links']:
                #breakpoint()
                self.updates.append((link['href'], entry ['title'],entry['updated'] ))

        #breakpoint()
        if self.updates: # probably don't need this test here
            return True
        else:
            return False
        
    def fetch_updates(self,force_all=False):
        # helper function to create the dict we need for updating database
        def generate_update_dict(feature):
            u = {}
            u['issuedDate'] = feature['properties']['issuedDate']
            u['weatherType'] = feature['properties']['weatherType']
            u['warningLikelihood'] = feature['properties']['warningLikelihood']
            u['warningLevel'] = feature['properties']['warningLevel']
            u['warningStatus'] = feature['properties']['warningStatus']
            u['warningHeadline'] = feature['properties']['warningHeadline']
            u['whatToExpect'] = feature['properties']['whatToExpect']
            u['warningId'] = feature['properties']['warningId']
            u['modifiedDate'] = feature['properties']['modifiedDate']
            u['validFromDate'] = feature['properties']['validFromDate']
            u['validToDate'] = feature['properties']['validToDate']
            u['affectedAreas'] = json.dumps(feature['properties']['affectedAreas'])
            u['warningImpact'] = feature['properties']['warningImpact']
            u['geometry'] = feature['geometry']
            gg = json.dumps(u['geometry'])
            #u['geojson'] = '{ "type": "Feature", "geometry" : ' + gg + ', "properties": { "name": "warning area" }}'
            return u
        
        updates = []
        #
        # This is where we get all the updates - usually not required
        #
        if force_all:
            print('fetching all current warnings')
            url = self.latest_list_url.split('https://'+ self.base_url,1)[1]
            
            self._conn.request("GET",url, headers=self.headers)
            data = self._conn.getresponse().read()
            j = json.loads(data)
            features = j['features']
            for feature in features:
                updates.append(generate_update_dict(feature))
                 
            return updates # a list of dictionaries        
        #
        # This is the more common processin where we just get the updates
        # since last check. The URLs for the warnings have been stored at 
        # the check stage
        #        
        print('fetching all new warnings/updates')
        
        for update in self.updates:
           
            url, action, time = update # unpack the update
            
            # get the warning details
            url = url.split('https://'+ self.base_url,1)[1]
            self._conn.request("GET", url, headers=self.headers)
             
            data = self._conn.getresponse().read()
            
            # should be json data
            j = json.loads(data)
           
            # Pick out the useful stuff
            features = j['features'] # only appears to be one feature but loop to be sure
            for feature in features:
                updates.append(generate_update_dict(feature))
        
        return updates # an list of dictionaries
    
    def store_updates(self, updates):
        def decodeWeatherType (weatherType):
            if weatherType == 'RAIN':
                return 0
            if weatherType == 'THUNDERSTORMS':
                return 1
            if weatherType == 'WIND':
                return 2
            if weatherType == 'SNOW':
                return 3
            if weatherType == 'LIGHTNING':
                 return 4
            if weatherType == 'ICE':
                return 5
            if weatherType == 'EXTREME HEAT':
                return 6
            if weatherType == 'FOG':
                return 7
            return 8
        
        def decodeStatus(warningStatus):
            if warningStatus == 'EXPIRED':
                return 0
            if warningStatus == 'ISSUED':
                return 1
        def decodeLevel(warningLevel):
            if warningLevel == 'YELLOW':
                return 0
            if warningLevel == 'AMBER':
                return 1
            if warningLevel == 'RED':
                return 2
            return 3

        service = Service.objects.get(pk=self.service_id)
        for update in updates:
            
            # need to decode the weather types eg WIND >> 2
            wt = []
            for type in update['weatherType']:
                wt.append(decodeWeatherType(type))
            wte = ''
            
            # concatenate whatToExpect entries into one string
            for expect in update['whatToExpect']:
                wte = wte + expect + '. '

            warning = Warning(
                warningId = update['warningId'],
                service = service,
                issuedDate = update['issuedDate'],
                weatherType = wt,
                warningLikelihood = update['warningLikelihood'],
                warningLevel = decodeLevel(update['warningLevel']),
                warningStatus = decodeStatus(update['warningStatus']),
                warningHeadline = update['warningHeadline'],
                whatToExpect = wte,
                modifiedDate = update['modifiedDate'],
                validFromDate = update['validFromDate'],
                validToDate = update['validToDate'],
                affectedAreas = update['affectedAreas'],
                warningImpact = update['warningImpact'],
                geometry = json.dumps(update['geometry']),
                )
            #breakpoint()
            warning.save()   
        
        service.lastUpdate = self.updated
        service.save()
    
    def close(self):
        self._conn.close()