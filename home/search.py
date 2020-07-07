from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections
from django_elasticsearch_dsl import DocType, Index, fields
from elasticsearch.helpers import bulk
#from . import models
from home.models import Book, Page

books = Index('books')
pages = Index('pages')

#connections.create_connection()  #create the connection of the search engine

@books.doc_type
class BookIndex(DocType):

	class Meta:
		model=Book
		fields=['id','author','title','isbn','source']

@pages.doc_type
class PageIndex(DocType):
	class Meta:
		model=Page
		fields=['id','content']