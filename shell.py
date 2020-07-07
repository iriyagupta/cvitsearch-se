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
    os.chdir("/home/ndlsearch19/rename_telugu/Telugu")
    book_path_folder = os.getcwd()
    book_name_lan = os.getcwd().split("/")[-1]
    
    #print(book_path_folder)
    book_list = Book.objects.all()
    test_list=[]
    for i in book_list:
        test_list.append(i.title)
    # print(test_list)
    count = 1

    book_path_list = glob.glob('*')
    book_path_list = [i for i in book_path_list if os.path.isdir(i)]
    print(book_path_list)
    # cwd = os.getcwd()
    test=[]

    for book_path in book_path_list:
        print(book_path)
        print("/n/n")

        test_list_content = []
        test_list_images = []
        test_list_segment = []

        nameofthebook = book_path.split("/")[-1]
        #print(nameofthebook)
        os.chdir(book_path_folder+"/"+book_path)
        print(os.getcwd())
        images = []
        for i in valid_image_ext:
            images += glob.glob('Images/*.{}'.format(i))
        images = list(set(images))
        # print(images)
        content = glob.glob('Predictions_CRNN/*.txt')
        # print(content)
        #print(len(content))
        #print(len(images))

        segment = glob.glob('Segmentations/*.txt') 
        for i in images:
            i=i.split(".")[0].split("/")[-1]
            test_list_images.append(i)

        if len(content)!=0 and len(content) is not None: 
            for i in content:
                i = i.split(".")[0].split("/")[-1]
                test_list_content.append(i)
        else:
            print("No predictions")

        for i in segment:
            i = i.split(".")[0].split("/")[-1]
            test_list_segment.append(i)
        
        
        
        common_list = list(set(test_list_content) & (set(test_list_images)))
                # common_list_2 = list(set(test_list_content) & (set(test_list_segment)))
        
        print("common list")
        print(len(common_list))

        dir_name_img = os.getcwd() + "/" + "Images"
        dir_name_cont = os.getcwd() + "/" + "Predictions_CRNN"
        dir_name_seg = os.getcwd() + "/" + "Segmentations"
        
        for i in test_list_images:
            if i not in common_list:
                test_list_images.remove(i)

        for i in test_list_content:
            if i not in common_list:
                test_list_content.remove(i)


        for i in test_list_segment:
            if i not in common_list:
                test_list_segment.remove(i)
                                            
        test1=[]
        test2=[]
        test3=[]


        for i in test_list_images:
            i = i + "." + "png" 
            test1.append(i)

        for i in test_list_content:
            i = i + "." + "png.txt"
            test2.append(i)


        for i in test_list_segment:
            i = i + "." + "png.lines.txt"
            test3.append(i)

        for i in images : 
            if i.split("/")[-1] not in test1:
                images.remove(i)
                os.remove(os.path.join(dir_name_img,i.split("/")[-1]))

        for i in content : 
            if i.split("/")[-1] not in test2:
                content.remove(i)
                os.remove(os.path.join(dir_name_cont, i.split("/")[-1]))

        for i in segment: 
            if i.split("/")[-1] not in test3:
                segment.remove(i)
                os.remove(os.path.join(dir_name_seg, i.split("/")[-1]))


        print(len(images))
        print(len(content))
        print(len(segment))


        print(count)
        count+=1
        assert len(content) == len(images)
        #print(len(content[0].split('_')))
        if len(content[0].split('_')) > 2:
            content = ['_'.join(i.split('_')[1:]) for i in content]
            #print(content)
        root = et.parse('./META.XML').getroot()
        print(root)
        meta = {i.tag:i.text for i in root}
        
        if "title" not in meta.keys():
            meta["title"] = None
        
        if "totalpages" not in meta.keys():
            meta["totalpages"] = None

        if meta["title"] is None:
            meta["title"] = "NDLI_"+book_name_lan+str(count)
            count+=1
        #print(count)
        meta["title"] = meta["title"].lower()
        meta["title"] = meta["title"].title()

        if str(meta["title"]) in test_list :
            print("Already Present")
        else:
            if "creator" not in meta.keys():
                meta["creator"] = None
           
            if "digitalrepublisher" not in meta.keys():
                meta["digitalrepublisher"]= None

            if 'creator1' not in meta.keys() or meta["creator1"] is None:
                meta["creator1"] = "Anonymous"
            if meta["creator"] is None:
                meta["creator"]= meta["creator1"]
                
            if meta["digitalrepublisher"] is None:
                meta["digitalrepublisher"] = "Digital Library Of India"
            
            if "subject" not in meta.keys():
                meta["subject"] = "Unavailable"
            
            if meta["digitalrepublisher"] == "PAR Informatics, Hyderabad" or meta["digitalrepublisher"]=="UDL T.T.D, TIRUPATHI"  or meta["digitalrepublisher"]=="UDL TTD TIRUPATHI" or meta["digitalrepublisher"]=="PAR INFORMATICS,HYDERBAD" or meta["digitalrepublisher"]=="UDL T.T.D.Tirupati" or meta["digitalrepublisher"]=="UDL , T.T.D. TIRUPATI" or meta["digitalrepublisher"]=="UDL TTD TIRUPATI" or meta["digitalrepublisher"]=="PAR INFORMATICS,HYD" or meta["digitalrepublisher"]=="<>" or meta['digitalrepublisher']=="Sarvesh Mishra" or meta["digitalrepublisher"]=="UDL TTD TIRUPATI" or meta["digitalrepublisher"]=="Udl Ttd Tirupathi":
                meta["digitalrepublisher"] = "Others"


            if meta["subject"] is None or meta["subject"]=="<>" or meta['subject'] == "&lt;&gt;" or meta["subject"]=="-" or meta["subject"]=="&lt;enter subject of the book&gt;" or meta["subject"]=="<enter subject of the book>":
                meta["subject"] = "Unavailable"

            if meta["subject"]=="RELIGION" or meta['subject']=="Religion" or meta['subject']=="HINDUISM " or meta["subject"]=="hinduism" or meta["subject"]=="HINDUISM" or meta["subject"]=="RELIGION. THEOLOGY" or meta["subject"]=="Religion. Theology":
                meta["subject"] = "Religion and Theology"

            if meta["subject"]=="Literature" or meta["subject"]=="Litrature" or meta["subject"]=="Nobel" or meta["subject"]=="Novel" or meta["subject"] == "Hindi literature" or meta["subject"]=="Hindi Literature" or meta["subject"]=="LITERATURE" or meta["subject"]=="Hindi Literature" or meta["subject"]=="Literature " or meta["subject"]=="Language" or meta["subject"]=="Drama" or meta["subject"]=='drama'  or meta["subject"]=="Hindi drama" or meta["subject"]=="Hindi Drama" or meta["subject"]=="poetry" or meta["subject"]=="lictraturl" or meta["subject"]=="Story" or meta["subject"]=="literature" or meta['subject']=="poetry" or meta["subject"]=="Hindi poetry" or meta["subject"]=="Poetry":
                meta["subject"] = "Language. Linguistics. Literature"

            if meta["subject"]=="Others " or meta["subject"]=="OTHERS":
                meta["subject"]="Digital Library Of India"

            if meta["barcode"] is None:
                meta["barcode"] = "Unavailable"
            
            if meta["totalpages"] is None:
                meta["totalpages"] = "-"

            b = Book(
                isbn= meta['barcode'],
                title=meta['title'].lower().rstrip().title(),
                author=meta['creator'].lower().rstrip().title(),
                language=meta['language'].lower().rstrip().title(),
                genre=meta['subject'].lower().rstrip().title(),
                source=meta['digitalrepublisher'].lower().rstrip().title(),
                numpages = meta["totalpages"]
            )

            shutil.make_archive('Images','zip','.',base_dir='Images')
            shutil.make_archive('Predictions_CRNN','zip','.',base_dir='Predictions_CRNN')
            shutil.make_archive('Segmentations','zip','.',base_dir='Segmentations')

            image_zip = os.path.abspath('Images.zip')
            content_zip= os.path.abspath('Predictions_CRNN.zip')
            segment_zip= os.path.abspath('Segmentations.zip')

            os.chdir(cwd)

            b.book_pdf.save('Images.zip',File(open(image_zip,'rb')), save=False)
            b.book_content.save('Predictions_CRNN.zip', File(open(content_zip,'rb')),save=False)
            b.book_segment.save('Segmentations.zip', File(open(segment_zip,'rb')),save=False)


            os.remove(image_zip)
            os.remove(content_zip)
            os.remove(segment_zip)


            b.save()
            print(meta)
            print(os.getcwd())
            
