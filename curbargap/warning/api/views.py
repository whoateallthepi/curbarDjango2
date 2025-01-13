from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from ..models import Warning
from .serializers import WarningSerializer

from django.db import transaction
from django.conf import settings

from ..classes import SMS_message

from .classes import MessageHandler

import json

class WarningListView(generics.ListAPIView):
    queryset = Warning.objects.all()
    serializer_class = WarningSerializer

class WarningDetailView(generics.RetrieveAPIView):
    queryset = Warning.objects.all()
    serializer_class = WarningSerializer   

class IncomingMessageView(APIView):
    queryset = Warning.objects.all()
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post (self, request, *args, **kwargs):
        def send_message (message, number):
            s = SMS_message(settings.SMS_SERVER,settings.SMS_PORT)
            m = [message]
            n = [number]

            s.send_all(n,m)
        
        data = json.loads(request.body)
        
        number = data['number']
        message = data['message']
        print("Message {} received from {}".format(message, number)) 
        mm = MessageHandler(data)       
        reply = mm.reply()

        transaction.on_commit(lambda: send_message(reply, number))
        
        return Response ({'message_reply': reply, 'number': number})