from rest_framework import serializers
from .models import Client, Calendar


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = [
                "id",
                "cc",
                "nit",
                "name",
                "address",
                "telephone",
                "mail",
                "user",
                "notes",
                "fiscal_responsibilities"
                ]

class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = [
                "id",
                "digits",
                "date",
                ]