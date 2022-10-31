from django.urls import path
from pollData import views

urlpatterns = [
    path('world/', views.index, name ='index'),
    path('<int:pk>/', views.getScrapeData, name = 'getScrapeData'),
    path('', views.addScrapeData, name="addScrapeData")
]