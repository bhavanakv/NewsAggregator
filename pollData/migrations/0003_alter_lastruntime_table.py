# Generated by Django 4.1.1 on 2022-09-27 20:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pollData', '0002_newsblog_scrapeddata_alter_lastruntime_options'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='lastruntime',
            table='LastRunTime',
        ),
    ]
