from django.urls import reverse
from django.test.utils import setup_test_environment
from django.contrib.auth.models import User
from django.db.models import Q

from home.models import *
from home.search import *
# from searchengine.forms import *
# import requests
import os
import sys
import random


# from tabulate import tabulate
setup_test_environment()
from django.test import Client



c = Client()
from django.core.files import File
def populate_user_database():
    os.chdir('./static/books')
    id_=int(input('Enter ID: '))
    b=Book.objects.get(id=id_)
    os.chdir(b.title)
    os.chdir('content')
    ids=[]
    for file in os.listdir('.'):
        print(file)
        with open(file,'r') as f:
            r=f.readlines()
        r=[i.strip() for i in r]
        content='\n'.join(r)

        p=Page(pagetitle=file.strip(), content=content, book=b)
        p.save()
        ids.append(p.id)
    os.chdir('../images')
    for i in ids:
        pt='.'.join(Page.objects.get(id=i).pagetitle.split('.')[:-1])
        # pt=pt.split('.')[:-1]+'jpg'
        p=Page.objects.get(id=i)
        p.image.save(pt,File(open(pt,'rb')))




def flush_user_database():
    p = Page.objects.all()
    if len(p):
        for i in p:
            i.delete()
    b = Book.objects.all()
    if len(b):
        for i in b:
            i.delete()
