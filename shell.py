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
import cv2


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


def processing():
    import os
    import shutil
    import glob
    import xml.etree.ElementTree as et

    valid_image_ext = ['jpg','tif','jpeg','TIF','JPG','JPEG','PNG','png']
    cwd = os.getcwd()
    os.chdir("/home/riya/Telugu")
    book_path_folder = os.getcwd()
    book_name_lan = os.getcwd().split("/")[-1]

    book_list = Book.objects.all()
    test_list=[]
    for i in book_list:
        test_list.append(i.title)
    print(test_list)
    count = 1

    book_path_list = glob.glob('*/*/*')
    book_path_list = [i for i in book_path_list if os.path.isdir(i)]
    print(book_path_list)
    # cwd = os.getcwd()
    test=[]

    for book_path in book_path_list:
        print(book_path)
        os.chdir(book_path_folder+"/"+book_path)
        print(os.getcwd())
        images = []
        for i in valid_image_ext:
            images += glob.glob('Images/*.{}'.format(i))
        images = list(set(images))
        print(images)
        content = glob.glob('Predictions_CRNN/*.txt')
        print(content)
        print(len(content))
        print(len(images))
        assert len(content) == len(images)
        if len(content[0].split('_')) > 2:
            content = ['_'.join(i.split('_')[1:]) for i in content]
            print(content)
        root = et.parse('./META.XML').getroot()
        print(root)
        meta = {i.tag:i.text for i in root}

        meta["title"] = meta["title"].lower()
        meta["title"] = meta["title"].title()

        if str(meta["title"]) in test_list :
            print("Already Present")
        else:
            if "creator" not in meta.keys():
                meta["creator"] = None
            if meta["title"] is None:
                meta["title"] = "NDLI_"+book_name_lan+str(count)
            if meta["creator1"]:
                meta["creator"] = meta["creator1"]
            if meta["creator"] is None:
                meta["creator"] = "Anonymous"
            if meta["digitalrepublisher"] is None:
                meta["digitalrepublisher"] = meta["source"]
            if meta["subject"] is None or meta["subject"]=="<>":
                meta["subject"] = "Unavailable"
            if meta["subject"]=="Religion":
                meta["subject"] = "Religion and Theology"
            if meta["subject"]=="Literature" or meta["subject"]=="Language" or meta["subject"]=="Drama":
                meta["subject"] = "Language. Linguistics. Literature"
            if meta["digitalrepublisher"] == "Udl .T.T.D, Tirupati" or meta["digitalrepublisher"] == "Udl T.T.D. Tirupati":
                meta["digitalrepublisher"] = "Udl ttd Tirupathi"
            if meta["digitalrepublisher"] =="Digital Library Of India":
                meta["digitalrepublisher"] = "Digital Library Of India"
            if meta["digitalrepublisher"] == "Sci-Hyd" or meta["digitalrepublisher"] == "AOU " or meta["digitalrepublisher"] == "OU " or meta["digitalrepublisher"] == "TMS " or meta["digitalrepublisher"] == "SVDL " or meta["digitalrepublisher"] == "CPL " or meta["digitalrepublisher"] == "Others ":
                meta["digitalrepublisher"] = "Others"
            if meta["barcode"] is None:
                meta["barcode"] = "Unavailable"


            b = Book(
                isbn= meta['barcode'],
                title=meta['title'].lower().rstrip().title(),
                author=meta['creator'].lower().rstrip().title(),
                language=meta['language'].lower().rstrip().title(),
                genre=meta['subject'].lower().rstrip().title(),
                source=meta['digitalrepublisher'].lower().rstrip().title(),
            )
            shutil.make_archive('Images','zip','.',base_dir='Images')
            shutil.make_archive('Predictions_CRNN','zip','.',base_dir='Predictions_CRNN')
            image_zip = os.path.abspath('Images.zip')
            content_zip= os.path.abspath('Predictions_CRNN.zip')
            os.chdir(cwd)
            b.book_pdf.save('Images.zip',File(open(image_zip,'rb')), save=False)
            b.book_content.save('Predictions_CRNN.zip', File(open(content_zip,'rb')),save=False)
            # b.book_pdf = File(open(image_zip,'rb'))
            # b.book_content = File(open(content_zip,'r'))
            b.save()
            print(meta)
            print(os.getcwd())
            
