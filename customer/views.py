from email import policy
from multiprocessing.sharedctypes import Value
from typing import Type
from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required,user_passes_test
from django.shortcuts import get_object_or_404
from django.conf import settings
from coinbase_commerce.client import Client
from decimal import Decimal
from django.core.paginator import Paginator
from datetime import date, datetime
from django.utils.datastructures import MultiValueDictKeyError
from django.core.files.uploadedfile import InMemoryUploadedFile
import mimetypes
from django.db.models import Q
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from backoffice import models as CMODEL
from backoffice import forms as CFORM
from django.contrib.auth.models import User
from turtle import end_fill
from django.views.decorators.csrf import csrf_exempt
from PIL import Image, ImageDraw, ImageFont
import json
import os
import cv2
import numpy as np
from pytesseract import Output
import arabic_reshaper
import random
import math
from scipy.ndimage import interpolation as inter
import matplotlib.pyplot as plt
from ArabicOcr import arabicocr
from easyocr import Reader
import re
import pytesseract
import Levenshtein
from bidi.algorithm import get_display
from pyzbar.pyzbar import *
from glob import glob
import multiprocessing
import time
import subprocess
import string
import stripe
from django.http.response import JsonResponse
from .chat import get_response, predict_class
import fitz
from backoffice.models import Course
import pandas as pd
import copy
from .utils import setup_job, MyJsonEncoder,PyeScheduler
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


 

def auto_correction_word(bad_word,model_path,data_path):
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    from tensorflow.keras.preprocessing.text import Tokenizer
    from tensorflow import keras
    import numpy as np
    model = keras.models.load_model(model_path)
    tokenizer = Tokenizer()
    data = open(data_path, encoding="utf8").read()
    corpus = data.split("\n")
    for i in corpus:
        if i == "":
            corpus.remove('')
    corpus = corpus[1:-1]
    corpus_new = []
    for st in corpus:
        ch = " ".join(st)
        corpus_new.append(ch)
    tokenizer.fit_on_texts(corpus_new)
    total_words = len(tokenizer.word_index) + 1
    #############################################################################
    input_sequences = []
    for line in corpus_new:
        token_list = tokenizer.texts_to_sequences([line])[0]
        for i in range(1, len(token_list)):
            n_gram_sequence = token_list[:i + 1]
            input_sequences.append(n_gram_sequence)

    # pad sequences
    max_sequence_len = max([len(x) for x in input_sequences])
    input_sequences = np.array(pad_sequences(input_sequences, maxlen=max_sequence_len, padding='pre'))
    counter = len(bad_word)
    for i in range(counter):
        if (ord(bad_word[i]) in [i for i in range(285)]) == True:
            seed_text = " ".join(bad_word[:i])
            noTraited_text = " ".join(bad_word[i + 1:])
            next_words = 100

            for _ in range(next_words):
                token_list = tokenizer.texts_to_sequences([seed_text])[0]
                token_list = pad_sequences([token_list], maxlen=max_sequence_len - 1, padding='pre')
                #     predicted = model.predict_classes(token_list, verbose=0)
                predicted = np.argmax(model.predict(token_list), axis=1)
                output_word = ""
                for word, index in tokenizer.word_index.items():
                    if index == predicted:
                        output_word = word
                        break
            seed_text += " " + output_word + " " + noTraited_text
            bad_word = "".join(seed_text.split())
    return bad_word

def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# Réduction de bruits
def remove_noise(image):
    return cv2.medianBlur(image, 1)
# Seuillage
def thresholding(image):
    return cv2.threshold(image, 200, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]



def correct_ocr_order(results, pixels=25):
    text = []
    for i in range(len(results)):
        l = [[results[i][1],results[i][0][0][0]]]
        for j in range(len(results)):
            c=0
            if(i==j):
                continue
            for k in range(4):
                if abs(results[i][0][k][1]-results[j][0][k][1])<=pixels:
                    c+=1
            w = results[i][0][0][1]
            if(c>=3):
                l.append([results[j][1],results[j][0][0][0]])
                w = results[i][0][0][1]
                results[j][1]=''
        l = sorted(l,key=lambda x:round(x[1]),reverse=True)
        a=0
        for p in range(len(l)):
            if '' in l[p]:
                a+=1
        sentence = [l[i][0] for i in range(len(l))]
        phrase = ' '.join(sentence)
        if(a==0):
            text.append([phrase,w])
    text = sorted(text,key=lambda x:round(x[1]))
    return text

def correct_ocr_output(input):
    output=input
    output.replace('$','S')
    output.replace("()",'0')
    liste = [x for x in output]
    liste1 = ["" if x in set(string.punctuation) else x for x in liste]
    return "".join(liste1)

def correct_orientation(image, delta=.1, limit=45):
    def determine_score(arr, angle):
        data = inter.rotate(arr, angle, reshape=False, order=0)
        histogram = np.sum(data, axis=1)
        score = np.sum((histogram[1:] - histogram[:-1]) ** 2)
        return histogram, score

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 3)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1] 

    scores = []
    angles = np.arange(-limit, limit + delta, delta)
    for angle in angles:
        histogram, score = determine_score(thresh, angle)
        scores.append(score)

    best_angle = angles[scores.index(max(scores))]

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, best_angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, \
              borderMode=cv2.BORDER_REPLICATE)

    return best_angle, rotated

def customerclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('customer-dashboard')
    return redirect('login')

@csrf_exempt
def checkout_view(request,pk):
    if request.method=='GET':
        customer = models.Customer.objects.get(user_id=request.user.id)
        policy_record = CMODEL.LeaveRecord.objects.get(customer=customer, id=pk)
        domain_url = 'http://localhost:8000/customer/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see https://stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        checkout_session = stripe.checkout.Session.create(
        success_url=domain_url + 'contracts',
        cancel_url=domain_url + 'dashboard',
        payment_method_types=['card'],
        mode='payment',
        client_reference_id=str(pk)+'_'+str(request.user.id)+'_'+"payment",
        customer_email=customer.email,
        line_items=[
                    {
                        'name': policy_record.Vocation.policy_name,
                        'quantity': 1,
                        'currency': 'eur',
                        'amount': int(policy_record.Vocation.sum_assurance * 106)
                    }
                ]
            )
        return redirect(checkout_session.url)
    return redirect('contracts')

# @csrf_exempt
# def process_payment(request,pk):
#     customer = models.Customer.objects.get(user_id=request.user.id)
#     policy_record = CMODEL.LeaveRecord.objects.get(customer=customer, id=pk)
#     order_id = request.session.get('order_id')
#     host = 'localhost:8000/customer/'
#     paypal_dict = {
#         'business': settings.PAYPAL_RECEIVER_EMAIL,
#         'amount': int(policy_record.Vocation.sum_assurance * 1.06),
#         'item_name': 'Order {}'.format(policy_record.id),
#         'invoice': str(request.user.id)+" "+str(pk),
#         'currency_code': 'USD',
#         'notify_url': 'http://{}{}'.format(host,
#                                            reverse('paypal-ipn')),
#         'return_url': 'http://{}{}'.format(host,
#                                            reverse('contracts')),
#         'cancel_return': 'http://{}{}'.format(host,
#                                               reverse('contracts')),
#     }
#     return redirect(paypal_dict['notify_url'])

@csrf_exempt
def coinbase_checkout_view(request,pk):
    if request.method=='GET':
        customer = models.Customer.objects.get(user_id=request.user.id)
        policy_record = CMODEL.LeaveRecord.objects.get(customer=customer, id=pk)
        domain_url = 'http://localhost:8000/customer/'
        client = Client(api_key=settings.COINBASE_COMMERCE_API_KEY)
        product = {
            'name': policy_record.Vocation.policy_name,
            'description': 'A really good car backoffice deal.',
            'local_price': {
                'amount': int(policy_record.Vocation.sum_assurance * 1.06),
                'currency': 'TND'
            },
            'pricing_type': 'fixed_price',
            'redirect_url': domain_url + 'contracts',
            'cancel_url': domain_url + 'dashboard',
        }
        charge = client.charge.create(**product)
        return redirect(charge.hosted_url)
    return redirect('contracts')

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_id = session.client_reference_id.split("_")[1]
        contract_id = session.client_reference_id.split("_")[0]
        customer = models.Customer.objects.get(user_id=customer_id)
        policy_record = CMODEL.LeaveRecord.objects.get(customer=customer, id=contract_id)
        policy_record.status="Approved"
        policy_record.save()
        user_dir = os.path.join(settings.MEDIA_ROOT, "customer_{}".format(customer_id))
        invoice_path = os.path.join(user_dir,"INV-{}{}.pdf".format(customer_id,policy_record.id))
        contract_path = os.path.join(user_dir,"contrat_{}_{}.pdf".format(customer_id,policy_record.id))
        signature_path = os.path.join(settings.BASE_DIR,"signature.png")
     #   signature_add(invoice_path,signature_path,3000,950,0.6,0.9)
      #  signature_add(contract_path,signature_path,3100,1200,0.6,0.9)
        if customer.email_notifications:
            message = get_template("mail.html").render({'context':""})
            email = EmailMessage(
        'Paiement effectué avec succès',
        message,
        'keycorpsolutions@gmail.com',
        [customer.email],
    )
            #user_dir = os.path.join(settings.MEDIA_ROOT, "customer_{}".format(customer_id))
            email.content_subtype="html"
            #email.attach_file(os.path.join(user_dir,"contrat_{}_{}.png".format(customer_id,policy_record.id)))
            email.send()
        if customer.sms_notifications:
            pass
        if customer.call_notifications:
            pass
        if customer.whatsapp_notifications:
            pass
        intent = stripe.PaymentIntent.retrieve(session.payment_intent)
        used_card = intent.charges.data[0].payment_method_details.card
        if not CMODEL.Card .objects.all().filter(customer=customer,last4=used_card.last4,brand=used_card.brand):
            card = CMODEL.Card(customer=customer,holder=intent.charges.data[0].billing_details.name,brand=used_card.brand,last4=used_card.last4,exp_month=used_card.exp_month,exp_year=used_card.exp_year % 100)
            card.save()
        else:
            CMODEL.Card.objects.all().filter(customer=customer,last4=used_card.last4,brand=used_card.brand).update(holder=intent.charges.data[0].billing_details.name,exp_month=used_card.exp_month,exp_year=used_card.exp_year % 100)
    #return HttpResponse(status=200)
    return redirect('contracts')


def customer_signup_view(request):
    userForm=forms.CustomerUserForm()
    customerForm=forms.CustomerForm()
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST)
        customerForm=forms.CustomerForm(request.POST,request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customer=customerForm.save(commit=False)
            customer.user=user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
        return HttpResponseRedirect('login')
    return render(request,'home/sign-up.html',context=mydict)

def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()

def chatbot_view(request):
    if request.method=='GET':
        return render(request,'base.html')
    pass
    
@csrf_exempt
def predict_view(request):
    if request.method=='POST':
        text=json.load(request)['message']
        ints=predict_class(text)
        intents = json.loads(open('intents.json').read())
        response =get_response(ints,intents)
        message={'answer':response}
        return JsonResponse(message)
    return render(request,'customer/index.html')

def presentation_view(request):
    return render(request,'presentation.html') 

def rtl_view(request):
    dict={"segment":"rtl"}
    return render(request,'home/rtl.html',context=dict) 

def virtual_reality_view(request):
    dict={"segment":"virtual"}
    return render(request,'home/virtual-reality.html',context=dict)   

@login_required(login_url='login')
def customer_dashboard_view(request):

    dict={
        'customer':models.Customer.objects.get(user_id=request.user.id),
        'available_policy':CMODEL.Vocation.objects.all().count(),
        'applied_policy':CMODEL.LeaveRecord.objects.all().filter(customer=models.Customer.objects.get(user_id=request.user.id)).count(),
        'total_category':CMODEL.Category.objects.all().count(),
        'total_question':CMODEL.Question.objects.all().filter(customer=models.Customer.objects.get(user_id=request.user.id)).count(),
        "segment":"customer-dashboard",
        'course':CMODEL.Course.objects.all().count(),


        'courses' :CMODEL.Course.objects.filter(paid=True)


    }


    return render(request,'home/index.html',context=dict)

def customer_gopro_view(request):
    return render(request,'home/gopro.html')

def toggle_email_view(request):
    w = models.Customer.objects.get(id=request.POST['id'])
    w.email_notifications = request.POST['email_check'] == 'true'
    w.save()
    return HttpResponse('success')

def toggle_sms_view(request):
    w = models.Customer.objects.get(id=request.POST['id'])
    w.sms_notifications = request.POST['sms_check'] == 'true'
    w.save()
    return HttpResponse('success')

def toggle_call_view(request):
    w = models.Customer.objects.get(id=request.POST['id'])
    w.call_notifications = request.POST['call_check'] == 'true'
    w.save()
    return HttpResponse('success')

def toggle_whatsapp_view(request):
    w = models.Customer.objects.get(id=request.POST['id'])
    w.whatsapp_notifications = request.POST['whatsapp_check'] == 'true'
    w.save()
    return HttpResponse('success')


@login_required(login_url='login')
def profile_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    dict={'customer':customer,"segment":"profile"}
    return render(request,'home/profile.html',context=dict)   

@login_required(login_url='login')
def select_source_view(request,pk):
    connector= models.Connector.objects.get(pk=pk)
    dict={"segment":"connector","pk":pk,"connector":connector}
    return render(request,'home/task.html',context=dict) 


@login_required(login_url='login')
def select_source_delete(request,pk):
    connector= models.Connector.objects.get(pk=pk).delete()
    return redirect("connector-history")



    
@login_required(login_url='login')
def source_credential_view(request):    

    source_val = request.POST.get("connector_type","dummy")
    copy_postdata = copy.copy(request.POST)
    print(copy_postdata)
    post_data = {}
    if request.POST:  
        pk = request.POST.get("connector_pk")
        connector= models.Connector.objects.get(pk=pk)
        connector.connector_type = source_val
        connector.parameters = json.dumps(copy_postdata, cls=MyJsonEncoder)
        connector.save()

        if source_val=='flatfile':
            filetype = request.POST.get('filetype')
            files = request.FILES.getlist('files')
            file_list = []
            for file in files:
                my_file = models.FilesModel.objects.create(file=file,filetype=filetype,connector_id=connector.pk)
                file_list.append(my_file)
            connector.files.set(file_list)
            connector.save()
                

        return redirect('connector-history')

    else:
        source_val = request.GET.get("source-val","dummy")
        pk = request.GET.get("pk")
        connector= models.Connector.objects.get(pk=pk)

        data = []
        if source_val =='dummy':
            json_path = os.path.join(os.getcwd(),   'static', 'json', 'sample_data.json')
            with open(json_path,encoding="utf8") as f:
                data = json.load(f)['sample_data']

        if source_val=='task':
            data =  models.Task.objects.filter(created_by=request.user).order_by('-date_created').values("name","pk")

        if connector.parameters:
            post_data = json.loads(connector.parameters)



        dict={"segment":"connector","source_val":source_val,"data":data,"connector":connector,
        'post_data':post_data}
        return render(request,'home/credential.html',context=dict)  
    
@login_required(login_url='login')
def new_task_view(request):    

    task_pk = request.GET.get("task_pk")
    action = request.GET.get("action")

    task = {}
    if request.POST:
        name = request.POST.get('name')
        description = request.POST.get('description')
        created_by = request.user
        source_ids = request.POST.get('source')
        target_ids = request.POST.getlist('targets')
        transformers_ids = request.POST.getlist('transformers')
        schedule_time = request.POST.get('schedule_time')
        minute_time = request.POST.get('minute_time')
        daily_time = request.POST.get('daily_time') or None
        # weekly_day = request.POST.get('weekly_day')
        weekly_time = request.POST.get('weekly_time') or None
        
        # Get the Connector objects for source and target
        sources = models.Connector.objects.filter(id__in=source_ids)
        targets = models.Connector.objects.filter(id__in=target_ids)

        # Get the Transformer objects
        transformers = models.Transformer.objects.filter(id__in=transformers_ids)

           
        # Create the Task object

        try:
            task = models.Task.objects.get(name=name)
            task.description=description
            task.created_by=created_by
            task.schedule_time=schedule_time
            task.minute_time=minute_time
            task.daily_time=daily_time
            task.weekly_time=weekly_time 
            task.save()

        except ObjectDoesNotExist:
            task = models.Task.objects.create(name=name, description=description, created_by=created_by,
                schedule_time=schedule_time,minute_time=minute_time,daily_time=daily_time,
                weekly_time=weekly_time )


        save_days = [setattr(task, day,request.POST.get(day)) for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] if request.POST.get(day)]

        # Add the Source to the Task
        for connector in sources:
            task.source.add(connector)


        # Add the Target to the Task
        for connector in targets:
            task.targets.add(connector)
        
        # Add the Transformers to the Task
        for transformer in transformers:
            task.transformers.add(transformer)
        task.save()

        return redirect('apply-policy')

    else: 
        if task_pk:
            scheduler = PyeScheduler()
            task= models.Task.objects.get(pk=task_pk)
            if action == 'delete':
                scheduler.remove_job(task)
                task.delete()
                return redirect('apply-policy')
            elif action == "play":
                try:
                    scheduler.schedule_job(task)
                except Exception as e:
                    print('schedule error',e)
                    task.status = "error"
                    task.error = str(e)
                    task.save()
                return redirect('apply-policy')
            elif action == "stop" or action == "cancel" :
                try:
                    scheduler.stop_job(task)
                except Exception as e:
                    print(e)
                    task.status = "error"
                    task.error = str(e)
                    task.save()
                return redirect('apply-policy')
            elif action == "pause":
                try:
                    scheduler.pause_job(task)
                except Exception as e:
                    print(e)
                    task.status = "error"
                    task.error = str(e)
                    task.save()
                return redirect('apply-policy')

            elif action == "resume":
                try:
                    scheduler.resume_job(task)
                except Exception as e:
                    print(e)
                    task.status = "error"
                    task.error = str(e)
                    task.save()
                return redirect('apply-policy')
            else:
                task= models.Task.objects.get(pk=task_pk)

        connectors = models.Connector.objects.filter(created_by=request.user).order_by('-date_created').values("name","description","pk")
        transformers = models.Transformer.objects.filter(Q(is_public="True") | Q(created_by=request.user) ).order_by('-last_modified')

        dict={"segment":"apply-policy",'task':task,"connectors":connectors,"transformers":transformers}
        return render(request,'home/new_task.html',context=dict)     

@login_required(login_url='login')
def billing_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policies = CMODEL.LeaveRecord.objects.all().filter(customer=customer)
    cards = CMODEL.Card.objects.all().filter(customer=customer)
    gross = customer.rate * customer.hrs
    net = gross * 0.9
    try:
        newest_card = CMODEL.Card.objects.filter(customer=customer).latest('creation_time')
    except:
        newest_card = None
    return render(request,'home/billing.html',{'segment':"billing",'policies':policies,'newest_card':newest_card,'cards':cards,'customer':customer,'gross':gross,'net':net})

@login_required(login_url='login')
def apply_policy_view(request): 
    # customer = models.Customer.objects.get(user_id=request.user.id)
    query = request.GET.get('q',"") 
    tasks = models.Task.objects.filter(created_by=request.user).order_by('-date_created')
    if query:
        tasks = tasks.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )  

    paginator = Paginator(tasks, 10) # Display 10 tasks per page
    page = request.GET.get('page')
    tasks = paginator.get_page(page)

    return render(request,'home/task_list.html',{'tasks':tasks,'segment' : "apply-policy","q":query})

@login_required(login_url='login')
def connector_history_view(request): 

    # customer = models.Customer.objects.get(user_id=request.user.id)
    query = request.GET.get('q',"") 
    connectors = models.Connector.objects.filter(created_by=request.user).order_by('-date_created')
    if query:
        connectors = connectors.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )  

    paginator = Paginator(connectors, 10) # Display 10 tasks per page
    page = request.GET.get('page')
    connectors = paginator.get_page(page)

    if request.method == 'POST': 
        print("fffffffff") 
        try:
            code_Form=forms.Connectorform(request.POST)
            if code_Form.is_valid() :
                code_save = code_Form.save(commit=False)
                code_save.created_by = request.user
                code_save.save() 

        except Exception as e:

            print("e",e)

            return  render(request,'home/connector.html',{'connectors':connectors,
                                                    'segment' : "connectors",
                                                    "error":e})

        return render(request,'home/task.html',{'connector':code_save,
                                                    'segment' : "connectors","pk":code_save.pk,
                                                    })

    return render(request,'home/connector.html',{'connectors':connectors,
                                                    'segment' : "connectors","q":query })

def apply_view(request,pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policy = CMODEL.Vocation.objects.get(id=pk)
    policyrecord = CMODEL.LeaveRecord()
    policyrecord.Policy = policy
    policyrecord.customer = customer
    policyrecord.save()
    email = EmailMessage(
        'Demande de congé en cours de traitement',
        "Votre demande de congé de numéro {}{} créée le {} a été envoyée avec succès et est en cours de traitement.".format(request.user.id,policyrecord.id,policyrecord.creation_date),
        'proxymartstore@gmail.com',
        ["driverprodigy@gmail.com",customer.email],
    )
    email.send()
    return redirect('history')

def history_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policies = CMODEL.LeaveRecord.objects.all().filter(customer=customer)
    return render(request,'customer/history.html',{'policies':policies,'customer':customer})


def delete_contract_view(request,pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policy_record = CMODEL.LeaveRecord.objects.get(customer=customer, id=pk)
    policy_record.delete()
    return redirect('contracts')

def delete_card_view(request,pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    card = CMODEL.Card.objects.get(customer=customer,id=pk)
    card.delete()
    return redirect('billing')

def delete_car_view(request,pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    car = CMODEL.Car.objects.get(owner=customer,id=pk)
    car.delete()
    return redirect('contracts')

@login_required(login_url='login')
def history_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    vocations = CMODEL.LeaveRecord.objects.all().filter(customer=customer)
    cars = CMODEL.Car.objects.all().filter(owner=customer)
    return render(request,'home/tables.html',{'cars':cars,'vocations':vocations,'customer':customer,'segment':"contracts"})

def delete_question_view(request,pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    question = CMODEL.Question.objects.get(customer=customer,id=pk)
    question.delete()
    return redirect('question-history')



@login_required(login_url='login')
def delete_code_editor(request,pk):
    connector= models.Transformer.objects.get(pk=pk).delete()
    return redirect("question-history")



def code_editor(request,pk=None): 

    transformers = models.Transformer.objects.filter(is_public="True").order_by('-last_modified')
    transformers_type = transformers.values_list('transformer_type', flat=True).distinct()

    if request.method == 'POST':  
        try:

            try:
                saved_transformer = models.Transformer.objects.get(pk=pk,created_by=request.user)
                saved_transformer.code = request.POST.get("code")
                saved_transformer.is_public = request.POST.get("is_public")
                saved_transformer.description = request.POST.get("description")
                saved_transformer.transformer_type = request.POST.get("transformer_type")
                saved_transformer.save()
                return redirect('question-history')

            except ObjectDoesNotExist:            
                code_Form=forms.CodeForm(request.POST)
                if code_Form.is_valid() :
                    code_save = code_Form.save(commit=False)
                    code_save.created_by = request.user
                    code_save.transfomer_type = request.POST.get("transfomer_type")
                    code_save.save()
                # saved_transformer = models.Transformer.objects.create(**save_data) 
                return redirect('question-history')
        except Exception as e:
            print(e)
            form = forms.CodeForm()
            return render(request,'home/code_editor.html',{'code':request.POST.get("code"),'form':form,"update":1,
                'name':request.POST.get("name"),'description':request.POST.get("description"),"error":e,
                'transformers_type':transformers_type,

                 }) 
    else:
        form = forms.CodeForm()
        if pk:
            transformer = models.Transformer.objects.get(pk=pk)
            return render(request,'home/code_editor.html',{'code':transformer.code,'form':form,"update":1,
                'name':transformer.name,'description':transformer.description,'transformers_type':transformers_type, }) 
        return render(request,'home/code_editor.html',{'code':
            """# This Python 3 environment comes with many helpful analytics libraries installed 

    import numpy as np # linear algebra
    import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

    def main(transform_data,source_data):
        dt = source_data['Dataset Reading']
        print(dt)
        dt.pop()
        return dt

        """,'transformers_type':transformers_type,'is_public':transformer.is_public}) 



def question_history_view(request): 
    # customer = models.Customer.objects.get(user_id=request.user.id)
    query = request.GET.get('q',"")
    q_types = request.GET.get('q_types',"")
    transformers = models.Transformer.objects.filter().order_by('-last_modified')
    transformers_type = transformers.values_list('transformer_type', flat=True).distinct()
    my_work = models.Transformer.objects.filter(created_by=request.user).count()  

    if query:
        transformers = transformers.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )  

    if q_types:
        transformers.filter(transformer_type=q_types)

    paginator = Paginator(transformers, 10) # Display 10 transformers per page
    page = request.GET.get('page')
    transformers = paginator.get_page(page)

    return render(request,'home/my-questions.html',{'transformers':transformers,'transformers_type':transformers_type,
                                                    'segment' : "question-history","q":query,"my_work":my_work})


def download_attendance(request):
    e = models.Customer.objects.get(user_id=request.user.id)
    employee_dir = os.path.join(settings.MEDIA_ROOT, "employee_{}".format(request.user.id))
    os.makedirs(employee_dir,exist_ok=True)
    filename = "attendance_{}.pdf".format(request.user.id)
    font = ImageFont.truetype("arial.ttf", 35, encoding="utf-8")
    font1 = ImageFont.truetype("arial.ttf", 15, encoding="utf-8")
    canvas = Image.open('attendance.png')
    canvas=canvas.convert('RGB')
    draw = ImageDraw.Draw(canvas)
    draw.text((430, 420), str(request.user.first_name)+" "+str(request.user.last_name), 'black', font)
    draw.text((530, 580), "{}    {}      {}".format(datetime.now().day,datetime.now().month,datetime.now().year), 'black', font1)
    canvas.save(os.path.join(employee_dir,filename))
    #signature_add(os.path.join(employee_dir,filename),'signature.png',3000,750,0.6,0.9)
    filepath = settings.BASE_DIR + '\\static\\' + "employee_{}\\".format(request.user.id) + filename
    fl = open(filepath, 'rb')
    mime_type, _ = mimetypes.guess_type(filename)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    email = EmailMessage(
    'Certificat de présence',
    "Veuillez trouver ci-joint votre certificat de présence, attribuée suite à votre demande.",
    'proxymartstore@gmail.com',
    ["driverprodigy@gmail.com",e.email],
)
    email.attach_file(os.path.join(employee_dir,filename))
    email.send()
    return response

def download_payslip(request):
    e = models.Customer.objects.get(user_id=request.user.id)
    employee_dir = os.path.join(settings.MEDIA_ROOT, "employee_{}".format(request.user.id))
    os.makedirs(employee_dir,exist_ok=True)
    filename = "payslip_{}_{}_{}.pdf".format(request.user.id,datetime.now().month,datetime.now().year)
    font2 = ImageFont.truetype("arial.ttf", 15, encoding="utf-8")
    font = ImageFont.truetype("arial.ttf", 20, encoding="utf-8")
    canvas = Image.open('payslip.png')
    canvas=canvas.convert('RGB')
    draw = ImageDraw.Draw(canvas)
    draw.text((550, 300), "{} H".format(e.hrs), 'black', font)
    draw.text((620, 305), "{} DT/H".format(e.rate), 'black', font2)
    draw.text((700, 305), "{} DT".format(e.hrs*e.rate), 'black', font2)
    draw.text((700, 340), "{} DT".format(e.hrs*e.rate), 'black', font2)
    draw.text((700, 370), "{} DT".format(e.hrs*e.rate*0.1), 'black', font2)
    draw.text((700, 400), "{} DT".format(e.hrs*e.rate*0.9), 'black', font2)
    draw.text((700, 430), "{} DT".format(e.hrs*e.rate*0.9*0.02), 'black', font2)
    draw.text((530, 200), "{}/{}/{}".format(datetime.now().day,datetime.now().month,datetime.now().year), 'black', font2)
    draw.text((40, 170), "{} {}".format(request.user.first_name,request.user.last_name), 'black', font2)
    draw.text((40, 200), "{}".format(e.address), 'black', font2)
    canvas.save(os.path.join(employee_dir,filename))
   # signature_add(os.path.join(employee_dir,filename),'signature.png',450,450,0.6,0.9)
    filepath = settings.BASE_DIR + '\\static\\' + "employee_{}\\".format(request.user.id) + filename
    fl = open(filepath, 'rb')
    mime_type, _ = mimetypes.guess_type(filename)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    email = EmailMessage(
    'Bulletin de paie',
    "Veuillez trouver ci-joint votre bulletin de paie pour le mois {}/{}.".format(datetime.now().month,datetime.now().year),
    'proxymartstore@gmail.com',
    ["driverprodigy@gmail.com",e.email],
)
    email.attach_file(os.path.join(employee_dir,filename))
    email.send()
    return response

def download_autorization(request,pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    leave_record = CMODEL.LeaveRecord.objects.get(customer=customer,id=pk)
    if leave_record.status != "Approved":
        return redirect('contracts')
    employee_dir = os.path.join(settings.MEDIA_ROOT, "employee_{}".format(request.user.id))
    os.makedirs(employee_dir,exist_ok=True)
    filename = "autorization_{}_{}.pdf".format(request.user.id,pk)
    font = ImageFont.truetype("arial.ttf", 35, encoding="utf-8")
    font1 = ImageFont.truetype("arial.ttf", 25, encoding="utf-8")
    canvas = Image.open('autorization.jpg')
    canvas=canvas.convert('RGB')
    draw = ImageDraw.Draw(canvas)
    draw.text((100, 410), "{} {}".format(request.user.first_name,request.user.last_name), 'black', font)
    draw.text((180, 470), "{}".format(leave_record.creation_date), 'black', font)
    draw.text((670, 570), "{}{}".format(request.user.id,pk), 'black', font)
    draw.text((335, 595), "{}".format(leave_record.creation_date), 'black', font1)
    canvas.save(os.path.join(employee_dir,filename))
  #  signature_add(os.path.join(employee_dir,filename),'signature.png',5000,600,0.6,0.9)
    filepath = settings.BASE_DIR + '\\static\\' + "employee_{}\\".format(request.user.id) + filename
    fl = open(filepath, 'rb')
    mime_type, _ = mimetypes.guess_type(filename)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


def movie_recommendation_view(request):
    if request.method == "GET":
      # The context/data to be presented in the HTML template
      context = generate_movies_context()
      # Render a HTML page with specified template and context
      return render(request, 'customer/movie_list.html', context)

def generate_movies_context():
    context = {}
    # Show only movies in recommendation list
    # Sorted by vote_average in desc
    # Get recommended movie counts
    recommended_count = Course.objects.filter(
        recommended=True
    ).count()
    # If there are no recommended movies
    if recommended_count == 0:
        # Just return the top voted and unwatched movies as popular ones
        courses = Course.objects.filter(
            watched=False
        ).order_by('-vote_count')[:30]
    else:
        # Get the top voted, unwatched, and recommended movies
        courses = Course.objects.filter(
            watched=False
        ).filter(
            recommended=True
        ).order_by('-vote_count')[:30]
    context['movie_list'] = courses

    return context



 


def process_payment(request):
    # Retrieve form data
    amount = "20"
    card_cvv = request.POST.get('card_cvv')
    card_expiry_date = request.POST.get('card_expiry_date')
    card_expiry_month = request.POST.get('card_expiry_month')

    # Create payment payload
    payload = {
        'merchantId': settings.REMITA_MERCHANT_ID,
        'serviceTypeId': '123456789',
        'amount': amount,
        'cardCVV': card_cvv,
        'cardExpiryDate': card_expiry_date,
        'cardExpiryMonth': card_expiry_month,
        # Add other required parameters
    }

    # Make API request to Remita
    response = requests.post(
        f"{settings.REMITA_API_BASE_URL}/remita/exapp/api/v1/send/api/echannelsvc/echannel/initialize",
        json=payload,
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {settings.REMITA_API_KEY}"}
    )

    # Process the response and redirect the user to the payment page
    if response.status_code == 200:
        payment_data = response.json()
        redirect_url = payment_data['paymentAuthUrl']
        return redirect(redirect_url)
    else:
        # Handle error case
        return render(request, 'home/paymenterror.html')

