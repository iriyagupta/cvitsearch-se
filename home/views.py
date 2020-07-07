import os
import subprocess
import tempfile
import json
from django.utils import timezone
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render
from django.db.models import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth.models import User
from django.contrib.postgres.aggregates.general import StringAgg
import time
import re
import shutil
import os,cv2,sys,codecs
import numpy as np

from .search import BookIndex, PageIndex
from .models import Page, Book , Announcement
import random
import string


def index(request):
    page_title = 'Home'
    context ={}
    a = Page.objects.count()
    context["total"] = a
    book_type = Book.objects.values_list("id",flat=True).order_by("id") 
    ids = [x for x in book_type]
    test = Book.objects.values('genre').annotate(Count('genre')) 
    #print(test)

    #genre source 
    count_genre=[]
    count=[]
    genre_param = request.GET.get('genre_param')
    if genre_param:
        context["results"] = Book.objects.filter(genre=genre_param)
    num = Book.objects.values('genre').order_by().annotate(Count('genre'))
    for i in num:
        count_genre.append(i["genre"])
        count.append(i["genre__count"])
    zipped = zip(count_genre,count)
    context["zipped"]=zipped

    count_source=[]
    counter=[]
    source_param = request.GET.get('source_param')
    if source_param:
        context["results"] = context["results"].filter(source=source_param)
    num1 = Book.objects.values('source').order_by().annotate(Count('source'))
    print(num1)
    for i in num1:
        count_source.append(i["source"])
        counter.append(i["source__count"])
    zipped_list = zip(count_source,counter)
    context["zipped_list"]=zipped_list
    
    
    
    
    context["announcements"] = Announcement.objects.all() 
    return render(request, 'home/index.jinja2', context)


def contact(request):
    page_title = 'Contact Us'
    return render(request, 'home/contact.jinja2',locals())


def stats(request):
    
    page_title = 'General Statics'
    uploaded = Book.objects.all().count()
    language_split={}
    for each in Book.objects.all():
        each = each.language
        language_split[each] = Book.objects.filter(language=each).values('language').order_by('language').annotate(count=Count('id'))
    
    
    return render(request, 'home/stats.jinja2',locals())






def list1(request):
    context={}
    page_title = 'British Library'
    a = Book.objects.filter(source="British Library")
    ids = [i.id for i in a]
    dataset1 = Book.objects.filter(id__in=ids)
    context['language_list'] = list(set([i.language for i in Book.objects.filter(id__in=ids)]))

    lang = request.GET.get('lang', None)

    if lang:
        dataset1 = dataset1.filter(language=lang).distinct()

    npages = request.GET.get('npages')

    if npages:
        if npages == '1':
            dataset1=[i for i in dataset1 if len(i.numpages)<3]
        elif npages == '2':
            dataset1=[i for i in dataset1 if len(i.numpages)<4]

    context['dataset1']=dataset1

    pages_for_pagination = []

    list_dataset1 = dataset1

    for content in list_dataset1:
        pages_for_pagination.append(content)

    paginator = Paginator(pages_for_pagination, 20)
    page = request.GET.get('page',1)
    try:
        pages_for_pagination = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pages_for_pagination = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pages_for_pagination = paginator.page(paginator.num_pages)

    context['dataset1']=pages_for_pagination

    return render(request, 'home/list1.jinja2', context , locals())



def list2(request):
    context={}
    page_title = 'Digital Library Of India'
    a = Book.objects.filter(source="Digital Library Of India")
    ids = [i.id for i in a]
    dataset2 = Book.objects.filter(id__in=ids).order_by("language","title")
    context['language_list'] = list(set([i.language for i in Book.objects.filter(id__in=ids)]))

    lang = request.GET.get('lang', None)

    if lang:
        dataset2 = dataset2.filter(language=lang).distinct()

    npages = request.GET.get('npages')
    print(npages)

    if npages:
        if npages == '1':
            dataset2=[i for i in dataset2 if len(i.numpages)<3]
        elif npages == '2':
            dataset2=[i for i in dataset2 if len(i.numpages)<4]

    context['dataset2']=dataset2
    print(context['dataset2'])

    pages_for_pagination = []

    list_dataset2 = dataset2

    for content in list_dataset2:
        pages_for_pagination.append(content)

    paginator = Paginator(pages_for_pagination, 25)
    page = request.GET.get('page',1)
    try:
        pages_for_pagination = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pages_for_pagination = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pages_for_pagination = paginator.page(paginator.num_pages)

    context['dataset2']=pages_for_pagination
    print(context['dataset2'])

    return render(request, 'home/list2.jinja2', context , locals())



"""IIITH dataset list"""
def list3(request):
    context={}
    page_title = 'IIITH Library'
    a = Book.objects.filter(source="IIITH Library")
    ids = [i.id for i in a]

    dataset3 = Book.objects.filter(id__in=ids).order_by("language","title")
    # print(dataset2)
    context['language_list'] = list(set([i.language for i in Book.objects.filter(id__in=ids)]))
    lang = request.GET.get('lang', None)

    if lang:
        dataset3 = dataset3.filter(language=lang).distinct()

    npages = request.GET.get('npages')

    if npages:
        if npages == '1':
            dataset3=[i for i in dataset3 if len(i.numpages)<3]
        elif npages == '2':
            dataset3=[i for i in dataset3 if len(i.numpages) < 4]

    context['dataset3']=dataset3
    pages_for_pagination = []
    list_dataset3 = dataset3

    for content in list_dataset3:
        pages_for_pagination.append(content)

    paginator = Paginator(pages_for_pagination,7)
    print(pages_for_pagination)
    page = request.GET.get('page',1)
    try:
        pages_for_pagination = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pages_for_pagination = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pages_for_pagination = paginator.page(paginator.num_pages)

    context['dataset3']=pages_for_pagination

    return render(request, 'home/list3.jinja2', context)


def books(request):
    print(request.POST)
    res_dictionary={}
    image_list = []
    context = {}

    if request.POST:
        context={}
        id_ = int(request.POST["fname"])
        # print(id)
        test = Book.objects.get(id=request.POST["fname"]).pages.all().values_list('image', flat=True).order_by("pagetitle") 
        # print(test)
        title = Book.objects.get(id=request.POST["fname"]).title
        isbn = Book.objects.get(id=request.POST["fname"]).isbn
        author = Book.objects.get(id=request.POST["fname"]).author
        pages = Book.objects.get(id=request.POST["fname"]).numpages
        genre = Book.objects.get(id=request.POST["fname"]).genre
        for i in test : 
            i = "/media/" + i
            image_list.append(i)
        res_dictionary["id_"] = id_
        res_dictionary["imglist"] = image_list
        # pdb.set_trace()
        # print(res_dictionary)
        res_dictionary["title"] = title
        res_dictionary["author"] = author
        res_dictionary["isbn"] = isbn
        res_dictionary["pages"] = pages
        res_dictionary["genre"] = genre


        return render(request, 'home/books.jinja2', res_dictionary)




#def search(request):
 #   page_title = 'Searched Results'
    #context = {}
    #q = request.GET.get('q',None)
    #print(q)
    # lan = request.GET.get('language',None)
    # print(lan)
    #para = request.GET.get('parameter',None)
    # para = request.GET.get('value',None)
    #print(para)
    
#
#    tic = time.clock()
    # if q is None:
    #     return redirect('home')
 #   if para == 'author':     a = BookIndex.search().query('match_phrase',author=q)
        #ids = [i.id for i in a]
        #context['results'] = Book.objects.filter(id__in=ids)
        #context["total"]= Book.objects.filter(id__in=ids).count()
   # elif para == 'isbn':
    #    a = BookIndex.search().query('match_phrase',isbn=q)
     #   ids = [i.id for i in a]
      #  context['results'] = Book.objects.filter(id__in=ids)
       # context["total"]= Book.objects.count()
    #elif para == 'title':
     #   a = BookIndex.search().query('match_phrase',title=q)
      #  ids = [i.id for i in a]
       # context['results'] = Book.objects.filter(id__in=ids)
        #context["total"]= Book.objects.count()
   # else:
    #    a=PageIndex.search().query('match_phrase',content=q)
     #   ids=[i.id for i in a]
      #  context['results'] = Book.objects.filter(pages__id__in=ids).distinct()
   #     context["total"]= Book.objects.filter(pages__id__in=ids).count()


    #toc = time.clock()

    #book_type = Book.objects.values_list("id",flat=True).order_by("id") 
    #ids = [x for x in book_type]

    #time_diff = toc - tic


    #count_genre=[]
    #count=[]

    #total = Book.objects.values('genre').order_by().annotate(Count('genre'))
    #print(total)
    #for i in total:
     #   count_genre.append(i["genre"])
      #  count.append(i["genre__count"])

   # print(count,count_genre)

    #zipped = zip(count_genre,count)
    #context["zipped"]=zipped

    #count_source=[]
    #counter=[]

    #total = Book.objects.values('source').order_by().annotate(Count('source'))
   # print(total)
    #for i in total:
     #   count_source.append(i["source"])
      #  counter.append(i["source__count"])

   # print(counter,count_source)

    #zipped_list = zip(count_source,counter)
   # context["zipped_list"]=zipped_list
    #context['q'] = q
   # context["time_diff"] = str(time_diff)

    
    #return render(request, 'home/search.jinja2', context )


"""Searched Results"""
def search(request):
    page_title = 'Searched Results'
    context = {}
    q = request.GET.get('q',None)

    para = request.GET.get('parameter',None)
    lan = request.GET.get('language',None)
    #check for the beginning of time of calculation of query retrieval
    tic = time.clock()

    #genre list on home page
    index_genre = request.GET.get('index_genre')
    index_source = request.GET.get('index_source')
    #check whether the query exists or not for particular params

    if q:
        if para == 'author':
            a = BookIndex.search().query('match_phrase',author=q)
            ids = [i.id for i in a]
            context['results'] = Book.objects.filter(id__in=ids)
            total = context["results"].count() #get the total count
        elif para == 'isbn':
            a = BookIndex.search().query('match_phrase',isbn=q)
            ids = [i.id for i in a]
            context['results'] = Book.objects.filter(id__in=ids)
            total = context["results"].count()
        elif para == 'all':
            a = BookIndex.search().query('match_phrase',title=q)
            b = BookIndex.search().query('match_phrase',isbn=q)
            c = BookIndex.search().query('match_phrase',author=q)
            d = PageIndex.search().query('match_phrase',content=q)
            id1 = [i.id for i in a]
            id2 = [i.id for i in b]
            id3 = [i.id for i in c]
            id4 = [i.id for i in d]
            #print(id1,id2,id3,id4)
            book_list_common=[]
            for i in id4:
                book_list = Page.objects.get(pk=i)
                b = book_list.book_id
                book_list_common.append(b)
            #print(book_list_common)

            final = list(set().union(id1, id2, id3,book_list_common)) 
            context['results'] = Book.objects.filter(id__in=final)
            total = context["results"].count()

            page_index=PageIndex.search().query('match_phrase',content=q)
            page_ids=[i.id for i in page_index]
            pages=[]
            page_lines = {i:[] for i in page_ids}
            page_lines2 = {i:[] for i in page_ids}
            book_ids=[]

            for i in page_ids:
                pages.append(i)
                # print(pages.count(q))
                line_list = Page.objects.get(id=i).content.split('.')
                counter_exact =[]
                count=0
                for line in line_list:
                    l=line.lower()
                    cap = False
                    if q.lower() in l:
                        l=l.replace(q,'<b class="text-success">{}</b>'.format(q.upper()))
                        print(l)
                        count+=1
                        cap=True
                    if cap:
                        page_lines[i].append(l)
                #print(count)
            context['page_list'] = Page.objects.filter(id__in=page_ids)
            # print(context["page_list"])
            context['page_lines'] = page_lines
        elif para=="content":

            #print(q)

            if " " in q:
                q = q.strip()
                #print(q)

            if q.startswith('"') and q.endswith('"'):
                q = q.replace('"','')

                a = Page.objects.filter(content__contains=q)
                page_ids=[i.id for i in a]
                page_list = Page.objects.filter(id__in=page_ids)

                pages=[]
                page_lines = {i:[] for i in page_ids}
                page_lines2 = {i:[] for i in page_ids}
                book_ids=[]
# 
                context['results'] = Book.objects.filter(pages__id__in=page_ids).distinct()
                total = context["results"].count()
                context['page_list'] = page_list

                for i in page_ids:
                    new_line_list = Page.objects.get(id=i).content.split('\n')
                    index_list =[]
                    # print(new_line_list)
                    for line in new_line_list:
                        cap= False
                        count=1
                        # print(line)
                        if q in line:
                            index_list.append(new_line_list.index(line))
                            l=line.replace(q,'<b class="text-success">{}</b>'.format(q))
                            cap=True
                        if cap:
                            page_lines[i].append(l)

                context['page_lines'] = page_lines

                # q = request.GET.get('q',None)
                # print(q)
                if " " in request.GET.get('q',None):
                    q = request.GET.get('q',None).strip()
                else:
                    q = request.GET.get('q',None)

              # = request.GET.get('q',None)
            else:
                print("words without quotes")
                words = q.split(" ")
                if lan == "sel":
                    operators = list(set())

                elif lan == "te":
                    operators=list(set(('వీరి', 'లను', 'కొందరు', 'అను', 'ఆమె', 'ఇవీ', 'అసలు', 'అప్పుడు', 'ఉన్నత', 'ఇప్పుడు', 'లాంటి',
                                        'వీరు', 'వీటిని', 'క్రింది', 'వారిని', 'ఇక్కడి', 'పైగా', 'అలాగే', 'దానిని', 'వచ్చే', 'కాక', 'భాగం', 'గాని',
                                        'అప్పటి', 'కనుక', 'దానికి', 'అలా', 'ఉంటే', 'కలవు', 'కేవలం', 'ఎంతో', 'ఎలా',
                                        'ఈయన', 'ఉండి', 'అనేది', 'సుమారు', 'మొదలైన', 'మన', 'అక్కడ',
                                        'నా', 'అత్యంత', 'కొంత', 'కలదు', 'లేని','.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}')))
                elif lan == "ta":
                    operators= list(set(('ஒரு', 'என்று', 'செய்து', 'இந்த', 'மேலும்', 'மற்றும்', 'இருந்தது', 'என்ற', 'வரும்', 'வேண்டும்', 'போது',
                                         'இது', 'அவர்', 'வந்து', 'அந்த', 'முதல்', 'அல்லது', 'தான்', 'என', 'ஆனால்', 'வரை', 'நான்', 'கடந்த',
                                        'கொண்டு', 'இன்று', 'பல', 'அவர்கள்', 'உள்ள', 'என்ன', 'என்பது', 'அவன்', 'அது', 'இருக்கும்', 'தன்', 'சில',
                                        'ஆண்டு', 'இருந்து', 'மூலம்', 'இல்லை', 'அதன்', 'உள்ளது', 'என்', 'இன்', 'அங்கு', 'இங்கே', 'எப்படி', 'எப்பொழுது','.',
                                         ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}')))

               
                elif lan=="hi":
                    operators = list(set(('अंदर', 'अत', 'अदि', 'अप', 'अपना', 'अपनि', 'अपनी', 'अपने', 'अभि', 'अभी', 'आदि', 'आप', 'इंहिं', 'इंहें', 'इंहों', 'इतयादि', 'इत्यादि',
                                         'इन', 'इनका', 'इन्हीं', 'इन्हें', 'इन्हों', 'इस', 'इसका', 'इसकि', 'इसकी', 'इसके', 'इसमें', 'इसि', 'इसी', 'इसे', 'उंहिं', 'उंहें', 'उंहों', 'उन', 
                                         'उनका', 'उनकि', 'उनकी', 'उनके', 'उनको', 'उन्हीं', 'उन्हें', 'उन्हों', 'उस', 'उसके', 'उसि', 'उसी', 'उसे', 'एक', 'एवं', 'एस', 'एसे', 'ऐसे', 
                                         'ओर', 'और', 'कइ', 'कई', 'कर', 'करता', 'करते', 'करना', 'करने', 'करें', 'कहते', 'कहा', 'का', 'काफि', 'काफ़ी', 'कि', 'किंहें', 'किंहों', 
                                         'कितना', 'किन्हें', 'किन्हों', 'किया', 'किर', 'किस', 'किसि', 'किसी', 'किसे', 'की', 'कुछ', 'कुल', 'के', 'को', 'कोइ', 'कोई', 'कोन', 'कोनसा', 
                                         'कौन', 'कौनसा', 'गया', 'घर', 'जब', 'जहाँ', 'जहां', 'जा', 'जिंहें', 'जिंहों', 'जितना', 'जिधर', 'जिन', 'जिन्हें', 'जिन्हों', 'जिस', 'जिसे', 'जीधर', 
                                         'जेसा', 'जेसे', 'जैसा', 'जैसे', 'जो', 'तक', 'तब', 'तरह', 'तिंहें', 'तिंहों', 'तिन', 'तिन्हें', 'तिन्हों', 'तिस', 'तिसे', 'तो', 'था', 'थि', 'थी', 'थे', 
                                         'दबारा', 'दवारा', 'दिया', 'दुसरा', 'दुसरे', 'दूसरे', 'दो', 'द्वारा', 'न', 'नहिं', 'नहीं', 'ना', 'निचे', 'निहायत', 'नीचे', 'ने', 'पर', 'पहले', 'पुरा', 
                                         'पूरा', 'पे', 'फिर', 'बनि', 'बनी', 'बहि', 'बही', 'बहुत', 'बाद', 'बाला', 'बिलकुल', 'भि', 'भितर', 'भी', 'भीतर', 'मगर', 'मानो', 'मे', 'में', 'यदि', 
                                         'यह', 'यहाँ', 'यहां', 'यहि', 'यही', 'या', 'यिह', 'ये', 'रखें', 'रवासा', 'रहा', 'रहे', 'ऱ्वासा', 'लिए', 'लिये', 'लेकिन', 'व', 'वगेरह', 'वरग', 'वर्ग', 
                                         'वह', 'वहाँ', 'वहां', 'वहिं', 'वहीं', 'वाले', 'वुह', 'वे', 'वग़ैरह', 'संग', 'सकता', 'सकते', 'सबसे', 'सभि', 'सभी', 'साथ', 'साबुत', 'साभ', 'सारा', 
                                         'से', 'सो', 'हि', 'ही', 'हुअ', 'हुआ', 'हुइ', 'हुई', 'हुए', 'हे', 'हें', 'है', 'हैं', 'हो', 'होता', 'होति', 'होती', 'होते', 'होना', 'होने' ,'जाते',
                                         '.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}')))

                
                words=[i for i in words if i not in operators]
                
                for element in words:
                    if element=="":
                        words.remove(element)
                
                
                context["words"] = words
                l1=[]
                for word in words:
                    if word != " ":
                        a = Page.objects.filter(content__contains=word) 
                        all_ids=[i.id for i in a]
                        l1.append(all_ids)
                final =[]
                for i in l1:
                    # print(i)
                    final = list(set(i+final))
                #print(final)

                x = l1[0]
                #print(x)
                page_ids=[i for i in final]
                print("\n\n")
                # x=set.intersection(*map(set,l1))  #get the pages with all the words occuring together (not feasible in cases where the exact line is being demaded)
                context['results'] = Book.objects.filter(pages__id__in=page_ids).distinct()  # get the book outputs on the basis of the query made 
                page_lines = {i:[] for i in page_ids}
                page_lines2 = {i:[] for i in page_ids}

 
                page_list = Page.objects.filter(id__in=page_ids)

                for i in page_ids:
                    new_line_list = Page.objects.get(id=i).content.split('\n')
                    index_list =[]
                    # print(new_line_list)
                    for line in new_line_list:
                        cap= False
                        count=1
                        for word in words:
                            if word in line:
                                index_list.append(new_line_list.index(line))
                                count += 1 
                                cap=True
                                #highlighted_words.append(word)
                                l=line.replace(word,'<b class="text-success">{}</b>'.format(word))
                                # if count == 2 : 
                                #     for i in highlighted_words : 
                                #         l=line.replace(word,'<b class="text-success">{}</b>'.format(word))   

                        if cap:
                            page_lines[i].append(l)

                context['page_lines'] = page_lines
                context['page_list'] = page_list
                total = context["results"].count()

                # q = request.GET.get('q',None)
                lan = request.GET.get('language',None) 
                print(lan)
 
        else:
            a = Book.objects.filter(title__contains=q)
            ids = [i.id for i in a]
            context['results'] = Book.objects.filter(id__in=ids)
            total = context["results"].count()
    else:
        q=""
        context["results"]=None
        total=0




    if index_genre:
        q=""
        context['results'] = Book.objects.filter(genre=index_genre)
        total = context["results"].count()
    
    if index_source:
        q=""
        context['results'] = Book.objects.filter(source=index_source)
        total = context["results"].count()


    toc = time.clock()

    time_diff = toc - tic 
    time_diff = '%.10f'%time_diff #time taken by query to generate


    book_type = Book.objects.values_list("id",flat=True).order_by("id") 
    ids = [x for x in book_type]

    #filter genre count depending on the list available on that page
    z = list(set([i.genre for i in Book.objects.filter(id__in=ids)]))
    count=[]
    if context["results"]:
        for i in z:
            test = context["results"].filter(genre=i).count()
            count.append(test)
    genre_param = request.GET.get('genre_param')
    if genre_param:
        context["results"] = context["results"].filter(genre=genre_param)
        total=context["results"].count()
    zipped = zip(z,count)
    context["zipped"]=zipped

    z1 = list(set([i.source for i in Book.objects.filter(id__in=ids)]))
    counter=[]
    if context["results"]:
        for i in z1:
            test = context["results"].filter(source=i).count()
            counter.append(test)
    source_param = request.GET.get('source_param')
    if source_param:
        context["results"] = context["results"].filter(source=source_param)
        total=context["results"].count()
    zipped_list = zip(z1,counter)
    context["zipped_list"]=zipped_list

    z2 = list(set([i.language for i in Book.objects.filter(id__in=ids)]))
    #print(z2)
    counter_lang=[]
    if context["results"]:
        for i in z2:
            test = context["results"].filter(language=i).count()
            counter_lang.append(test)
    source_lang= request.GET.get('source_lang')
    if source_lang:
        context["results"] = context["results"].filter(language=source_lang)
        total=context["results"].count()
    zipped_list_lang = zip(z2,counter_lang)
    context["zipped_list_lang"]=zipped_list_lang
    context['q'] = q
    context["time_diff"] = str(time_diff) 
    context["language"]=lan
    context["parameter"]=para
    context["total"] = total
    return render(request, 'home/search.jinja2', context)

import pdb

def line_segment(request):
    print ("!!!!!!!!!!!!!\n\n\n\n")
    lan = request.GET.get('language',None)
    print(request.POST)
    
    if request.POST:
        context={}
        id = int(request.POST["record_id"])
        q = request.POST["q"]

        lan = request.POST["language"]
        print(request.POST["language"])


        if "&#34;" in request.POST["q"] :
            q = q.strip("&#34;")
            
            a = Page.objects.filter(content__contains=q)
            page_ids=[i.id for i in a]
            #print(page_ids)

            res_dictionary={}
            # pdb.set_trace()
            page_list = Page.objects.filter(id__in=page_ids)

            segmented_image_list = []
            for i in page_ids:

                # print("\n\n")
                #print(i)


                b = Page.objects.get(pk=i)
                book_id = b.book_id
                # print(book_id)
               
                if book_id == id:
                    new_line_list = Page.objects.get(id=i).content.split('\n')


                    segmentation_list = Page.objects.get(id=i).segment.split("\n")
                    segmented = []
                    for x in segmentation_list:
                        x = x.strip("\r")
                        segmented.append(x)

                    counter_exact =[]
                    count=0
                    index_list =[]
                    for line in new_line_list:
                        l=line.lower()
                        cap = False
                        if q.lower() in l:
                            # print(l)
                            index_list.append(new_line_list.index(l))
                            l=l.replace(q,'<b class="text-success">{}</b>'.format(q.upper()))
                            count+=1
                            cap=True
                            # print(l)
                        # if cap:
                        #     page_lines[i].append(l)
                    
                    
                    image_url = Page.objects.get(id=i).image.url
                    # print(image_url)


                    image = cv2.imread("/home/ndlsearch19/cvitsearch"+Page.objects.get(id=i).image.url)
                    overlay = image.copy()
                    for index_num in index_list:
                        for seg in segmented:
                            if index_num == segmented.index(seg) :
                                seg = seg.strip("\r").split("\t")
                                x1 = int(seg[0])
                                y1 = int(seg[1])
                                x2 = int(seg[2])+x1
                                y2 = int(seg[3])+y1
                                cv2.rectangle(overlay,(x1,y1),(x2,y2),(0,255,255),-1)
                                alpha = 0.5  # Transparency factor.
                                img_written =  cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
                                new_image = cv2.imwrite("/home/ndlsearch19/cvitsearch/media/tmp/exact_matches/"+str(Page.objects.get(id=i).image.url.split("/")[-1]), img_written)
                
                    res_dictionary[i] = "/media/tmp/exact_matches/"+str(Page.objects.get(id=i).image.url.split("/")[-1])

                    segmented_image_list.append("/home/ndlsearch19/cvitsearch/media/tmp/exact_matches/"+str(Page.objects.get(id=i).image.url.split("/")[-1]))

            context['page_list'] = page_list

            context["res_dictionary"] = res_dictionary
            #print(context["res_dictionary"])

        else :

            print("we are in the all query section")
            words = q.split(" ")
            # print(q)
            # print(lan)

            if lan == "sel":
                    operators = list(set())
            elif lan == "te":
                    operators=list(set(('వీరి', 'లను', 'కొందరు', 'అను', 'ఆమె', 'ఇవీ', 'అసలు', 'అప్పుడు', 'ఉన్నత', 'ఇప్పుడు', 'లాంటి',
                                        'వీరు', 'వీటిని', 'క్రింది', 'వారిని', 'ఇక్కడి', 'పైగా', 'అలాగే', 'దానిని', 'వచ్చే', 'కాక', 'భాగం', 'గాని',
                                        'అప్పటి', 'కనుక', 'దానికి', 'అలా', 'ఉంటే', 'కలవు', 'కేవలం', 'ఎంతో', 'ఎలా',
                                        'ఈయన', 'ఉండి', 'అనేది', 'సుమారు', 'మొదలైన', 'మన', 'అక్కడ',
                                        'నా', 'అత్యంత', 'కొంత', 'కలదు', 'లేని','.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}')))
            elif lan == "ta":
                operators= list(set(('ஒரு', 'என்று', 'செய்து', 'இந்த', 'மேலும்', 'மற்றும்', 'இருந்தது', 'என்ற', 'வரும்', 'வேண்டும்', 'போது',
                                         'இது', 'அவர்', 'வந்து', 'அந்த', 'முதல்', 'அல்லது', 'தான்', 'என', 'ஆனால்', 'வரை', 'நான்', 'கடந்த',
                                        'கொண்டு', 'இன்று', 'பல', 'அவர்கள்', 'உள்ள', 'என்ன', 'என்பது', 'அவன்', 'அது', 'இருக்கும்', 'தன்', 'சில',
                                        'ஆண்டு', 'இருந்து', 'மூலம்', 'இல்லை', 'அதன்', 'உள்ளது', 'என்', 'இன்', 'அங்கு', 'இங்கே', 'எப்படி', 'எப்பொழுது','.',
                                         ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}')))


            elif lan=="hi":
                operators = list(set(('अंदर', 'अत', 'अदि', 'अप', 'अपना', 'अपनि', 'अपनी', 'अपने', 'अभि', 'अभी', 'आदि', 'आप', 'इंहिं', 'इंहें', 'इंहों', 'इतयादि', 'इत्यादि',
                                         'इन', 'इनका', 'इन्हीं', 'इन्हें', 'इन्हों', 'इस', 'इसका', 'इसकि', 'इसकी', 'इसके', 'इसमें', 'इसि', 'इसी', 'इसे', 'उंहिं', 'उंहें', 'उंहों', 'उन',
                                         'उनका', 'उनकि', 'उनकी', 'उनके', 'उनको', 'उन्हीं', 'उन्हें', 'उन्हों', 'उस', 'उसके', 'उसि', 'उसी', 'उसे', 'एक', 'एवं', 'एस', 'एसे', 'ऐसे',
                                         'ओर', 'और', 'कइ', 'कई', 'कर', 'करता', 'करते', 'करना', 'करने', 'करें', 'कहते', 'कहा', 'का', 'काफि', 'काफ़ी', 'कि', 'किंहें', 'किंहों',
                                         'कितना', 'किन्हें', 'किन्हों', 'किया', 'किर', 'किस', 'किसि', 'किसी', 'किसे', 'की', 'कुछ', 'कुल', 'के', 'को', 'कोइ', 'कोई', 'कोन', 'कोनसा',
                                         'कौन', 'कौनसा', 'गया', 'घर', 'जब', 'जहाँ', 'जहां', 'जा', 'जिंहें', 'जिंहों', 'जितना', 'जिधर', 'जिन', 'जिन्हें', 'जिन्हों', 'जिस', 'जिसे', 'जीधर',
                                         'जेसा', 'जेसे', 'जैसा', 'जैसे', 'जो', 'तक', 'तब', 'तरह', 'तिंहें', 'तिंहों', 'तिन', 'तिन्हें', 'तिन्हों', 'तिस', 'तिसे', 'तो', 'था', 'थि', 'थी', 'थे',
                                         'दबारा', 'दवारा', 'दिया', 'दुसरा', 'दुसरे', 'दूसरे', 'दो', 'द्वारा', 'न', 'नहिं', 'नहीं', 'ना', 'निचे', 'निहायत', 'नीचे', 'ने', 'पर', 'पहले', 'पुरा',
                                         'पूरा', 'पे', 'फिर', 'बनि', 'बनी', 'बहि', 'बही', 'बहुत', 'बाद', 'बाला', 'बिलकुल', 'भि', 'भितर', 'भी', 'भीतर', 'मगर', 'मानो', 'मे', 'में', 'यदि',
                                         'यह', 'यहाँ', 'यहां', 'यहि', 'यही', 'या', 'यिह', 'ये', 'रखें', 'रवासा', 'रहा', 'रहे', 'ऱ्वासा', 'लिए', 'लिये', 'लेकिन', 'व', 'वगेरह', 'वरग', 'वर्ग',
                                         'वह', 'वहाँ', 'वहां', 'वहिं', 'वहीं', 'वाले', 'वुह', 'वे', 'वग़ैरह', 'संग', 'सकता', 'सकते', 'सबसे', 'सभि', 'सभी', 'साथ', 'साबुत', 'साभ', 'सारा',
                                         'से', 'सो', 'हि', 'ही', 'हुअ', 'हुआ', 'हुइ', 'हुई', 'हुए', 'हे', 'हें', 'है', 'हैं', 'हो', 'होता', 'होति', 'होती', 'होते', 'होना', 'होने' ,'जाते',
                                         '.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}')))
            
            
            
            words=[i for i in words if i not in operators]
            # print(words)
            for element in words:
                if element=="":
                    words.remove(element)

            context["words"] = words

            l1=[]
            for word in words:
                if word != " ":
                    a = Page.objects.filter(content__contains=word)
                    all_ids=[i.id for i in a]
                    l1.append(all_ids)
                else:
                    print('hello')
                # print(all_ids)
            # x=set.intersection(*map(set,l1))  #get the pages with all the words occuring together (not feasible in cases where the exact line is being demaded)
            final =[]
            for i in l1:
                # print(i)
                final = list(set(i+final))

            x = l1[0]
            page_ids=[i for i in final]
            # for i in Book.objects.filter(pages__id__in=page_ids).distinct():
            #     print(i.id)
            context['results'] = Book.objects.filter(pages__id__in=page_ids).distinct()  # get the book outputs on the basis of the query made 
            pages=[]
            parts=[]
            book_ids=[]
            image_urls=[]
            dictionary={}
            # context['page_list'] = Page.objects.filter(id__in=page_ids)
            page_lines = {i:[] for i in page_ids}
            page_lines2 = {i:[] for i in page_ids}
            # shutil.rmtree('/home/riya/newdjango/cvitsearch/media/tmp/all_matches/')
            # os.mkdir('/home/riya/newdjango/cvitsearch/media/tmp/all_matches/')

            line_list_test = []
            
            page_list_new = []

            final_urls=[]
            final_book_list=[]
            pageid_url=[]


            #from collections import defaultdict
            res_dictionary={}

            page_list = Page.objects.filter(id__in=page_ids)

            segmented_image_list = []

            for i in page_ids:
                pages.append(i)
                # line_list = Page.objects.get(id=i).content.split('.')

                b = Page.objects.get(pk=i)
                book_id = b.book_id
                # print(book_id)
               
                if book_id == id:



                    new_line_list = Page.objects.get(id=i).content.split('\n')
                    if new_line_list is None:
                        break


                    segmentation_list = Page.objects.get(id=i).segment.split("\n")
                    segmented = []
                    for x in segmentation_list:
                        x = x.strip("\r")
                        segmented.append(x)



                    # for line in line_list:
                    index_list =[]
                    for line in new_line_list:
                        cap= False
                        count=1
                        for word in words:
                            if word.lower() in line:
                                index_list.append(new_line_list.index(line))
                                l=line.replace(word,'<b class="text-success">{}</b>'.format(word.upper()))
                                cap=True
                        if cap:
                            page_lines[i].append(l)
                    image_content = Page.objects.get(id=i).image.url
                    image_urls.append(image_content)



                    #Use the foreign key in the page model to retrieve the book ids wrt to their page ids
                    b = Page.objects.get(pk=i)
                    book_id = b.book_id
                    book_ids.append(book_id)



                    image = cv2.imread("/home/ndlsearch19/cvitsearch"+Page.objects.get(id=i).image.url)
                    overlay = image.copy()
                    for index_num in index_list:
                        # print(index_num)
                        for seg in segmented:
                            if index_num == segmented.index(seg) :
                                seg = seg.strip("\r").split("\t")
                                # print(seg)
                                x1 = int(seg[0])
                                y1 = int(seg[1])
                                x2 = int(seg[2])+x1
                                y2 = int(seg[3])+y1
                                cv2.rectangle(overlay,(x1,y1),(x2,y2),(0,255,255),-1)
                                alpha = 0.5  # Transparency factor.
                                img_written = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
                                lettersAndDigits = string.ascii_letters + string.digits
                                random_string = ''.join(random.choice(lettersAndDigits) for i in range(6))
                                new_image = cv2.imwrite("/home/ndlsearch19/cvitsearch/media/tmp/all_matches/"+str(Page.objects.get(id=i).image.url.split("/")[-1].split(".")[0])+"_"+random_string+"."+str(Page.objects.get(id=i).image.url.split("/")[-1].split(".")[-1]), img_written)


                    res_dictionary[i] = "/media/tmp/all_matches/"+str(Page.objects.get(id=i).image.url.split("/")[-1].split(".")[0])+"_"+random_string+"."+str(Page.objects.get(id=i).image.url.split("/")[-1].split(".")[-1])

                    segmented_image_list.append("/home/ndlsearch19/cvitsearch/media/tmp/all_matches/"+str(Page.objects.get(id=i).image.url.split("/")[-1]))




                    # for word in words :
                    #     for line in line_list:
                    #         if word in line:
                    #             ind = line_list.index(line)
                    #             line = line.lower()
                    #             line = line.replace(word,word.upper())
                    #             parts.append(line)


            context['page_list'] = page_list

            context["res_dictionary"] = res_dictionary
            # print(context["res_dictionary"])




        # from django.forms.models import model_to_dict

        # data = self.get_queryset()

        # for item in data:
        #    item['page_list'] = model_to_dict(item['page_list'])
        # diction = json.dumps(list(res_dictionary.values()))
        # page_list = json.dumps(list(page_list.values()))
    # pdb.set_trace()
    res = JsonResponse({"diction" : res_dictionary}) 

    return res




def ajax_search(request):
    data = {
            'results': [],
            'error_message': '',
            'nresults': 0
            }
    if not request.GET.get('q', None):
        data['error_message'] = 'No Search Query Given'
        return JsonResponse(data)
    else:
        q = request.GET.get('q', None).strip()
        print('Page database is searching against query: "{}"'.format(query))

    results = get_search_results(q)
    data['nresults'] = results.count()
    if data['nresults'] == 0:
        data['error_message'] = 'No results found, Please redefine your Search'
        return JsonResponse(data)
    for i in results:
        data['results'].append( {
            'pageid': i.id,
            'pagetitle': i.pagetitle,
            'book': i.book.title,
        })
    return JsonResponse(data)

def book(request, book_id):
    context = {}
    try:
        b = Book.objects.get(pk=book_id)
    except:
        messages.error(request, 'No book with this ID')
        return redirect(request.META.get('HTTP_REFERER','/'))
    context['book'] = b
    return render(request, 'home/book.html', context)



