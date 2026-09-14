from rest_framework import serializers
from api_projectplanning.models.etapa import Etapa
from api_projectplanning.models.proyecto import Project
from datetime import datetime

class EtapaSerializer(serializers.ModelSerializer):
    proyecto_back_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Etapa
        fields = [
            'nombre',
            'aporte_necesario',
            'cantidad',
            'etapa_back_id',
            'proyecto_back_id',   # <-- JSON lo manda
            'proyecto_back',      # <-- Lo usamos internamente
            'fecha_inicio',
            'fecha_fin'
        ]
        extra_kwargs = {
            'proyecto_back': {'read_only': True}  # No viene en el JSON
        }

        
    def validate(self, data):
        fecha_inicio = data.get("fecha_inicio")
        fecha_fin = data.get("fecha_fin")

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha_fin no puede ser anterior a fecha_inicio"}
            )
        return data
    
    
    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad del aporte debe ser mayor a 0")
        return value
    
    
    def create(self, validated_data):
        proyecto_id = validated_data.pop('proyecto_back_id')

        try:
            proyecto = Project.objects.get(proyecto_back_id=proyecto_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError(
                {"proyecto_back_id": "El proyecto no existe."}
            )

        validated_data['proyecto_back'] = proyecto
        return super().create(validated_data)

    

