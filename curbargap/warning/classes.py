import http.client
import feedparser
import json

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

    def check(self):
        self.updates = []
        self._conn.request("GET", self.feeds_url, headers=self.headers)
        data = self._conn.getresponse().read()
        p = feedparser.parse(data)
        self.latest_list_url = p['feed']['links'][1]['href']
        self.updated = p['feed']['updated']
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
        
    def fetch_updates(self):
        print('Update')
        #breakpoint()
        updates = []
        for update in self.updates:
            u = {}
            
            url, action, time = update # unpack the update
            
            # get the warning details
            self._conn.request("GET", url, headers=self.headers)
            url = url.split('https://'+ self.base_url,1)[1]
            #breakpoint()
            data = self._conn.getresponse().read()
            
            # should be json data
            j = json.loads(data)
           
            # Pick out the useful stuff
            f1 = j['features'][0] # assuming one feature per warning??
            breakpoint()
            
            u['issuedDate'] = f1['properties']['issuedDate']
            u['weatherType'] = f1['properties']['weatherType']
            u['warningLikelihood'] = f1['properties']['warningLikelihood']
            u['warningLevel'] = f1['properties']['warningLevel']
            u['warningStatus'] = f1['properties']['warningStatus']
            u['warningHeadline'] = f1['properties']['warningHeadline']
            u['whatToExpect'] = f1['properties']['whatToExpect']
            u['warningId'] = f1['properties']['warningId']
            u['modifiedDate'] = f1['properties']['modifiedDate']
            u['validFromDate'] = f1['properties']['validFromDate']
            u['validToDate'] = f1['properties']['validToDate']
            u['affectedAreas'] = json.dumps(f1['properties']['affectedAreas'])
            u['warningImpact'] = f1['properties']['warningImpact']
            u['geometry'] = f1['geometry']
            
            updates.append(u)

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
                wte = wte + expect + '\n'

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
                geometry = update['geometry'],
            )
            breakpoint()    
        
        breakpoint()

        warning, created = Warning.objects.get_or_create(warningId=updates[warningId])
        breakpoint()

    
    def close(self):
        self._conn.close()