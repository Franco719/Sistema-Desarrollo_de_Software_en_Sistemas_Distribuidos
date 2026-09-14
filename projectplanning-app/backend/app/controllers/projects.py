from django.db import models
from datetime import datetime

from app.models.etapa import Etapa
from app.models.project import Project


def save_project(data) -> Project:
    project = Project(
        nombre=data['nombre'],        
        ong_responsable=data['ong_responsable'],
        fecha_inicio=data['fecha_inicio'],
        fecha_fin=data['fecha_fin'],
        plan_economico=data['plan_economico'],
        case_id=None,
    )
    project.save()
        
    return project


def save_etapas(data, project) -> list:
    etapas_creadas = []
    for nombre_etapa, info_etapa in data['etapas'].items():
        # Convertir string de ayuda a booleano
        requiere_ayuda = info_etapa['ayuda'].lower() == 'true'
        
        etapa = Etapa.objects.create(
            proyecto=project,
            nombre_etapa=nombre_etapa,  # La clave del diccionario es el nombre
            nombre_aporte=info_etapa['aporte'],
            cant_aporte_necesario=int(info_etapa['cantidad']),
            cant_aporte_actual=0,
            fecha_inicio=info_etapa['inicio'],
            fecha_fin=info_etapa['fin'], 
            requiere_ayuda=bool(requiere_ayuda)  # Convertir string a booleano
        )
        
        etapas_creadas.append(etapa)
        
    return etapas_creadas
    