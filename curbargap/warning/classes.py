import http.client
import feedparser
import json
import socket
from django.utils.dateparse import parse_datetime

from phonenumber_field.phonenumber import PhoneNumber

#import pyshorteners

from django.conf import settings

from warning.models import Warning, Service, Location, Subscription, Device

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
        # This is the more common processing where we just get the updates
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

class SMS_message(object):
    def __init__(self,server,port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((server, port))
        except ConnectionRefusedError:
            print("Connection to {} {} refused".format(server,port))  
            self.client_socket = None
        
    def send_all (self, numbers, messages):
        message_control = {}
        message_control ['action'] = 0 # Tell the message interface these are messages to send.
        message_control ['messages'] = []
        
        for n,m in zip(numbers, messages):
            nn = PhoneNumber.from_string(n) # convert to object to standardise...
            message_control['messages'].append ({'number': nn.as_e164, 'message' : m })

        if self.client_socket == None:
            print("Socket not initialised - skipping send")
            return
        
        self.client_socket.sendall(json.dumps(message_control).encode()) 

        response_data = self.client_socket.recv(1024)
        response_dict = json.loads(response_data.decode())
        print(f'Received: {response_dict}')
    
    def close(self):
        self.client_socket.close()     

class Notification(SMS_message):
    
    def __init__(self, warning_id, server,port):
        super().__init__(server,port)
        
        self.warning = Warning.objects.get(warningId=warning_id)
        self.warning_id = warning_id
        #self.notifiedDate = self.warning.notifiedDate 
        #print("self.notifiedDate {}".format(self.notifiedDate) )

    def send(self, debug=True):
        def create_entry (warning, subscription, contained=True):
            entry = {}
            entry['area'] = subscription.location.name
            entry['level'] = Warning.WarningLevel(warning.warningLevel).label
            entry['contained'] = contained
            entry['types'] = warning.display_weatherType()
            entry['device'] = subscription.device.phoneNumber 
            entry['from'] = warning.validFromDate
            entry['to'] = warning.validToDate
            entry['status'] = warning.warningStatus
            entry['url'] = settings.SITE_URL + '/w/' + warning.hash
            #entry['url'] = settings.SITE_URL + "/warning/warning/"
            # extra info
            entry['issued'] = warning.issuedDate
            entry['modified'] = warning.modifiedDate
            entry['status']  = warning.warningStatus
            
            return entry
        
        #tiny = pyshorteners.Shortener() # used in closure send

        # OK we are potentially alerting this if it affects any of the subscribed locations
        # Generate a list of dictionaries of all the messages to be sent
        #
        send_list = []
        # get a list of locations completely inside the warning area
        # 
        inside = Location.objects.filter(area__coveredby=self.warning.geometry)  
        
        # all the subscriptions for the area
        inside_subs = Subscription.objects.none() # we are going to add to this
        for i in inside:
            inside_subs = inside_subs.union(Subscription.objects.filter(location=i)) 

        # for each subscription, get all the data we need to send to a device
        notify_list = []
        for isb in inside_subs:
            entry = create_entry(self.warning, isb, True)
            notify_list.append(entry)

        # Next get a list of locations partly coverd by warning area. EG for
        # England, a warning might only be in place for West Midlands
        #    
        touching =  Location.objects.filter(area__overlaps=self.warning.geometry)
        
        touching_subs = Subscription.objects.none()
        
        for t in touching:
            touching_subs = touching_subs.union(Subscription.objects.filter(location=t)) 

        for tsb in touching_subs:
            entry = create_entry(self.warning, tsb, False)
            notify_list.append(entry)

        if debug: 
            print("message list")
            print("************")
        
        message_line = "{} warning of {} {} for {}{} from {} {}"
        
        message_control = {}
        message_control ['action'] = 0 # Tell the message interface these are messages to send.
        message_control ['messages'] = [] # Will be a list of dictionary items ['number' ['message']]
        
        numbers = []
        messages = []

        for n in notify_list:
            
            # expand weather types
            weather_types = ""
            for i, w in enumerate(n['types']):
                if i > 0:
                    weather_types = weather_types + "/"
                weather_types = weather_types + w
            
            if n['contained']:
                contained = ""
            else:
                contained = "parts of "    
            
            # check if this is an update to a warning
            if n['modified'] > n['issued']:
                action = "updated"
            else: 
                action = "issued"
            
            out = message_line.format(
                                      n['level'].upper(),
                                      weather_types,
                                      action,
                                      contained,
                                      n['area'],
                                      n['from'].strftime("%c"),
                                      #n['to'].strftime("%c"),
                                      n['url'] )
            

            if n['status'] == 1: # only issued at the moment. Updates ot follow
                numbers.append(n['device'].as_e164)
                messages.append(out)
            
            if debug: 
                print("Status:{}".format(n['status']))
                print(n['device'].as_e164 + ":" + out)

        self.send_all(numbers,messages)
    
    def close(self):
        super().close()    