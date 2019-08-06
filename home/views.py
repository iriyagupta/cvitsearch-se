"""
Import important libraries and required modules 

"""

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
from django.db.models import Q,Count
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


""" Home page """ 
def index(request):
    page_title = 'Home'
    context ={}
    a = Page.objects.count()
    context["total"] = a
    book_type = Book.objects.values_list("id",flat=True).order_by("id") 
    ids = [x for x in book_type]
    test = Book.objects.values('genre').annotate(Count('genre')) 

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




    context["ann"]=Announcement.objects.all()
    return render(request, 'home/index.jinja2',context)



"""Contact"""
def contact(request):
    page_title = 'Contact Us'
    return render(request, 'home/contact.jinja2',locals())



"""Statistics of the books uploaded """
def stats(request):
    page_title = 'General Statics'
    uploaded = Book.objects.all().count()
    language_split={}
    for each in Book.objects.all():
        each = each.language
        language_split[each] = Book.objects.filter(language=each).values('language').order_by('language').annotate(count=Count('id'))
    return render(request, 'home/stat.jinja2',locals())


"""British Library List"""
def list1(request):
    context={}
    page_title = 'British Library'
    a = Book.objects.filter(source="British Library")
    ids = [i.id for i in a]
    dataset1 = Book.objects.filter(id__in=ids).order_by("language","title")
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


"""IIITH dataset list"""
def list2(request):
    context={}
    page_title = 'IIITH Library'
    a = Book.objects.filter(source="IIITH Library")
    ids = [i.id for i in a]

    dataset2 = Book.objects.filter(id__in=ids).order_by("language","title")
    # print(dataset2)
    context['language_list'] = list(set([i.language for i in Book.objects.filter(id__in=ids)]))
    lang = request.GET.get('lang', None)

    if lang:
        dataset2 = dataset2.filter(language=lang).distinct()

    npages = request.GET.get('npages')
        
    if npages:
        if npages == '1':
            dataset2=[i for i in dataset2 if len(i.numpages)<3]
        elif npages == '2':
            dataset2=[i for i in dataset2 if len(i.numpages) < 4]

    context['dataset2']=dataset2
    pages_for_pagination = []
    list_dataset2 = dataset2

    for content in list_dataset2:
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

    context['dataset2']=pages_for_pagination

    return render(request, 'home/list2.jinja2', context)


"""Searched Results"""
def search(request):
    page_title = 'Searched Results'
    context = {}
    q = request.GET.get('q',None)

    para = request.GET.get('parameter',None)

    lan = request.GET.get('language',None)
    # print(lan)
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
            print(id1,id2,id3,id4)
            book_list_common=[]
            for i in id4:
                book_list = Page.objects.get(pk=i)
                b = book_list.book_id
                book_list_common.append(b)
            print(book_list_common)

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
                print(count)
            context['page_list'] = Page.objects.filter(id__in=page_ids)
            # print(context["page_list"])
            context['page_lines'] = page_lines
        elif para=="content":
            if q.startswith('"') and q.endswith('"'):
                q = q.replace('"','')
                # print(q)
                a=PageIndex.search().query('match_phrase',content=q)
                page_ids=[i.id for i in a]
                # print(page_ids)
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
                    print(count)   
                context['results'] = Book.objects.filter(pages__id__in=page_ids).distinct()
                total = context["results"].count()
                context['page_list'] = Page.objects.filter(id__in=page_ids)
                context['page_lines'] = page_lines
                q = request.GET.get('q',None)
            else:
                words = q.split(" ")
                if lan == "sel":
                    operators = list(set())
                if lan == 'en':
                    operators = list(set(("i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", 
                                        "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", 
                                        "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", 
                                        "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", 
                                        "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
                                        "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", 
                                        "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about",
                                        "against", "between", "into", "through", "during", "before", "after", "above", "below",
                                        "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", 
                                        "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", 
                                        "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", 
                                        "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now")))
                elif lan == "te":
                    operators=list(set(('వీరి', 'లను', 'కొందరు', 'అను', 'ఆమె', 'ఇవీ', 'అసలు', 'అప్పుడు', 'ఉన్నత', 'ఇప్పుడు', 'లాంటి',
                                        'వీరు', 'వీటిని', 'క్రింది', 'వారిని', 'ఇక్కడి', 'పైగా', 'అలాగే', 'దానిని', 'వచ్చే', 'కాక', 'భాగం', 'గాని', 'దగ్గర',
                                        'అప్పటి', 'కనుక', 'దానికి', 'ఏర్పాటు', 'అలా', 'లేక', 'ఉంటే', 'కలవు', 'కేవలం', 'ఎంతో', 'ఎలా',
                                        'కలిసి', 'ఈయన', 'ఉండి', 'అనేది', 'లేకుండా', 'సుమారు', 'మొదలైన', 'రచనలు', 'మన', 'అక్కడ',
                                         'నా', 'అత్యంత', 'కొంత', 'కలదు', 'లేని')))
                elif lan == "ta":
                    operators= list(set(('ஒரு', 'என்று', 'செய்து', 'இந்த', 'மேலும்', 'மற்றும்', 'இருந்தது', 'என்ற', 'வரும்', 'வேண்டும்', 'போது',
                                         'இது', 'அவர்', 'வந்து', 'அந்த', 'முதல்', 'அல்லது', 'தான்', 'என', 'ஆனால்', 'வரை', 'நான்', 'கடந்த',
                                        'கொண்டு', 'இன்று', 'பல', 'அவர்கள்', 'உள்ள', 'என்ன', 'என்பது', 'அவன்', 'அது', 'இருக்கும்', 'தன்', 'சில',
                                        'ஆண்டு', 'இருந்து', 'மூலம்', 'இல்லை', 'அதன்', 'உள்ளது', 'என்', 'இன்', 'அங்கு', 'இங்கே', 'எப்படி', 'எப்பொழுது')))

                elif lan == "bn":
                    operators = list(set(('অতএব', 'অথচ', 'অথবা', 'অনুযায়ী', 'অনেক', 'অনেকে', 'অনেকেই', 'অন্তত', 'অন্য', 'অবধি', 'অবশ্য', 'অর্থাত', 'আই', 'আগামী',
                                         'আগে', 'আগেই', 'আছে', 'আজ', 'আদ্যভাগে', 'আপনার', 'আপনি', 'আবার', 'আমরা', 'আমাকে', 'আমাদের', 'আমার', 'আমি', 'আর',
                                        'আরও', 'ই', 'ইত্যাদি', 'ইহা', 'উচিত', 'উত্তর', 'উনি', 'উপর', 'উপরে', 'এ', 'এঁদের', 'এঁরা', 'এই', 'একই', 'একটি', 'একবার',
                                        'একে', 'এক্', 'এখন', 'এখনও', 'এখানে', 'এখানেই', 'এটা', 'এটাই', 'এটি', 'এত', 'এতটাই', 'এতে', 'এদের', 'এব', 'এবং', 'এবার',
                                        'এমন', 'এমনকী', 'এমনি', 'এর', 'এরা', 'এল', 'এস', 'এসে', 'ঐ', 'ও', 'ওঁদের', 'ওঁর', 'ওঁরা', 'ওই', 'ওকে', 'ওখানে', 'ওদের',
                                         'ওর', 'ওরা', 'কখনও', 'কত', 'কবে', 'কমনে', 'কয়েক', 'কয়েকটি', 'করছে', 'করছেন', 'করতে', 'করবে', 'করবেন', 'করলে', 'করলেন',
                                        'করা', 'করাই', 'করায়', 'করার', 'করি', 'করিতে', 'করিয়া', 'করিয়ে', 'করে', 'করেই', 'করেছিলেন', 'করেছে', 'করেছেন', 'করেন',
                                        'কাউকে', 'কাছ', 'কাছে', 'কাজ', 'কাজে', 'কারও', 'কারণ', 'কি', 'কিংবা', 'কিছু', 'কিছুই', 'কিন্তু', 'কী', 'কে', 'কেউ',
                                        'কেউই', 'কেখা', 'কেন', 'কোটি', 'কোন', 'কোনও', 'কোনো', 'ক্ষেত্রে', 'কয়েক', 'খুব', 'গিয়ে', 'গিয়েছে', 'গিয়ে', 'গুলি',
                                        'গেছে', 'গেল', 'গেলে', 'গোটা', 'চলে', 'চান', 'চায়', 'চার', 'চালু', 'চেয়ে', 'চেষ্টা', 'ছাড়া', 'ছাড়াও', 'ছিল', 'ছিলেন',
                                         'জন', 'জনকে', 'জনের', 'জন্য', 'জন্যওজে', 'জানতে', 'জানা', 'জানানো', 'জানায়', 'জানিয়ে', 'জানিয়েছে', 'জে', 'জ্নজন', 'টি', 'ঠিক',
                                          'তখন', 'তত', 'তথা', 'তবু', 'তবে', 'তা', 'তাঁকে', 'তাঁদের', 'তাঁর', 'তাঁরা', 'তাঁাহারা', 'তাই', 'তাও', 'তাকে', 'তাতে', 'তাদের',
                                         'তার', 'তারপর', 'তারা', 'তারৈ', 'তাহলে', 'তাহা', 'তাহাতে', 'তাহার', 'তিনঐ', 'তিনি', 'তিনিও', 'তুমি', 'তুলে', 'তেমন', 'তো', 'তোমার', 
                                         'থাকবে', 'থাকবেন', 'থাকা', 'থাকায়', 'থাকে', 'থাকেন', 'থেকে', 'থেকেই', 'থেকেও', 'দিকে', 'দিতে', 'দিন', 'দিয়ে', 'দিয়েছে', 'দিয়েছেন', 
                                         'দিলেন', 'দু', 'দুই', 'দুটি', 'দুটো', 'দেওয়া', 'দেওয়ার', 'দেওয়া', 'দেখতে', 'দেখা', 'দেখে', 'দেন', 'দেয়', 'দ্বারা', 'ধরা', 'ধরে', 'ধামার',
                                          'নতুন', 'নয়', 'না', 'নাই', 'নাকি', 'নাগাদ', 'নানা', 'নিজে', 'নিজেই', 'নিজেদের', 'নিজের', 'নিতে', 'নিয়ে', 'নিয়ে', 'নেই', 'নেওয়া', 'নেওয়ার', 
                                          'নেওয়া', 'নয়', 'পক্ষে', 'পর', 'পরে', 'পরেই', 'পরেও', 'পর্যন্ত', 'পাওয়া', 'পাচ', 'পারি', 'পারে', 'পারেন', 'পি', 'পেয়ে', 'পেয়্র্', 'প্রতি', 
                                          'প্রথম', 'প্রভৃতি', 'প্রযন্ত', 'প্রাথমিক', 'প্রায়', 'প্রায়', 'ফলে', 'ফিরে', 'ফের', 'বক্তব্য', 'বদলে', 'বন', 'বরং', 'বলতে', 'বলল', 'বললেন', 
                                          'বলা', 'বলে', 'বলেছেন', 'বলেন', 'বসে', 'বহু', 'বা', 'বাদে', 'বার', 'বি', 'বিনা', 'বিভিন্ন', 'বিশেষ', 'বিষয়টি', 'বেশ', 'বেশি', 'ব্যবহার', 
                                          'ব্যাপারে', 'ভাবে', 'ভাবেই', 'মতো', 'মতোই', 'মধ্যভাগে', 'মধ্যে', 'মধ্যেই', 'মধ্যেও', 'মনে', 'মাত্র', 'মাধ্যমে', 'মোট', 'মোটেই', 'যখন', 
                                          'যত', 'যতটা', 'যথেষ্ট', 'যদি', 'যদিও', 'যা', 'যাঁর', 'যাঁরা', 'যাওয়া', 'যাওয়ার', 'যাওয়া', 'যাকে', 'যাচ্ছে', 'যাতে', 'যাদের', 'যান', 'যাবে', 
                                          'যায়', 'যার', 'যারা', 'যিনি', 'যে', 'যেখানে', 'যেতে', 'যেন', 'যেমন', 'র', 'রকম', 'রয়েছে', 'রাখা', 'রেখে', 'লক্ষ', 'শুধু', 'শুরু', 'সঙ্গে', 
                                          'সঙ্গেও', 'সব', 'সবার', 'সমস্ত', 'সম্প্রতি', 'সহ', 'সহিত', 'সাধারণ', 'সামনে', 'সি', 'সুতরাং', 'সে', 'সেই', 'সেখান', 'সেখানে', 'সেটা', 
                                          'সেটাই', 'সেটাও', 'সেটি', 'স্পষ্ট', 'স্বয়ং', 'হইতে', 'হইবে', 'হইয়া', 'হওয়া', 'হওয়ায়', 'হওয়ার', 'হচ্ছে', 'হত', 'হতে', 'হতেই', 'হন', 'হবে', 
                                          'হবেন', 'হয়', 'হয়তো', 'হয়নি', 'হয়ে', 'হয়েই', 'হয়েছিল', 'হয়েছে', 'হয়েছেন', 'হল', 'হলে', 'হলেই', 'হলেও', 'হলো', 'হাজার', 'হিসাবে', 'হৈলে', 
                                          'হোক', 'হয়')))
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
                                         'से', 'सो', 'हि', 'ही', 'हुअ', 'हुआ', 'हुइ', 'हुई', 'हुए', 'हे', 'हें', 'है', 'हैं', 'हो', 'होता', 'होति', 'होती', 'होते', 'होना', 'होने')))
                
                elif lan =="sa":
                    operators = list(set(('अहम्', 'आवाम्', 'वयम्', 'माम्', 'मा', 'आवाम्', 'अस्मान्', 'नः', 'मया', 'आवाभ्याम्', 'अस्माभिस्', 'मह्यम्', 'मे', 'आवाभ्याम्', 'नौ', 'अस्मभ्यम्', 'नः',
                                     'मत्', 'आवाभ्याम्', 'अस्मत्', 'मम', 'मे', 'आवयोः', 'अस्माकम्', 'नः', 'मयि', 'आवयोः', 'अस्मासु', 'त्वम्', 'युवाम्', 'यूयम्', 'त्वाम्', 'त्वा', 'युवाम्', 'वाम्',
                                      'युष्मान्', 'वः', 'त्वया', 'युवाभ्याम्', 'युष्माभिः', 'तुभ्यम्', 'ते', 'युवाभ्याम्', 'वाम्', 'युष्मभ्यम्', 'वः', 'त्वत्', 'युवाभ्याम्', 'युष्मत्', 'तव', 'ते', 'युवयोः', 'वाम्',
                                       'युष्माकम्', 'वः', 'त्वयि', 'युवयोः', 'युष्मासु', 'सः', 'तौ', 'ते', 'तम्', 'तौ', 'तान्', 'तेन', 'ताभ्याम्', 'तैः', 'तस्मै', 'ताभ्याम्', 'तेभ्यः', 'तस्मात्', 'ताभ्याम्', 
                                       'तेभ्यः', 'तस्य', 'तयोः', 'तेषाम्', 'तस्मिन्', 'तयोः', 'तेषु', 'सा', 'ते', 'ताः', 'ताम्', 'ते', 'ताः', 'तया', 'ताभ्याम्', 'ताभिः', 'तस्यै', 'ताभ्याम्', 'ताभ्यः', 'तस्याः', 
                                       'ताभ्याम्', 'ताभ्यः', 'तस्य', 'तयोः', 'तासाम्', 'तस्याम्', 'तयोः', 'तासु', 'तत्', 'ते', 'तानि', 'तत्', 'ते', 'तानि', 'तया', 'ताभ्याम्', 'ताभिः', 'तस्यै', 'ताभ्याम्', 'ताभ्यः', 
                                       'तस्याः', 'ताभ्याम्', 'ताभ्यः', 'तस्य', 'तयोः', 'तासाम्', 'तस्याम्', 'तयोः', 'तासु', 'अयम्', 'इमौ', 'इमे', 'इमम्', 'इमौ', 'इमान्', 'अनेन', 'आभ्याम्', 'एभिः', 'अस्मै', 
                                       'आभ्याम्', 'एभ्यः', 'अस्मात्', 'आभ्याम्', 'एभ्यः', 'अस्य', 'अनयोः', 'एषाम्', 'अस्मिन्', 'अनयोः', 'एषु', 'इयम्', 'इमे', 'इमाः', 'इमाम्', 'इमे', 'इमाः', 'अनया', 'आभ्याम्', 
                                       'आभिः', 'अस्यै', 'आभ्याम्', 'आभ्यः', 'अस्याः', 'आभ्याम्', 'आभ्यः', 'अस्याः', 'अनयोः', 'आसाम्', 'अस्याम्', 'अनयोः', 'आसु', 'इदम्', 'इमे', 'इमानि', 'इदम्', 'इमे', 
                                       'इमानि', 'अनेन', 'आभ्याम्', 'एभिः', 'अस्मै', 'आभ्याम्', 'एभ्यः', 'अस्मात्', 'आभ्याम्', 'एभ्यः', 'अस्य', 'अनयोः', 'एषाम्', 'अस्मिन्', 'अनयोः', 'एषु', 'एषः', 'एतौ', 
                                       'एते', 'एतम्', 'एनम्', 'एतौ', 'एनौ', 'एतान्', 'एनान्', 'एतेन', 'एताभ्याम्', 'एतैः', 'एतस्मै', 'एताभ्याम्', 'एतेभ्यः', 'एतस्मात्', 'एताभ्याम्', 'एतेभ्यः', 'एतस्य', 'एतस्मिन्', 
                                       'एतेषाम्', 'एतस्मिन्', 'एतस्मिन्', 'एतेषु', 'एषा', 'एते', 'एताः', 'एताम्', 'एनाम्', 'एते', 'एने', 'एताः', 'एनाः', 'एतया', 'एनया', 'एताभ्याम्', 'एताभिः', 'एतस्यै', 'एताभ्याम्', 
                                       'एताभ्यः', 'एतस्याः', 'एताभ्याम्', 'एताभ्यः', 'एतस्याः', 'एतयोः', 'एनयोः', 'एतासाम्', 'एतस्याम्', 'एतयोः', 'एनयोः', 'एतासु', 'एतत्', 'एतद्', 'एते', 'एतानि', 'एतत्', 'एतद्', 
                                       'एनत्', 'एनद्', 'एते', 'एने', 'एतानि', 'एनानि', 'एतेन', 'एनेन', 'एताभ्याम्', 'एतैः', 'एतस्मै', 'एताभ्याम्', 'एतेभ्यः', 'एतस्मात्', 'एताभ्याम्', 'एतेभ्यः', 'एतस्य', 'एतयोः', 
                                       'एनयोः', 'एतेषाम्', 'एतस्मिन्', 'एतयोः', 'एनयोः', 'एतेषु', 'असौ', 'अमू', 'अमी', 'अमूम्', 'अमू', 'अमून्', 'अमुना', 'अमूभ्याम्', 'अमीभिः', 'अमुष्मै', 'अमूभ्याम्', 'अमीभ्यः', 
                                       'अमुष्मात्', 'अमूभ्याम्', 'अमीभ्यः', 'अमुष्य', 'अमुयोः', 'अमीषाम्', 'अमुष्मिन्', 'अमुयोः', 'अमीषु', 'असौ', 'अमू', 'अमूः', 'अमूम्', 'अमू', 'अमूः', 'अमुया', 'अमूभ्याम्', 'अमूभिः', 
                                       'अमुष्यै', 'अमूभ्याम्', 'अमूभ्यः', 'अमुष्याः', 'अमूभ्याम्', 'अमूभ्यः', 'अमुष्याः', 'अमुयोः', 'अमूषाम्', 'अमुष्याम्', 'अमुयोः', 'अमूषु', 'अमु', 'अमुनी', 'अमूनि', 'अमु', 'अमुनी', 'अमूनि', 
                                       'अमुना', 'अमूभ्याम्', 'अमीभिः', 'अमुष्मै', 'अमूभ्याम्', 'अमीभ्यः', 'अमुष्मात्', 'अमूभ्याम्', 'अमीभ्यः', 'कः', 'कौ', 'के', 
                                       'कम्', 'कौ', 'कान्', 'केन', 'काभ्याम्', 'कैः', 'कस्मै', 'काभ्याम्', 'केभ्य', 'कस्मात्', 'काभ्याम्', 'केभ्य', 'कस्य', 'कयोः', 'केषाम्', 'कस्मिन्', 'कयोः', 'केषु', 'का', 'के', 'काः', 
                                       'काम्', 'के', 'काः', 'कया', 'काभ्याम्', 'काभिः', 'कस्यै', 'काभ्याम्', 'काभ्यः', 'कस्याः', 'काभ्याम्', 'काभ्यः', 'कस्याः', 'कयोः', 'कासाम्', 'कस्याम्', 'कयोः', 'कासु', 'किम्', 'के', 
                                       'कानि', 'किम्', 'के', 'कानि', 'केन', 'काभ्याम्', 'कैः', 'कस्मै', 'काभ्याम्', 'केभ्य', 'कस्मात्', 'काभ्याम्', 'केभ्य', 'कस्य', 'कयोः', 'केषाम्', 'कस्मिन्', 'कयोः', 'केषु', 'भवान्', 
                                       'भवन्तौ', 'भवन्तः', 'भवन्तम्', 'भवन्तौ', 'भवतः', 'भवता', 'भवद्भ्याम्', 'भवद्भिः', 'भवते', 'भवद्भ्याम्', 'भवद्भ्यः', 'भवतः', 'भवद्भ्याम्', 'भवद्भ्यः', 'भवतः', 'भवतोः', 'भवताम्', 'भवति', 
                                       'भवतोः', 'भवत्सु', 'भवती', 'भवत्यौ', 'भवत्यः', 'भवतीम्', 'भवत्यौ', 'भवतीः', 'भवत्या', 'भवतीभ्याम्', 'भवतीभिः', 'भवत्यै', 'भवतीभ्याम्', 'भवतीभिः', 'भवत्याः', 'भवतीभ्याम्', 'भवतीभिः', 
                                       'भवत्याः', 'भवत्योः', 'भवतीनाम्', 'भवत्याम्', 'भवत्योः', 'भवतीषु', 'भवत्', 'भवती', 'भवन्ति', 'भवत्', 'भवती', 'भवन्ति', 'भवता', 'भवद्भ्याम्', 'भवद्भिः', 'भवते', 'भवद्भ्याम्', 'भवद्भ्यः', 
                                       'भवतः', 'भवद्भ्याम्', 'भवद्भ्यः', 'भवतः', 'भवतोः', 'भवताम्', 'भवति', 'भवतोः', 'भवत्सु', 'अये', 'अरे', 'अरेरे', 'अविधा', 'असाधुना', 'अस्तोभ', 'अहह', 'अहावस्', 'आम्', 'आर्यहलम्', 'आह', 
                                       'आहो', 'इस्', 'उम्', 'उवे', 'काम्', 'कुम्', 'चमत्', 'टसत्', 'दृन्', 'धिक्', 'पाट्', 'फत्', 'फाट्', 'फुडुत्', 'बत', 'बाल्', 'वट्', 'व्यवस्तोभति', 'व्यवस्तुभ्', 'षाट्', 'स्तोभ', 'हुम्मा', 'हूम्', 
                                       'अति', 'अधि', 'अनु', 'अप', 'अपि', 'अभि', 'अव', 'आ', 'उद्', 'उप', 'नि', 'निर्', 'परा', 'परि', 'प्र', 'प्रति', 'वि', 'सम्', 'अथवा', 'उत', 'अन्यथा', 'इव', 'च', 'चेत्', 'यदि', 
                                       'तु', 'परन्तु', 'यतः', 'करणेन', 'हि', 'यतस्', 'यदर्थम्', 'यदर्थे', 'यर्हि', 'यथा', 'यत्कारणम्', 'येन', 'ही', 'हिन', 'यथा', 'यतस्','स्थाने', 'अह', 'एव', 'एवम्', 'कच्चित्', 'कु', 'कुवित्', 
                                       'कूपत्', 'च', 'चण्', 'चेत्', 'तत्र', 'नकिम्', 'नह', 'नुनम्', 'नेत्', 'भूयस्', 'मकिम्', 'मकिर्', 'यत्र', 'युगपत्', 'वा', 'शश्वत्', 'सूपत्', 'ह', 'हन्त', 'हि', 'सर्वम्', 'सर्वे')))

                words=[i for i in words if i not in operators]
                context["words"] = words
                l1=[]
                for word in words:
                    a=PageIndex.search().query('match_phrase',content=word)
                    all_ids=[i.id for i in a]
                    l1.append(all_ids)
                # x=set.intersection(*map(set,l1))  #get the pages with all the words occuring together (not feasible in cases where the exact line is being demaded)
                x = l1[0]
                page_ids=[i for i in x]
                print("\n\n")
                context['results'] = Book.objects.filter(pages__id__in=page_ids).distinct()  # get the book outputs on the basis of the query made 
                pages=[]
                parts=[]
                book_ids=[]
                image_urls=[]
                dictionary={}
                context['page_list'] = Page.objects.filter(id__in=page_ids)
                page_lines = {i:[] for i in page_ids}
                page_lines2 = {i:[] for i in page_ids}
                for i in page_ids:
                    pages.append(i)
                    print(pages.count(words))
                    line_list = Page.objects.get(id=i).content.split('.')
                    for line in line_list:
                        l=line.lower()
                        cap= False
                        count=1
                        for word in words:
                            if word.lower() in l:
                                l=l.replace(word,word.upper())
                                cap=True
                        if cap:
                            page_lines[i].append(l)
                    image_content = Page.objects.get(id=i).image.url
                    image_urls.append(image_content)

                    #Use the foreign key in the page model to retrieve the book ids wrt to their page ids
                    b = Page.objects.get(pk=i)
                    book_id = b.book_id
                    book_ids.append(book_id)

                    for word in words :
                        for line in line_list:
                            if word in line:
                                ind = line_list.index(line)
                                line = line.lower()
                                line = line.replace(word,word.upper())
                                parts.append(line)
                context['parts']=parts
                context["book_ids"]=book_ids
                context["image_content"]= image_urls
                context['page_lines'] = page_lines

                content = zip(book_ids,parts,image_urls,pages)

                from collections import defaultdict
                diction = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
                value=[]
                nested={}
                for i, j , k , l  in content:
                    diction[i][l]["query_des"].append(j)
                    diction[i][l]["image_urls"].append(k)
                dictioni={}
                for i in diction:
                    a=''
                    for j in diction[i]:
                        a=diction[i][j]["query_des"][0]
                        break
                    dictioni[i]=a
                context["dictionary"]=diction
                context["content"]=content
                context["dictioni"]=dictioni
                total = context["results"].count()
        else:
            a = BookIndex.search().query('match_phrase',title=q)
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
    print(z2)
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


    # count_source=[]
    # counter=[]
    # source_param = request.GET.get('source_param')
    # num = Book.objects.values('source').order_by().annotate(Count('source'))
    # if source_param:
    #     context["results"] = context["results"].filter(source=source_param)
    # for i in num:
    #     count_source.append(i["source"])
    #     counter.append(i["source__count"])
    # zipped_list = zip(count_source,counter)
    # context["zipped_list"]=zipped_list

    context['q'] = q
    context["time_diff"] = str(time_diff)
    context["total"] = total
    return render(request, 'home/search.jinja2', context)


"""test ajax code"""
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



"""test version for line segmentation"""
def line_segment(request):
    # context={}
    # q = request.GET.get('q',None)
    # print(q)
    # context['q'] = q
    # a=PageIndex.search().query('match_phrase',content=q)
    # ids=[i.id for i in a]  
    # print(ids)  

    # bookid=request.GET.get('bookid',None)
    # context['bookid'] = bookid
    # bookid=int(bookid)
    # ids = [i for i in ids if Page.objects.get(id=i).book.id==bookid]

    # content =[Page.objects.get(id=i).content for i in ids]
    # image_content = [Page.objects.get(id=i).image.url for i in ids if Page.objects.get(id=i).image]
    # context['ids']= ids
    # image_data=[]
    # contents = []

    # # #testing module
    # shutil.rmtree('/home/riya/newdjango/cvitsearch/media/tmp/')
    # os.mkdir('/home/riya/newdjango/cvitsearch/media/tmp/')
    # zipped = zip(content,image_content)
    # for c,img in zipped:
    #     list_of_indexes = []
    #     c = c.lower()
    #     q = q.lower()
    #     c = c.replace(q,'<em><span style="color:blue;">'+q+'</span></em>')
    #     print(c)
    #     image = cv2.imread("/home/riya/newdjango/cvitsearch/"+img)
    #     gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    #     ret,thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)
    #     kernel = np.ones((5,100))
    #     img_dilation = cv2.dilate(thresh, kernel, iterations=1)
    #     #find contours
    #     ctrs, hier = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #     #sort contours
    #     sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0] )
    #     sorted_ctrs = sorted(sorted_ctrs, key=lambda ctr: cv2.boundingRect(ctr)[1] )
    #     out_file = "/home/riya/newdjango/cvitsearch/media/tmp/positions.txt"
    #     out_writer = open(out_file, "w")
    #     counter = 0
    #     a =[]
    #     for i, ctr in enumerate(sorted_ctrs):
    #         pos = []
    #         x, y, w, h = cv2.boundingRect(ctr)
    #         roi = image[y:y+h, x:x+w]
    #         pos.append(x)
    #         pos.append(y)
    #         pos.append(x+w)
    #         pos.append(y+h)
    #         pos = [str(int(each)) for each in pos]
    #         component= 255 -roi
    #         area = component.shape[0]*component.shape[1]
    #         if area > 10500: 
    #             out_writer.write(str(counter)+" "+" ".join(pos)+'\n')
    #             counter+=1                
    #     out_writer.close()
    #     fileName=codecs.open("/home/riya/newdjango/cvitsearch/media/tmp/positions.txt",encoding="utf-8")
    #     lines = fileName.read()
    #     positions=lines.splitlines()
    #     # print(positions)
    #     cont = c.splitlines()
    #     cont = list(filter(None, cont))
    #     for i in cont:
    #         if q in i:
    #             list_of_indexes.append(cont.index(i))
    #     for val in positions:
    #         ind = val.split(" ")
    #         # print(ind)
    #         for j in list_of_indexes:
    #             if j == int(ind[0]):
    #                 img_written = cv2.rectangle(image,(int(ind[1]),int(ind[2])), (int(ind[3]),int(ind[4])),(0,0,255),5)
    #                 #array
    #                 a = cv2.imwrite("/home/riya/newdjango/cvitsearch/media/tmp/"+str(img.split("/")[-1]),img_written)
                    
    #     image_data.append("/media/tmp/"+img.split("/")[-1])
    #     contents.append(c) 

    # # #testing end
    # page = request.GET.get('page',1)
    # paginator = Paginator(contents, 1)
    # paginator2 = Paginator(image_data,1)
    # try:
    #     contents = paginator.page(page)
    #     image_data = paginator2.page(page)
    # except PageNotAnInteger:
    #     contents = paginator.page(1)
    #     image_data = paginator2.page(1)
    # except EmptyPage:
    #     contents = paginator.page(paginator.num_pages)
    #     image_data = paginator2.page(paginator2.num_pages)

    # context["content"] = contents
    # context["page_image"] = image_data
    return render(request, 'home/line_segment.jinja2', context)