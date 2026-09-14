from django.urls import path
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Project Planning",
        default_version='v1',
        description="Documentación de la API de proyectos, etapas y compromisos",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(), 
)

urlpatterns = [
    path('authenticate', views.authenticate_user, name="authenticate"),
    path('prueba', views.prueba, name="prueba"),
    path('save_etapa', views.save_etapa, name="save_etapa"),
    path('save_proyecto', views.save_proyecto, name="save_proyecto"),
    path('save_compromiso', views.save_compromiso, name="save_compromiso"),
    path('mark_cumplido_fulfilled', views.mark_cumplido_fulfilled, name="mark_cumplido_fulfilled"),
    path('get_commitments_by_project_id', views.get_commitments_by_project_id, name="get_commitments_by_project_id"),

    
    # Swagger UI:
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # Opcional: documentación en JSON
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
