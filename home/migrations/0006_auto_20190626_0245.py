# Generated by Django 2.1.7 on 2019-06-25 21:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_book_page'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='page',
            new_name='bookid',
        ),
    ]