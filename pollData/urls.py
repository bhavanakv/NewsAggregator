from django.urls import path
from pollData import views

urlpatterns = [
    path('world/', views.index, name ='index'),
    path('getData/', views.getScrapeData, name = 'getScrapeData'), # URL for fetching data
    path('', views.addScrapeData, name = "addScrapeData"), # URL for adding data to DB
    path('lastRunTime/', views.getLastRunTime, name = "getLastRunTime") # URL for fetching last runtime
]