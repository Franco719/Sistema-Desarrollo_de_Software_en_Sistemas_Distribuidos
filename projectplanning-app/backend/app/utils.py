from datetime import datetime

def procesar_etapas(request):
    etapas_dict = {}
    
    for key, value in request.POST.items():
        print(f"Procesando etapas: key {key}, value {value}")
        if key.startswith('etapas['):
            parts = key[7:-1].split('][')
            if len(parts) == 2:
                nombre_etapa, campo = parts
                
                if nombre_etapa not in etapas_dict:
                    etapas_dict[nombre_etapa] = {}
                
                etapas_dict[nombre_etapa][campo] = value
    
    return etapas_dict


def verificar_etapas(data):
    mensajes = []
    for nombre_etapa, info_etapa in data['etapas'].items():
        inicio_etapa = datetime.strptime(info_etapa["inicio"], "%Y-%m-%d").date()
        fin_etapa = datetime.strptime(info_etapa["fin"], "%Y-%m-%d").date()
        inicio_proyecto = datetime.strptime(data["fecha_inicio"], "%Y-%m-%d").date()
        fin_proyecto = datetime.strptime(data["fecha_fin"], "%Y-%m-%d").date()
        
        if inicio_etapa > fin_etapa:
            mensajes.append(f"La fecha de inicio de la Etapa {nombre_etapa} es superior a la fecha de fin de la misma Etapa")
        
        if inicio_etapa < inicio_proyecto:
            mensajes.append(f"La fecha de inicio de la Etapa {nombre_etapa} es anterior a la fecha de inicio del Proyecto")
        
        if fin_etapa > fin_proyecto:
            mensajes.append(f"La fecha de fin de la Etapa {nombre_etapa} es superior a la fecha de fin del Proyecto")
        
        if int(info_etapa['cantidad']) <= 0:
            mensajes.append(f"La cantidad del aporte {int(info_etapa['cantidad'])} para la Etapa {nombre_etapa} debe ser mayor a 0")

    return mensajes
    
    """
    nombre_etapa = models.CharField(max_length=255)
    nombre_aporte = models.CharField(max_length=255)
    cant_aporte_necesario = models.IntegerField()
    cant_aporte_actual = models.IntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    requiere_ayuda = models.BooleanField(default=False)
    proyecto = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='etapas'
    )
    """

def verificar_proyecto(proyecto):
    inicio_proyecto = datetime.strptime(proyecto["fecha_inicio"], "%Y-%m-%d").date()
    fin_proyecto = datetime.strptime(proyecto["fecha_fin"], "%Y-%m-%d").date()
    
    if inicio_proyecto > fin_proyecto:
        return f"La fecha de inicio del proyecto debe ser anterior a la de fin del mismo proyecto"
    else:
        return None


def obtain_cloud_token(force_refresh: bool = False) -> str:
    """Obtener un JWT/Bearer token desde el Cloud API y cachearlo.

    - Lee las variables de entorno: CLOUD_API_URL (opcional),
      CLOUD_API_TOKEN_URL (opcional), CLOUD_API_USER, CLOUD_API_PASSWORD.
    - Cachea el token usando el backend de cache de Django con una TTL
      basada en el campo `expires_in` si el endpoint lo devuelve.
    - Si force_refresh=True se fuerza la obtención de uno nuevo.

    Lanza RuntimeError si faltan variables o si la petición falla.
    """
    from os import getenv
    import requests
    from django.core.cache import cache #cache simple, lo mejor seria usar Redis o similar

    CLOUD_API_URL = getenv('CLOUD_API_URL')
    token_url = getenv('CLOUD_API_TOKEN_URL') or (CLOUD_API_URL + 'authenticate' if CLOUD_API_URL else None)
    auth_user = getenv('BONITA_USER')
    auth_pass = getenv('BONITA_PSW')

    if not token_url or not auth_user or not auth_pass:
        raise RuntimeError('CLOUD_API_TOKEN_URL/CLOUD_API_USER/CLOUD_API_PASSWORD no configurados')

    cache_key = 'cloud_api_token'
    if not force_refresh:
        t = cache.get(cache_key)
        if t:
            return t

    resp = requests.post(token_url, json={'username': auth_user, 'password': auth_pass}, timeout=8)
    resp.raise_for_status()
    data = resp.json()
    t = data.get('access_token') or data.get('token') or data.get('accessToken')
    expires = data.get('expires_in') or data.get('expires')
    if not t:
        raise RuntimeError('No se obtuvo token del endpoint de autenticación')

    # calcular TTL razonable
    if expires:
        try:
            ttl = int(expires) - 5 if int(expires) > 10 else int(expires)
        except Exception:
            ttl = 60 * 60
    else:
        ttl = 60 * 60

    cache.set(cache_key, t, ttl)
    return t


def fetch_commitments_from_cloud(project_id, cloud_api_url: str | None = None, timeout: int = 10):
    """Fetch commitments for a project from the cloud API.

    - Uses `obtain_cloud_token` to get a bearer token (cached).
    - Retries once with a forced refresh if the API returns 401.
    - Returns parsed JSON (list/dict) or raises RuntimeError on failure.
    """
    from os import getenv
    import requests

    base = cloud_api_url or getenv('CLOUD_API_URL')
    if not base:
        raise RuntimeError('CLOUD_API_URL no está configurada')

    # endpoint used by the front-end service
    endpoint = getenv('CLOUD_API_URL') + 'get_commitments_by_project_id'

    # obtain token (cached inside obtain_cloud_token)
    token = obtain_cloud_token()
    headers = {'Authorization': f'{token}'}

    resp = requests.get(endpoint, params={'proyecto_back_id': project_id}, headers=headers, timeout=timeout)

    # if unauthorized, refresh token once and retry
    if resp.status_code == 401:
        token = obtain_cloud_token(force_refresh=True)
        headers = {'Authorization': f'{token}'}
        resp = requests.get(endpoint, params={'proyecto_back_id': project_id}, headers=headers, timeout=timeout)

    try:
        resp.raise_for_status()
    except Exception as e:
        body = getattr(resp, 'text', '')
        raise RuntimeError(f'Error fetching commitments: status={resp.status_code} body={body}') from e

    try:
        return resp.json()
    except ValueError as e:
        raise RuntimeError('Invalid JSON response from cloud API') from e