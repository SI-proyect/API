from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status

from .serializers import ClientSerializer, CalendarSerializer
from .models import Client, Calendar
from .utils.file_controller import set_to_media_folder, delete_from_media_folder
from .utils.calendar import CalendarExtractor
import os
from django.conf import settings

# Create your views here.
@api_view(["POST"])
def create_client(request) -> JsonResponse:

    serializer : ClientSerializer = ClientSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return JsonResponse(
                data={"message": "Client was created successfully."},
                status=status.HTTP_201_CREATED
                )

    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_clients(request) -> JsonResponse:

    clients = Client.objects.all()

    serializer = ClientSerializer(clients, many=True)

    return JsonResponse(data=serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(["GET"])
def get_client(request, cc) -> JsonResponse:

    try:

        client = Client.objects.get(cc=cc)

    except Client.DoesNotExist:
        return JsonResponse(data={"message": f"The client with CC {cc} does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

    client_serialized = ClientSerializer(client)
    return JsonResponse(data=client_serialized.data, status=status.HTTP_200_OK)

@api_view(["DELETE"])
def delete_client(request, cc):

    try:
        client = Client.objects.get(cc=cc)
    except Client.DoesNotExist:
        return JsonResponse(data={"message": f"The client with CC {cc} does not exist. Failed to delete client."},
                            status=status.HTTP_400_BAD_REQUEST)

    client.delete()

    return JsonResponse(data={"message": f"Client with CC {cc} deleted successfully."}, status=status.HTTP_200_OK)

@api_view(["POST"])
def set_calendar(request) -> JsonResponse:

    try:
        calendar = Calendar.objects.all()
        calendar.delete()
    except Calendar.DoesNotExist:
        pass

    document = request.FILES["file"]
    if not document:
        return JsonResponse(data={"message": "No file was uploaded."},
                            status=status.HTTP_400_BAD_REQUEST)

    document_name = document.name
    if not document_name.endswith('.pdf'):
        return JsonResponse(data={"message": "Invalid file format. Please upload a PDF file."},
                            status=status.HTTP_400_BAD_REQUEST)

    #set document to media folder
    file_path = set_to_media_folder(document)

    #extract calendar from pdf
    calendar = CalendarExtractor(file_path)
    calendar.calendar_extractor()
    if calendar.dates == []:
        delete_from_media_folder(file_path)
        return JsonResponse(data={"message": "No calendar was found in the PDF file."},
                            status=status.HTTP_400_BAD_REQUEST)
    data = calendar.transform_to_dict()

    errors = []

    #delete file from media folder
    delete_from_media_folder(file_path)

    for digits, date in data.items():
        entry = {
            'id': 0,
            'digits': digits,
            'date': date
        }
        serializer = CalendarSerializer(data=entry)
        if serializer.is_valid():
            serializer.save()
        else:
            errors.append(serializer.errors)

    if errors:
        return JsonResponse(errors, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse(data={"message": "Calendar was processed successfully."},
                        status=status.HTTP_201_CREATED)

@api_view(["GET"])
def get_calendar(request) -> JsonResponse:
    calendar = Calendar.objects.all()
    serializer = CalendarSerializer(calendar, many=True)

    return JsonResponse(data=serializer.data, status=status.HTTP_200_OK, safe=False)

@api_view(["GET"])
def get_client_alerts(request, cc) -> JsonResponse:
    try:
        client = Client.objects.get(cc=cc)
        calendar = Calendar.objects.all()
        if client:
            str_cc = str(cc)[-2:]

        for entry in calendar:
            if entry.digits < 10:
                entry.digits = f"0{entry.digits}"
            else:
                entry.digits = str(entry.digits)

            if str_cc in entry.digits:
                return JsonResponse(data={"message": f"Alert! Client has a declaration at {entry.date}."},
                                    status=status.HTTP_200_OK)


    except Client.DoesNotExist:
        return JsonResponse(data={"message": f"The client with CC {cc} does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)
