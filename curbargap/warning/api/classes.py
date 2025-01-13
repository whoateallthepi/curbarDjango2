from ..models import Location, Device, Subscription

from django.db.utils import IntegrityError

from phonenumber_field.phonenumber import PhoneNumber

class MessageHandler (object):
    def __init__(self, message_in):
        try:
            self.message = message_in['message'].upper()
            self.number = message_in['number']
        except:
            raise ValueError("Usage: MessageHandler({'number': 447806xxxx , 'message': 'Help'}")

    def reply (self):
        # hardcoded messages for now....
        # 
        #               
        if self.message.startswith("HELP") | self.message.startswith("INFO") :
            return ("curbargap.info weather warning service (BETA testing). "
                    "Reply SUBSCRIBE <area> to subscribe, "
                    "AREAS for available <area>(s), "
                    "SUBSCRIPTIONS to see your subscriptions, "
                    "STOP to stop messages."
                    )
        
        elif self.message.startswith("SUBSCRIBE"):
            area = self.message.split()[1].upper()

            phone = PhoneNumber.from_string(self.number)

            try:
                location = Location.objects.get(name=area)
            except Location.DoesNotExist:
                return("Area {} is not on our system. For a list of available areas, reply: AREAS".format(area))    

            device, _ = Device.objects.get_or_create(type=Device.DeviceType.SMS, phoneNumber=phone)

            try:
                subscription = Subscription.objects.create(device=device,
                                                        location = location,
                                                        type = Subscription.SubscriptionType.WEATHER)
            except IntegrityError:
                return ("You were already subscribed to warnings for {}. For help, reply: HELP".format(area))

            return("Subscribed to weather warnings for {}.".format(area))
        
        elif self.message.startswith("STOP"):
            phone = PhoneNumber.from_string(self.number)

            try:
                device = Device.objects.get(phoneNumber=phone, type = Device.DeviceType.SMS) 
            except Device.DoesNotExist:
                return ("Your device was not registered with us. For help, text: HELP")

            #breakpoint()
            
            device.delete()
            
            return("All messages stopped for {}".format(self.number)) 
        
        elif self.message.startswith("AREAS"):
            
            areas = ""
            for l in Location.objects.all():
                areas += l.name.upper() + ' '
           
            return("Avaliable areas are: {}. To subscribe to warnings for an area, reply SUBSCRIBE <area>.".format(areas))
        
        elif self.message.startswith("SUBSCRIPTIONS"):
            phone = PhoneNumber.from_string(self.number)
            try:
                device = Device.objects.get(phoneNumber=phone, type = Device.DeviceType.SMS) 
            except Device.DoesNotExist:
                return ("Your device is not registered with us. For help, text: HELP")
            
            areas = ""
            for s in Subscription.objects.all().filter(device=device):
                areas += s.location.name.upper() + ' '

            return ("You are receiving warning for areas {}.".format(areas))    
        else:
            return("Unrecognised message. For help reply: HELP")
        