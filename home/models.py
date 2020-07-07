from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from zipfile import ZipFile
import os
import shutil
from fpdf import FPDF
from django.core.files import File
# Create your models here.
import cv2

class Book(models.Model):
    title = models.CharField(max_length=200,default="")
    author = models.CharField(max_length=200,default="")
    isbn = models.CharField(max_length=20, blank=True)
    numpages = models.CharField(max_length=20,default="")
    # publisher = models.CharField(max_length=200, blank=True)
    # editor = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=20, blank=True)
    thumbnail = models.ImageField(upload_to='media/', blank=True)
    genre = models.CharField(max_length=200,blank=True)
    source = models.CharField(max_length=200,blank=True)
    book_pdf = models.FileField(upload_to="book_pdf",blank=True)
    book_content=models.FileField(upload_to='book_page_content',blank=True)
    book_segment=models.FileField(upload_to='book_segment',blank=True)
    
    # open_books = models.FileField(upload_to="pdfs",blank=True)
    # book_zip=models.FileField(upload_to="book_page_images",blank=True)

    def __repr__(self):
        return '<Book: {} ({})>'.format(self.title, self.id)

    def __str__(self):
        return '<Book: {} ({})>'.format(self.title, self.id)

@receiver(post_save, sender=Book)
def convert_zipimages_pdf(sender, instance, **kwargs):
    with ZipFile(instance.book_pdf.path, 'r') as zp:
        names=zp.namelist()
        foldername=names[0]
        del names[0]
        name_book = []
        for i in names:
            #i = i.split("_")[0].split("/")[-1]
            #name_book.append(i)
            i = i.split("/")[-1].split(".")[0].split("_")
            i = '_'.join(i[0:2])

        a=instance.book_pdf.path.split('/')
        del a[-1]
        a='/'.join(a)
        # print(os.getcwd())
        if 'media/book_pdf' not in os.getcwd():
            os.chdir('media/book_pdf')
        zp.extractall(a)
        for image in names:
            pt=image.split('/')[-1].split('.')[0]
            p=Page(pagetitle=pt,book=instance,content='')
            p.image.save(image,File(open(image,'rb')))
            p.save()
        #os.remove(instance.book_pdf.path)
        shutil.rmtree('/'.join(instance.book_pdf.path.split('/')[:-1])+'/'+foldername)
  

    with ZipFile(instance.book_content.path,'r') as zp:
        names=zp.namelist()
        foldername=names[0]
        del names[0]
        # for i in names:
        #     print(i)
        a=instance.book_pdf.path.split('/')
        del a[-1]
        a='/'.join(a)
        print(os.getcwd())
        if 'media/book_pdf' not in os.getcwd():
            os.chdir('media/book_pdf')
        zp.extractall(a)
        for image in names:
            print(image)
            pt=image.split('/')[-1].split('.')[0]
            if (len(pt.split('_'))>2):
                pt='_'.join(pt.split('_')[0:])
            p=Page.objects.filter(pagetitle=pt).first()
            with open(image, 'r') as f:
                r = f.readlines()
            r=[i.strip() for i in r]
            p.content='\n'.join(r)
            p.save()
        #os.remove(instance.book_content.path))
        shutil.rmtree('/'.join(instance.book_pdf.path.split('/')[:-1])+'/'+foldername)

    with ZipFile(instance.book_segment.path,'r') as zp:
        names=zp.namelist()
        foldername=names[0]
        del names[0]
        # for i in names:
        #     print(i)
        a=instance.book_pdf.path.split('/')
        del a[-1]
        a='/'.join(a)
        print(os.getcwd())
        if 'media/book_pdf' not in os.getcwd():
            os.chdir('media/book_pdf')
        zp.extractall(a)
        for image in names:
            # print(images)
            pt=image.split('/')[-1].split('.')[0]
            if (len(pt.split('_'))>2):
                pt='_'.join(pt.split('_')[0:])
            p=Page.objects.filter(pagetitle=pt).first()
            with open(image, 'r') as f:
                r = f.readlines()
            r=[i.strip() for i in r]
            p.segment='\n'.join(r)
            p.save()
        #os.remove(instance.book_segment.path)
        shutil.rmtree('/'.join(instance.book_pdf.path.split('/')[:-1])+'/'+foldername)



class Page(models.Model):
    # pagetitle stores the name of the text file from which the body contents come from.
    pagetitle = models.CharField(max_length=100, default='')
    book = models.ForeignKey("Book", on_delete=models.CASCADE, related_name='pages')
    content = models.TextField()
    segment = models.TextField()
    image= models.ImageField(upload_to='page_images/', null=True, default=None, blank=True)

    def __str__(self):
        return '<Page: {} ({})'.format(self.pagetitle, self.book.title)


class Announcement(models.Model):
    ann_title = models.CharField(max_length=100,default="")
    description = models.TextField(default="")
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return '<Announcement: {} ({})'.format(self.ann_title,self.active)
