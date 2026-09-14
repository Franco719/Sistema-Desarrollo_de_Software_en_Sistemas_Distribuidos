#!/usr/bin/env python
"""
Script de diagnóstico para Bonita API
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.api.bonita import get_bonita_api

def test_bonita_connection():
    print("=" * 50)
    print("DIAGNÓSTICO DE BONITA API")
    print("=" * 50)
    
    # 1. Verificar variables de entorno
    print("\n1. VERIFICANDO VARIABLES DE ENTORNO:")
    bonita_url = os.getenv('BONITA_URL')
    bonita_user = os.getenv('BONITA_USER')
    bonita_psw = os.getenv('BONITA_PSW')
    
    print(f"BONITA_URL: {bonita_url or 'NO CONFIGURADA'}")
    print(f"BONITA_USER: {bonita_user or 'NO CONFIGURADA'}")
    print(f"BONITA_PSW: {'***' if bonita_psw else 'NO CONFIGURADA'}")
    
    if not all([bonita_url, bonita_user, bonita_psw]):
        print("\n❌ ERROR: Variables de entorno no configuradas")
        print("\nCrea un archivo .env con:")
        print("BONITA_URL=http://localhost:8080/bonita")
        print("BONITA_USER=walter.bates")
        print("BONITA_PSW=bpm")
        return
    
    # 2. Probar conexión y login
    print("\n2. PROBANDO CONEXIÓN Y LOGIN:")
    try:
        api = get_bonita_api()
        print(f"Autenticado: {api.authenticated}")
        print(f"API Token: {'***' if api.api_token else 'No disponible'}")
        
        if not api.authenticated:
            print("❌ ERROR: No se pudo autenticar")
            return
        
    except Exception as e:
        print(f"❌ ERROR en conexión: {e}")
        return
    
    # 3. Buscar proceso Project-Planning
    print("\n3. BUSCANDO PROCESO 'Project-Planning':")
    try:
        process_id = api.get_process_id("Project-Planning")
        print(f"Process ID: {process_id}")
        
        if not process_id:
            print("❌ ERROR: Proceso 'Project-Planning' no encontrado")
            
            # Listar todos los procesos disponibles
            print("\n📋 PROCESOS DISPONIBLES:")
            try:
                processes = api.get_processes()
                if processes:
                    for proc in processes[:5]:  # Mostrar solo los primeros 5
                        print(f"  - {proc.get('name', 'Sin nombre')} (ID: {proc.get('id', 'N/A')})")
                else:
                    print("  No se pudieron obtener los procesos")
            except Exception as e:
                print(f"  Error obteniendo procesos: {e}")
            return
        
    except Exception as e:
        print(f"❌ ERROR buscando proceso: {e}")
        return
    
    # 4. Probar instanciación
    print("\n4. PROBANDO INSTANCIACIÓN:")
    try:
        case_id = api.initiate_project_by_id(process_id)
        print(f"Case ID: {case_id}")
        
        if case_id:
            print("✅ ÉXITO: Proceso instanciado correctamente")
            
            # 5. Buscar actividades
            print("\n5. BUSCANDO ACTIVIDADES:")
            activity = api.search_activity_by_case_id(case_id)
            if activity:
                print(f"Actividad encontrada: {activity.get('name', 'Sin nombre')} (ID: {activity.get('id', 'N/A')})")
            else:
                print("ℹ️  No hay actividades pendientes (esto puede ser normal)")
                
        else:
            print("❌ ERROR: No se pudo instanciar el proceso")
            
    except Exception as e:
        print(f"❌ ERROR en instanciación: {e}")
    
    print("\n" + "=" * 50)
    print("DIAGNÓSTICO COMPLETADO")
    print("=" * 50)

if __name__ == "__main__":
    test_bonita_connection()