import datetime
import json
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import jwt
from django.contrib.auth import authenticate
from api_core.settings import SECRET_KEY
from api_projectplanning.decorators import require_jwt
from api_projectplanning.serializers.etapa import EtapaSerializer
from api_projectplanning.serializers.proyecto import ProyectoSerializer
from api_projectplanning.serializers.compromiso import CompromisoSerializer, CumplidoSerializer
from api_projectplanning.models.compromiso import Compromiso
from api_projectplanning.models.proyecto import Project
from api_projectplanning.models.etapa import Etapa
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Create your views here.
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={
        200: "Token generado correctamente",
        401: "Credenciales inválidas",
        400: "Solicitud incorrecta"
    }
)
@api_view(['POST'])
@csrf_exempt
def authenticate_user(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Faltan credenciales'}, status=400)

        # Valida contra la tabla User de Django
        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse({'error': 'Credenciales inválidas'}, status=401)

        # Si es válido → generar el token
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            'id': user.id,
            'username': user.username,
            'exp': now + datetime.timedelta(hours=2),
            'iat': now
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return JsonResponse({
            'token': f'Bearer {token}',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_jwt
def prueba(request):
    return JsonResponse({'data': 'joya'}, status=200)


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            in_=openapi.IN_HEADER,
            description="Token JWT. Formato: Bearer <token>",
            type=openapi.TYPE_STRING
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(      
            type=openapi.TYPE_OBJECT,
            required=[
                'nombre',
                'aporte_necesario',
                'cantidad',
                'etapa_back_id',
                'proyecto_back',
                'fecha_inicio',
                'fecha_fin'
            ],
            properties={
                'nombre': openapi.Schema(type=openapi.TYPE_STRING),
                'aporte_necesario': openapi.Schema(type=openapi.TYPE_STRING),
                'cantidad': openapi.Schema(type=openapi.TYPE_INTEGER),
                'etapa_back_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'proyecto_back': openapi.Schema(type=openapi.TYPE_INTEGER),
                'fecha_inicio': openapi.Schema(type=openapi.TYPE_STRING, format="date"),
                'fecha_fin': openapi.Schema(type=openapi.TYPE_STRING, format="date"),
            }
        )
    ),
    responses={201: "Etapas guardadas", 400: "Datos inválidos"}
)

@api_view(['POST'])
@csrf_exempt
@require_jwt
def save_etapa(request): 
    try: 
        payload = json.loads(request.body) 
    except json.JSONDecodeError: 
        return JsonResponse({"error": "JSON inválido"}, status=400) 
    
    serializer = EtapaSerializer(data=payload, many=True)
 
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse({"mensaje": "Etapas guardadas"}, status=201)
    except Exception as e:
        return JsonResponse({"errores": serializer.errors}, status=400)

    """
    [
        {
            "nombre": "Recolección de materiales",
            "aporte_necesario": "Madera, clavos y pintura",
            "cantidad": 50,
            "etapa_back_id": 1,
            "proyecto_back_id": 123,
            "fecha_inicio": "2025-01-10",
            "fecha_fin": "2025-02-15"
        },
        {
            "nombre": "Construcción inicial",
            "aporte_necesario": "Herramientas y mano de obra",
            "cantidad": 20,
            "etapa_back_id": 2,
            "proyecto_back_id": 123,
            "fecha_inicio": "2025-02-16",
            "fecha_fin": "2025-03-10"
        }
    ]
    """



@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['nombre', 'ong_responsable', 'id_back_ong', 'fecha_inicio', 'fecha_fin', 'case_id'],
        properties={
            'nombre': openapi.Schema(type=openapi.TYPE_STRING),
            'ong_responsable': openapi.Schema(type=openapi.TYPE_STRING),
            'id_back_ong': openapi.Schema(type=openapi.TYPE_STRING),
            'fecha_inicio': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
            'fecha_fin': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
            'case_id': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={201: "Proyecto creado correctamente"}
)
@api_view(['POST'])
@csrf_exempt
@require_jwt
def save_proyecto(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    
    serializer = ProyectoSerializer(data=payload)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({"mensaje": "Proyecto guardado"}, status=201)
    else:
        return JsonResponse(serializer.errors, status=400)
    """{
        "nombre": "Plan de Reforestación",
        "ong_responsable": "EcoVida",
        "ong_back_id": "123",
        "proyecto_back_id": "123",
        "fecha_inicio": "2025-10-20",
        "fecha_fin": "2025-12-31",
        "case_id": "123"
    }
    """
    
    
@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            in_=openapi.IN_HEADER,
            description="Token JWT. Formato: Bearer <token>",
            type=openapi.TYPE_STRING
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=[
            'ong_coolaboradora_id',
            'etapa_back_id',
            'aporte',
            'nombre_ong_coolaboradora',
            'cantidad'
        ],
        properties={
            'ong_coolaboradora_id': openapi.Schema(type=openapi.TYPE_STRING),
            'etapa_back_id': openapi.Schema(type=openapi.TYPE_STRING),
            'aporte': openapi.Schema(type=openapi.TYPE_STRING),
            'nombre_ong_coolaboradora': openapi.Schema(type=openapi.TYPE_STRING),
            'cantidad': openapi.Schema(type=openapi.TYPE_INTEGER),
            'cumplido': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        }
    ),
    responses={201: "Compromiso guardado", 400: "Datos inválidos"}
)
@api_view(['POST'])
@csrf_exempt
@require_jwt
def save_compromiso(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    serializer = CompromisoSerializer(
        data=payload,
        many=isinstance(payload, list)
    )
    
    try:
        serializer.is_valid(raise_exception=True)
        # Habra que verificar aca que el compromiso no es necesario? Es decir, si preciso 40 voluntarios
        # por ejemplo, y ya lo tengo, y me llega otro compromiso, debería bocharlo o ya se controla desde el back?
        compromisos = serializer.save()

        # Si son varios compromisos, devolvés una lista
        if isinstance(compromisos, list):
            respuesta = [
                {"compromiso_id": c.id, "etapa_id": c.etapa_back.etapa_back_id, "mensaje": "Compromiso guardado"}
                for c in compromisos
            ]
            return JsonResponse(respuesta, safe=False, status=201)

        return JsonResponse(
            {"compromiso_id": compromisos.id},
            status=201
        )

    except Exception:
        return JsonResponse({"errores": serializer.errors}, status=400)
    """
    [
        {
            "ong_coolaboradora_id": 4,
            "etapa_back_id": 1,
            "aporte": "Herramientas",
            "nombre_ong_coolaboradora": "Fundación X",
            "cantidad": 10,
            "cumplido": false
        },
        {
            "ong_coolaboradora_id": 4,
            "etapa_back_id": 1,
            "aporte": "Mano de Obra",
            "nombre_ong_coolaboradora": "Fundación X",
            "cantidad": 10,
            "cumplido": false
        }
    ]
    """
    

@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            in_=openapi.IN_HEADER,
            description="Token JWT. Formato: Bearer <token>",
            type=openapi.TYPE_STRING
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id_compromiso', 'cumplido'],
        properties={
            'id_compromiso': openapi.Schema(type=openapi.TYPE_INTEGER),
            'cumplido': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        }
    ),
    responses={200: "Estado actualizado", 404: "Compromiso no encontrado"}
)
@api_view(['POST'])
@csrf_exempt
@require_jwt
def mark_cumplido_fulfilled(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    
    serializer = CumplidoSerializer(data=payload)
    if serializer.is_valid():
        id_compromiso = serializer.validated_data["id_compromiso"]
        cumplido = serializer.validated_data["cumplido"]

        try:
            compromiso = Compromiso.objects.get(id=id_compromiso)
        except Compromiso.DoesNotExist:
            return JsonResponse({"error": "Compromiso no encontrado"}, status=404)

        compromiso.cumplido = cumplido
        compromiso.save()
        return JsonResponse({"mensaje": "Estado de compromiso actualizado correctamente"}, status=200)

    return JsonResponse(serializer.errors, status=400)
    """
    {
    "id_compromiso": 1,
    "cumplido": true
    }
    """
  
  
@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'Authorization', openapi.IN_HEADER,
            description="Bearer token (formato: Bearer <token>)",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'proyecto_back_id',
            openapi.IN_QUERY,
            description="ID del proyecto en el backend",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(description="Lista de compromisos"),
        400: "proyecto_back_id faltante",
        401: "No autorizado"
    }
)
@api_view(['GET'])
@csrf_exempt
@require_jwt
def get_commitments_by_project_id(request):
    proyecto_back_id = request.GET.get('proyecto_back_id')
    if not proyecto_back_id:
        return JsonResponse({"error": "Falta proyecto_back_id"}, status=400)

    try:
        compromisos = Compromiso.objects.filter(
            etapa_back__proyecto_back__proyecto_back_id=proyecto_back_id
        )

        if not compromisos.exists():
            return JsonResponse(
                {"compromisos": [], "aviso": "No hay compromisos para este proyecto"},
                status=200
            )

        data = [
            {
                "id": compromiso.id,
                "nombre_ong": compromiso.nombre_ong_coolaboradora,
                "aporte": compromiso.aporte,
                "cantidad": compromiso.cantidad,
                "cumplido": compromiso.cumplido,
            }
            for compromiso in compromisos
        ]

        return JsonResponse(
            {"compromisos": data, "aviso": "Se encontraron compromisos"}, status=200
        )

    except Exception as e:
        return JsonResponse(
            {"error": f"Error al obtener compromisos: {str(e)}"}, status=500
        ) 
    """
    http://127.0.0.1:8000/api/v1/get_commitments_by_project_id?id_proyecto_back=numero
    {
    "id_proyecto_back": "1"
    }
    """
    