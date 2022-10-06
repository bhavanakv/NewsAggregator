# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Lastruntime(models.Model):
    id = models.IntegerField(primary_key=True)
    lastscrapedtime = models.DateTimeField(db_column='scrapeTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'LastRunTime'


class Newsblog(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NewsBlog'


class Scrapeddata(models.Model):
    id = models.IntegerField(primary_key=True)
    headline = models.TextField()
    description = models.TextField(blank=True, null=True)
    written_by = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    blog = models.ForeignKey(Newsblog, on_delete=models.SET_NULL, null=True)

    class Meta:
        managed = False
        db_table = 'ScrapedData'
