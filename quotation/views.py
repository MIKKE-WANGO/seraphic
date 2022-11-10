
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
from asyncio import events
import email
from django.core.mail import EmailMessage
from unicodedata import name
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

from django.http import FileResponse

import math
from django.utils.timezone import make_aware
from django.core.mail import send_mail
from django.contrib.postgres.search import SearchQuery,  SearchVector
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny

#import pagination
from django.core.paginator import Paginator

#pdf 
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
#ensures table is on center of page
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.platypus import Paragraph, Spacer,Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
import csv
#from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
#from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self,request, format=None):
        data = request.data
        name = data['name']
        email = data['email']
        email = email.lower()
        password = data['password']
        phone = data['phone']
   
        if len(password) >=6:
            
            if not User.objects.filter(email=email).exists():
            
                User.objects.create_superuser(name=name, email=email, password=password,phone=phone)
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

class ManageEvent(APIView):
    #check if an event that has not been submitted exists and if it does send back its details
    def get(self, request, format=None):
        user = request.user
        if Event.objects.filter(user=user,submitted=False).exists():
            event = Event.objects.get(user=user,submitted=False)
            
            event = EventSerializer(event)
            return Response(
                {'event': event.data, 'exists':True},
                status=status.HTTP_200_OK
            )
        
        else:
            return Response(
                {'exists':False},
                status=status.HTTP_200_OK
            )
           
    #create a new event & if a user has an event that is not submitted i delete it
    def post(self, request, format=None):
        user = request.user
        data = request.data
        title = data['title']
        budget = data['budget']
        guests = data['guests']
        date = data['date']

        if Event.objects.filter(user=user, submitted=False).exists():
            event=Event.objects.get(user=user,submitted=False)
            event.delete()

        event = Event(user=user,title=title,budget=budget, guests=guests,date=date)
        event.save()
        return Response(
                {'success': 'Event successfully created'},
                status=status.HTTP_201_CREATED
            )

class DeleteEvent(APIView):
     def get(self, request, format=None):
        user = request.user
        if Event.objects.filter(user=user, submitted=False).exists():
            event=Event.objects.get(user=user,submitted=False)
            event.delete()
        return Response(
                {'success': 'Event successfully deleted'},
                status=status.HTTP_201_CREATED
            )


class ProductsCategoryView(APIView):
    permission_classes = (permissions.AllowAny,) 

    #Get products according to their category e.g tents,chairs
    def post(self, request, format=None):
        data = request.data
        category = data['category']
        
        category = Category.objects.get(name=category)

        #order objects randomly
        products = Product.objects.filter(category=category).order_by('?')
        products = ProductSerializer(products, many=True)
      
        return Response(
            {'products': products.data},
            status=status.HTTP_200_OK
        )  

class TentView(APIView):
    permission_classes = (permissions.AllowAny,) 
    
    def get(self, request, pk):
        product = Product.objects.get(id=pk)
        name = product.name + " draping"
        draping = False
        capacity = False
        tent = ProductSerializer(product)  
        if Product.objects.filter(name=name).exists():
            draping = Product.objects.get(name=name)
            draping = ProductSerializer(draping)

            if Capacity.objects.filter(tent=product).exists():
                capacity = Capacity.objects.get(tent=product)           
                capacity = CapacitySerializer(capacity)
                         
                return Response(
                    {'tent': tent.data, 'draping': draping.data, 'capacity':capacity.data },
                    status=status.HTTP_200_OK
                    )  
            else:
                return Response(
                    {'tent': tent.data, 'draping': draping.data, 'capacity':capacity },
                    status=status.HTTP_200_OK
                    ) 
        else:
            if Capacity.objects.filter(tent=product).exists():
                capacity = Capacity.objects.get(tent=product)           
                capacity = CapacitySerializer(capacity)
                return Response(
                {'tent': tent.data, 'draping': draping, 'capacity':capacity.data },
                status=status.HTTP_200_OK
                )
            else:
                return Response(
                {'tent': tent.data, 'draping': draping, 'capacity':capacity },
                status=status.HTTP_200_OK
                )
            
 
class BudgetLeft(APIView):
    def get(self, request, format=None):
        user = request.user
        event = Event.objects.get(user=user, submitted=False)
        budget = event.budget
        guests = event.guests
        price = event.get_total_price
        money_left = budget - price
        
        return Response(
            {'money_left':money_left,'budget':budget,'guests':guests },
            status=status.HTTP_200_OK
        )  


class AddProductToEvent(APIView):
    def post(self, request, format=None):
        user = request.user
        event = Event.objects.get(user=user, submitted=False)
        data = request.data
        product = Product.objects.get(id=data['productId'])
        quantity = int(data['quantity'])
        #if product exists change the quantity only else create 
        if EventProduct.objects.filter(event=event, product=product).exists():
            eventproduct = EventProduct.objects.get(event=event, product=product)
            eventproduct.quantity = quantity + eventproduct.quantity
            eventproduct.save()
        else:
            eventproduct = EventProduct(event=event, product=product, quantity=quantity)
            eventproduct.save()
        return Response(
                {'success': 'EventProduct successfully created'},
                status=status.HTTP_201_CREATED
            )

     
class ChairView(APIView):
    permission_classes = (permissions.AllowAny,) 
    
    def get(self, request, pk):
        product = Product.objects.get(id=pk)
        sitcovers = False
        tiebacks = False
        chair = ProductSerializer(product)
        sitcoversubcategory = SubCategory.objects.get(name='sitcover')
        tiebacksubcategory = SubCategory.objects.get(name='tieback')
        chiavari_subcategory = SubCategory.objects.get(name='chiavari chair')

        if product.name == 'Plastic chair':
            sitcovers = Product.objects.filter(subcategory=sitcoversubcategory)
            tiebacks = Product.objects.filter(subcategory=tiebacksubcategory)
            sitcovers = ProductSerializer(sitcovers,many=True)
            tiebacks = ProductSerializer(tiebacks,many=True)
            return Response(
                {'chair': chair.data, 'sitcovers': sitcovers.data, 'tiebacks':tiebacks.data },
                status=status.HTTP_200_OK
                )

        if product.subcategory == chiavari_subcategory:
             
            tiebacks = Product.objects.filter(subcategory=tiebacksubcategory)
            tiebacks = ProductSerializer(tiebacks,many=True)
            return Response(
                {'chair': chair.data, 'sitcovers':False, 'tiebacks':tiebacks.data },
                status=status.HTTP_200_OK
                )

        return Response(
                {'chair': chair.data, 'sitcovers':False, 'tiebacks':False },
                status=status.HTTP_200_OK
                )
        


class TableView(APIView):
    permission_classes = (permissions.AllowAny,) 
    
    def get(self, request, pk):
        product = Product.objects.get(id=pk)
        tablecloth = False
        overlay = False
        table = ProductSerializer(product)
        overlay_category = SubCategory.objects.get(name='overlay')
        tablecloth_category = SubCategory.objects.get(name='tablecloth')
        tablecloth = Product.objects.filter(subcategory=tablecloth_category)
        overlay = Product.objects.filter(subcategory=overlay_category)
        tablecloth = ProductSerializer(tablecloth, many=True)
        overlay = ProductSerializer(overlay, many= True)
        return Response(
                {'table': table.data, 'tablecloth':tablecloth.data, 'overlay':overlay.data },
                status=status.HTTP_200_OK
                )

class DecorView(APIView):
    permission_classes = (permissions.AllowAny,) 
    
    def get(self, request, pk):
        product = Product.objects.get(id=pk)
        product = ProductSerializer(product)
        return Response(
                {'decor': product.data,  },
                status=status.HTTP_200_OK
                )

class Review(APIView):
    
    def get(self, request,):
        user = request.user
        event = Event.objects.get(user=user,submitted=False)
        event_price = event.get_total_price
        event_products = event.eventproduct_set.all()
        products = []
        for item in event_products:
            #get serialized image from product table
            p = Product.objects.get(id=item.product.id)
            p = ProductSerializer(p)
            p = p.data
            name = p['name']
            price=p['price']
            product = {"id": item.id, "name": name, "price":price, "total_price":item.get_total_price,"quantity":item.quantity }
            products.append(product)
        return Response(
                {'event_products': products,'total_price':event_price  },
                status=status.HTTP_200_OK
                )

    #Delete an event_product
    def post(self, request,):
        user = request.user
        data = request.data
        id = data['id']
        event = Event.objects.get(user=user,submitted=False)
        event_product = EventProduct.objects.get(id=id,event=event)
        event_product.delete()

        return Response(
                {"success": 'deleted successfully' },
                status=status.HTTP_200_OK
                )

class QuoteView(APIView):
    def post(self, request,):
        user = request.user
        data = request.data
        id = data['id']
        
        event = Event.objects.get(user=user,submitted=True, id=id)
        #print(event)
        event_price = event.get_total_price
        event_products = event.eventproduct_set.all()
        products = []
        for item in event_products:
            #get serialized image from product table
            p = Product.objects.get(id=item.product.id)
            p = ProductSerializer(p)
            p = p.data
            name = p['name']
            price=p['price']
            product = {"id": item.id, "name": name, "price":price, "total_price":item.get_total_price,"quantity":item.quantity }
            products.append(product)
        return Response(
                {'event_products': products,'total_price':event_price  },
                status=status.HTTP_200_OK
                )

#Send pdf after submitting to user and seraphic
class SubmitQuote(APIView):
    def get(self, request):
        user = request.user
        event = Event.objects.get(user=user,submitted=False)
        event_price = event.get_total_price
        event.submitted = True
        event.date_submitted = datetime.now()
        event.save()

        #add lines of text
        event_products = event.eventproduct_set.all()
        products = [['Name', 'Quantity', 'Unit Price', 'Total Price',]]
        for item in event_products:
            #get serialized image from product table
            p = Product.objects.get(id=item.product.id)
            p = ProductSerializer(p)
            p = p.data
            name = p['name']
            price=p['price']
            product = [name,item.quantity,price,item.get_total_price,]
            products.append(product)
        
        end = [' ', ' ', 'TOTAL COST', event_price]
        products.append(end)

        filename = 'Quote.pdf'

        pdf = SimpleDocTemplate(
            filename,
            pagesize=letter
        )
        
        table = Table(products)

        style = TableStyle([
        #('ALIGN',(0,0),(-1,-1), 'CENTER'),
        #('FONTNAME', (0,0),(-1,0), 'Courier-Bold'),
        ('FONTSIZE',(0,0),(-1,0), 15),
        ('BOTTOMPADDING',(0,0),(-1,0),12),
        ('BACKGROUND', (0,0),(-1,0), colors.firebrick),
        #('BACKGROUND', (0,1),(-1,-1), colors.beige),,
        ('BOTTOMPADDING',(0,1),(-1,-1),10),
        ('TOPPADDING',(0,1),(-1,-1),10),
        ('LINEBELOW',(0,-1),(-1,-1),2,colors.firebrick)
        

        ])
        table.setStyle(style)

        #alternate background row colors
        rowNum = len(products)
        for i in range(1,rowNum):
            if i % 2 ==0:
                color= colors.whitesmoke
                text = colors.firebrick
            else:
                color = colors.white
                text = colors.black

            ts = TableStyle([
                ('BACKGROUND', (0,i),(-1,i), color),
                ('TEXTCOLOR',(0,i),(-1,i), text),
                ('TEXTCOLOR',(0,-1),(-1,-1), colors.orange),
                
            ])
            table.setStyle(ts)
            
        a = Image('./Seraphic-logo.jpg')  
        a.drawHeight = 1.3*inch
        a.drawWidth = 3*inch

        elems = []
        elems.append(a)
        elems.append(Paragraph('Title: '+ event.title))
        elems.append(Paragraph('Name: '+ user.name))
        elems.append(Paragraph('Email: '+ user.email))
        elems.append(Paragraph('Mobile: '+ user.phone))

        elems.append(Spacer(5 * cm, 1 * cm))
        elems.append(table)
        
        pdf.build(elems)

        with open('quote.csv', 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',dialect='excel')
            spamwriter.writerows(products)
    
        #sent to client
        message = EmailMessage(
            'Quotation from Seraphic',
            'Your quotation has been Received by our team.\nYou will hear from us soon.\nBelow is a copy of your quoation',
            'mikemundati@gmail.com',
            [user.email],
        )
        message.attach_file(BASE_DIR/'Quote.pdf')
        message.send(fail_silently=False)

        #sent to seraphic
        message = EmailMessage(
            'New quotation',
            'Client details are in the pdf.\nOpen the csv file with excel.',
            'mikemundati@gmail.com',
            ['mikemundati@gmail.com'],
        )
        message.attach_file(BASE_DIR/'Quote.pdf')
        message.attach_file(BASE_DIR/'quote.csv')
        message.send(fail_silently=False)

        return Response(
                {"success": 'Submitted successfully' },
                status=status.HTTP_200_OK
                )



def pdf_view(request):
    user = User.objects.get(email='mikemundati@gmail.com')
    event = Event.objects.get(user=user,submitted=False)
    event_price = event.get_total_price
   
    #add lines of text
    event_products = event.eventproduct_set.all()
    products = [['Name', 'Quantity', 'Unit Price', 'Total Price',]]
    for item in event_products:
        #get serialized image from product table
        p = Product.objects.get(id=item.product.id)
        p = ProductSerializer(p)
        p = p.data
        name = p['name']
        price=p['price']
        product = [name,item.quantity,price,item.get_total_price,]
        products.append(product)
    
    end = [' ', ' ', 'TOTAL COST', event_price]
    products.append(end)

    filename = 'Quote.pdf'

    pdf = SimpleDocTemplate(
        filename,
        pagesize=letter
    )
    
    table = Table(products)

    style = TableStyle([
       #('ALIGN',(0,0),(-1,-1), 'CENTER'),
       #('FONTNAME', (0,0),(-1,0), 'Courier-Bold'),
       ('FONTSIZE',(0,0),(-1,0), 15),
       ('BOTTOMPADDING',(0,0),(-1,0),12),
       ('BACKGROUND', (0,0),(-1,0), colors.firebrick),
       #('BACKGROUND', (0,1),(-1,-1), colors.beige),,
       ('BOTTOMPADDING',(0,1),(-1,-1),10),
       ('TOPPADDING',(0,1),(-1,-1),10),
       ('LINEBELOW',(0,-1),(-1,-1),2,colors.firebrick)
       

    ])
    table.setStyle(style)

    #alternate background row colors
    rowNum = len(products)

    

    for i in range(1,rowNum):
        if i % 2 ==0:
            color= colors.whitesmoke
            text = colors.firebrick
        else:
            color = colors.white
            text = colors.black

        ts = TableStyle([
            ('BACKGROUND', (0,i),(-1,i), color),
            ('TEXTCOLOR',(0,i),(-1,i), text),
            ('TEXTCOLOR',(0,-1),(-1,-1), colors.orange),
            
        ])
        table.setStyle(ts)


 
        
    a = Image('./Seraphic-logo.jpg')  
    a.drawHeight = 1.3*inch
    a.drawWidth = 3*inch

    elems = []
    elems.append(a)
    elems.append(Paragraph('Title: '+ event.title))
    elems.append(Paragraph('Name: '+ user.name))
    elems.append(Paragraph('Email: '+ user.email))
    elems.append(Paragraph('Mobile: '+ user.phone))

    elems.append(Spacer(5 * cm, 1 * cm))
    elems.append(table)
    
    pdf.build(elems)
    print('build')

    with open('quote.csv', 'w') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',dialect='excel')
        spamwriter.writerows(products)
   
    message = EmailMessage(
        'Quotaion Received',
        'Your quotation has been Received by our team.\nYou will hear from us soon.\nBelow is a copy of your quoation',
        'mikemundati@gmail.com',
        [user.email],
       )
    message.attach_file(BASE_DIR/'Quote.pdf')
    message.send(fail_silently=False)

    message = EmailMessage(
        'New quotation',
        'Client details are in the pdf.\nOpen the csv file with excel.',
        'mikemundati@gmail.com',
        ['mikemundati@gmail.com'],
       )
    message.attach_file(BASE_DIR/'Quote.pdf')
    message.attach_file(BASE_DIR/'quote.csv')
    message.send(fail_silently=False)

    return FileResponse(pdf,as_attachment=True, filename='quote.pdf')


class QuotationList(APIView):
    def get(self, request):
        user = request.user
        events = Event.objects.filter(user=user,submitted=True) 
        quotations = []
        for event in events:
            q = {'name': event.title, 'total_price': event.get_total_price,'guests':event.guests, 'id':event.id}
            quotations.append(q)
        return Response(
                {"events": quotations },
                status=status.HTTP_200_OK
                )
