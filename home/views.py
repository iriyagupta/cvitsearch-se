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



class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

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
        elif para == 'title':
            a = BookIndex.search().query('match_phrase',title=q)
            ids = [i.id for i in a]
            context['results'] = Book.objects.filter(id__in=ids)
            total = context["results"].count()
        else:      # print(q)
            if '"' in q:
                print(q)
                # q.count('"') % 2 != 0:
                # print(q)
                a=PageIndex.search().query('match_phrase',content=q)
                page_ids=[i.id for i in a]
                print(page_ids)
                print("\n\n")
                context['results'] = Book.objects.filter(pages__id__in=page_ids).distinct()
                total = context["results"].count()
                print(total)
                context['page_list'] = Page.objects.filter(id__in=page_ids)
                print(context["page_list"])
                for i in context["page_list"]:
                    print(i)
                page_lines = {i:[] for i in page_ids}
                print(page_lines)
                page_lines2 = {i:[] for i in page_ids}
                print(page_lines2)
                context['page_lines'] = page_lines
            else:
                print("yay")
                words = q.split(" ")
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
                words=[i for i in words if i not in operators]
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
                    line_list = Page.objects.get(id=i).content.split('.')
                    for line in line_list:
                        l=line.lower()
                        cap= False
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
                # print(dictioni)
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