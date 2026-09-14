#!/usr/bin/env python
"""
Script para listar TODOS los procesos en Bonita (habilitados y deshabilitados)
"""
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.api.bonita import get_bonita_api

def list_all_processes():
    print("🔍 LISTANDO TODOS LOS PROCESOS EN BONITA")
    print("=" * 50)
    
    api = get_bonita_api()
    
    if not api.authenticated:
        print("❌ No autenticado")
        return
    
    # Listar procesos habilitados
    print("\n📋 PROCESOS HABILITADOS:")
    response = api.do_request("GET", "/API/bpm/process?f=activationState=ENABLED&p=0&c=20")
    if response:
        if len(response) == 0:
            print("  ❌ No hay procesos habilitados")
        else:
            for i, proc in enumerate(response, 1):
                print(f"  {i}. {proc.get('name', 'Sin nombre')} (v{proc.get('version', 'N/A')})")
                print(f"     ID: {proc.get('id', 'N/A')}")
                print(f"     Estado: {proc.get('activationState', 'N/A')}")
                print()
    
    # Listar TODOS los procesos (incluidos deshabilitados)
    print("\n📋 TODOS LOS PROCESOS (incluidos deshabilitados):")
    response = api.do_request("GET", "/API/bpm/process?p=0&c=20")
    if response:
        if len(response) == 0:
            print("  ❌ No hay procesos en absoluto")
        else:
            for i, proc in enumerate(response, 1):
                print(f"  {i}. {proc.get('name', 'Sin nombre')} (v{proc.get('version', 'N/A')})")
                print(f"     ID: {proc.get('id', 'N/A')}")
                print(f"     Estado: {proc.get('activationState', 'N/A')}")
                print()
    
    # Sugerencia
    print("\n💡 SUGERENCIAS:")
    print("1. Si no hay procesos, necesitas:")
    print("   - Abrir Bonita Studio")
    print("   - Crear/importar un proceso BPMN")
    print("   - Desplegarlo en el servidor")
    print()
    print("2. Si hay procesos DISABLED, puedes habilitarlos desde Bonita Portal")
    print()
    print("3. Para testing rápido, puedes cambiar el nombre en tu código")
    print("   de 'Project-Planning' al nombre de un proceso existente")

if __name__ == "__main__":
    list_all_processes()