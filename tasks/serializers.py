from rest_framework import serializers
from .models import Client, Calendar, Declaration, Rut


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

class DeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Declaration
        fields = [
                "client",
                "id",
                "nit",
                "primary_economic_activity",
                "previus_year_anticipation",
                "next_year_anticipation",
                "liquid_heritage",
                "liquid_income",
                "net_income_tax",
                "anual_auditory_benefits",
                "semestrals_auditory_benefits",
                "unearned_income",
                "uvt",
                "date",
                ]
class RutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rut
        fields = [
                "client",
                "nit",
                "primary_economic_activity",
                "secondary_economic_activity",
                "date",
                ]