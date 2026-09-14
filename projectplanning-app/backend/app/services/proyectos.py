import json
from django.db import transaction
from app.api.bonita import get_bonita_api
from app.models.etapa import Etapa
from app.models.project import Project
from django.contrib.auth.models import User
import datetime
from django.db.models import F


class ProyectosServiceError(Exception):
    pass


def process_offers(project, seleccionadas, post_data, user=None):
    """Procesa las ofertas de ayuda (aportes) para un proyecto.

    Args:
        project: instancia de Project
        seleccionadas: lista de ids (strings) de etapas seleccionadas
        post_data: request.POST (Mapping) con los campos enviados
        user: usuario que realiza la acción (opcional)

    Returns:
        dict con keys: 'aportes' (list) y 'case_id' (str)

    Lanza ProyectosServiceError en caso de problemas predecibles.
    """
    if not seleccionadas:
        raise ProyectosServiceError('No se enviaron aportes.')

    case_id = getattr(project, 'case_id', None)
    if not case_id:
        raise ProyectosServiceError('El proyecto no tiene un case_id asociado en Bonita.')    

    aportes = []

    # Usamos una transacción para asegurar consistencia en decrementos
    with transaction.atomic():
        # Agregar al usuario como colaborador si aún no lo es
        if user and user.is_authenticated:
            # Verificar que no sea el originante
            owner_id_str = str(project.ong_responsable)
            if str(user.id) != owner_id_str:
                # Agregar como colaborador si no está ya
                if not project.ongs_colaboradoras.filter(id=user.id).exists():
                    project.ongs_colaboradoras.add(user)
        
        for etapa in project.etapas.all():
            eid = str(etapa.id)
            if eid in seleccionadas:
                if not etapa.requiere_ayuda:
                    raise ProyectosServiceError(f'La etapa "{etapa.nombre_aporte}" no está solicitando ayuda.')

                aporte_text =  etapa.nombre_aporte #post_data.get(f'aporte_{eid}', '').strip()
                cantidad_raw = post_data.get(f'cantidad_{eid}', '').strip()

                try:
                    cantidad = int(cantidad_raw) if cantidad_raw != '' else None
                except (ValueError, TypeError):
                    raise ProyectosServiceError(f'Cantidad inválida para la etapa "{etapa.nombre_aporte}".')
                
                if cantidad is None or cantidad <= 0:
                    raise ProyectosServiceError(f'Debe indicar una cantidad válida para la etapa "{etapa.nombre_aporte}".')

                etapa_locked = Etapa.objects.select_for_update().get(pk=etapa.id)
                if cantidad + etapa_locked.cant_aporte_actual > etapa_locked.cant_aporte_necesario:
                    raise ProyectosServiceError(f'La cantidad aportada excede la solicitada para el aporte "{etapa.nombre_aporte}". Se necesita la siguiente cantidad de aporte: {etapa_locked.cant_aporte_necesario - etapa_locked.cant_aporte_actual}.')  
               
                etapa_locked.cant_aporte_actual =etapa_locked.cant_aporte_actual + cantidad
                etapa_locked.save()
                
                aportes.append({
                    'ong_coolaboradora_id': user.id,
                    'etapa_back_id': etapa_locked.id,
                    'aporte': aporte_text,
                    'nombre_ong_coolaboradora': user.first_name,
                    'cantidad': cantidad,
                    'cumplido': False,
                })
                
                print("Termine la transaccion")

        # Chequeo de todas las etapas cubiertas
        etapas_proyecto = Etapa.objects.filter(proyecto__case_id=case_id, requiere_ayuda=True)
        todas_etapas_cubiertas = not etapas_proyecto.exclude(cant_aporte_actual__gte=F('cant_aporte_necesario')).exists()
        
        if todas_etapas_cubiertas:
            project.estado = Project.ESTADO_CUBIERTO
            project.save()
        
        # Enviar las variables a Bonita
        payload = {
            "compromisos": aportes,
            "plan_trabajo_completo": todas_etapas_cubiertas
        }
        api = get_bonita_api("walter.bates", "bpm")
        activity = api.search_activity_by_case_id(case_id)
        if activity:
            print(f"Actividad encontrada: {activity}")
            # Asigna la tarea a un usuario
            bates = api.get_user_id_by_username("walter.bates")
            api.assign_task(activity, bates)
            # Intentar ejecutar la tarea
            executed = api.execute_user_task(activity, payload)
            print(f"Tarea ejecutada: {executed}")
        else:
            print("No se encontraron actividades pendientes (esto puede ser normal)")

    return {'aportes': aportes, 'case_id': case_id}
