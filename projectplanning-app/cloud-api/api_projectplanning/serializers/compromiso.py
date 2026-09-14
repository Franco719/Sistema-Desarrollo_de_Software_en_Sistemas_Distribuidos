from rest_framework import serializers
from api_projectplanning.models.compromiso import Compromiso
from api_projectplanning.models.etapa import Etapa
from datetime import date


class CompromisoSerializer(serializers.ModelSerializer):
    etapa_back_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Compromiso
        fields = [
            'ong_coolaboradora_id',
            'etapa_back',       # read-only
            'etapa_back_id',    # viene en JSON
            'aporte',
            'nombre_ong_coolaboradora',
            'cantidad',
            'cumplido'
        ]
        extra_kwargs = {
            'etapa_back': {'read_only': True}
        }

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad del aporte debe ser mayor a 0")
        return value

    def validate(self, attrs):
        etapa_id = attrs.get("etapa_back_id")

        if etapa_id is None:
            raise serializers.ValidationError({"etapa_back_id": "Este campo es obligatorio"})

        try:
            etapa = Etapa.objects.get(pk=etapa_id)
        except Etapa.DoesNotExist:
            raise serializers.ValidationError({"etapa_back_id": "La etapa no existe"})

        # guardás el objeto
        attrs["etapa_back"] = etapa

        return attrs

    def create(self, validated_data):
        validated_data.pop("etapa_back_id")  # eliminar porque no pertenece al modelo
        validated_data["fecha_compromiso"] = date.today()
        return super().create(validated_data)




class CumplidoSerializer(serializers.Serializer):
    id_compromiso = serializers.IntegerField()
    cumplido = serializers.BooleanField()