from django.urls import path
from . import views

urlpatterns = [
    path('destinatarios/', views.obtener_destinatarios, name='obtener_destinatarios'),
    path('destinatarios_observaciones/<int:proyecto_id>/', views.obtener_destinatarios_observaciones, name='destinatarios_observaciones'),
    #path('recibir_compromisos/', views.recibir_compromisos, name='recibir_compromisos'),
    path('post_cloud_project_id/', views.obtener_destinatarios, name='set_cloud_project_id'),
]