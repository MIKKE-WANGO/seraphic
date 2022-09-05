import json
from re import S
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response 
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.contrib.auth import get_user_model
User = get_user_model()

from .serializers import *
from .models import *
import random
from datetime import datetime,timedelta

import math
from django.utils.timezone import make_aware
from django.core.mail import send_mail
from django.contrib.postgres.search import SearchQuery,  SearchVector
from rest_framework.decorators import api_view,permission_classes

from rest_framework.permissions import AllowAny


class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self,request, format=None):
        data = request.data
        name = data['name']
        email = data['email']
        email = email.lower()
        password = data['password']
   
        if len(password) >=6:
            
            if not User.objects.filter(email=email).exists():
            
                User.objects.create_user(name=name, email=email, password=password)
                return Response(
                            {'success': 'User created successfully'},
                            status=status.HTTP_201_CREATED
                        )
            else:
                return Response(
                    {'error': 'User with this email already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
 
        else:
            return Response(
                    {'error': 'Password must be at least 6 characters long'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
#get user details
class RetrieveUserView(APIView):
    def get(self, request, format=None):
        try:
            user = request.user
            print(user)
            user = UserSerializer(user)
            return Response(
                {'user': user.data},
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'error': 'Something went wrong when retrieving the user details'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def createResetPasswordCode():  
    ## storing strings in a list
    digits = [i for i in range(0, 10)]
    ## initializing a string
    code = ""
    ## we can generate any length of string we want
    for i in range(6):
        index = math.floor(random.random() * 10)
        code += str(digits[index])

    return code

class SendResetPasswordCode(APIView):
    permission_classes = (permissions.AllowAny,)

    #create otp save it in db and send it through email
    def post(self, request, format=None):
        data = request.data
        email = data['email']
        print(request.user)
        if  User.objects.filter(email=email).exists():
            
            otp = createResetPasswordCode()
            
            expiry_date = datetime.now() + timedelta(hours=0, minutes=10, seconds=0)            

            new_otp = ResetPasswordCode(email=email, code=otp, expiry_date=expiry_date)
            new_otp.save()

            send_mail("OTP", "Your otp is " + otp + " .It will expire in 10 minutes", "mikemundati@gmail.com",[ email], fail_silently=False)
            return Response(
                                    {'success': 'Otp sent successfully'},
                                    status=status.HTTP_201_CREATED
                                )

        else:
             return Response(
                            {'error': 'User with this email does not  exists'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

class TesCode(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        data = request.data
        otp = data['code']
        email = data['email']

        #check if otp exists
        exists = ResetPasswordCode.objects.filter(code=otp, email=email).exists()
        #check if otp has not expired
        valid = ResetPasswordCode.objects.filter(code=otp, email=email, expiry_date__gt =datetime.now()).exists()
        
        if (exists):
            if (valid):
             
                    otp_delete = ResetPasswordCode.objects.get(code=otp, email=email, expiry_date__gt =datetime.now())
                    
                    return Response(
                            {'success': ' Code is valid '},
                            status=status.HTTP_201_CREATED
                        )      
                
            else:
                #if otp has expired
                #delete otp
                otp_delete = ResetPasswordCode.objects.get(code=otp, email=email, expiry_date__lt =datetime.now())
                otp_delete.delete()

                return Response(
                    {'error': ' OTP has expired'},
                    status=status.HTTP_400_BAD_REQUEST
                )      
        else:
            return Response(
                    {'error': 'Invalid OTP'},
                    status=status.HTTP_400_BAD_REQUEST
                )

class ResetPassword(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        data = request.data
        otp = data['code']
        email = data['email']
        password = data['password']
        
        #check if otp exists
        exists = ResetPasswordCode.objects.filter(code=otp, email=email).exists()
        #check if otp has not expired
        valid = ResetPasswordCode.objects.filter(code=otp, email=email, expiry_date__gt =datetime.now()).exists()
        
        
        if (exists):
            if (valid):
                if len(password) >=6:
                    #if otp is valid
                    #reset password
                    user = User.objects.get(email=email)
                    user.set_password(password)
                    user.save()

                    #delete otp
                    otp_delete = ResetPasswordCode.objects.get(code=otp, email=email, expiry_date__gt =datetime.now())
                    otp_delete.delete()

                    return Response(
                            {'success': ' password reset '},
                            status=status.HTTP_201_CREATED
                        )
                
                else:
                    return Response(
                        {'error': 'Password must be at least 6 characters long'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
            else:
                #if otp has expired
                #delete otp
                otp_delete = ResetPasswordCode.objects.get(code=otp, email=email, expiry_date__lt =datetime.now())
                otp_delete.delete()

                return Response(
                    {'error': ' OTP has expired'},
                    status=status.HTTP_400_BAD_REQUEST
                )      
        else:
            return Response(
                    {'error': 'Invalid OTP'},
                    status=status.HTTP_400_BAD_REQUEST
                )
