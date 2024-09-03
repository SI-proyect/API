from django.shortcuts import render
from django.http import JsonResponse
from geodesic.client import client
from rest_framework.decorators import api_view
from rest_framework import status

from .serializers import ClientSerializer, CalendarSerializer, DeclarationSerializer, RutSerializer
from .models import Client, Calendar, Declaration, Rut
from .utils.file_controller import set_to_media_folder, delete_from_media_folder
from .utils.calendar import CalendarExtractor
from .utils.client_alerts import DatabaseComparer
from .utils.extractor import PDFExtractor
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

    document = request.FILES.get("file", None)
    if not document:
        return JsonResponse(data={"message": "No file was uploaded."},
                            status=status.HTTP_400_BAD_REQUEST)

    document_name = document.name
    if not document_name.endswith('.pdf'):
        return JsonResponse(data={"message": "Invalid file format. Please upload a PDF file."},
                            status=status.HTTP_400_BAD_REQUEST)


    #extract calendar from pdf
    calendar = CalendarExtractor(document)
    calendar.calendar_extractor()
    if calendar.dates == []:
        return JsonResponse(data={"message": "No calendar was found in the PDF file."},
                            status=status.HTTP_400_BAD_REQUEST)
    data = calendar.transform_to_dict()

    errors = []

    try:
        calendar = Calendar.objects.all()
        calendar.delete()
    except Calendar.DoesNotExist:
        pass

    for digits, date in data.items():
        entry = {
            'id': 0,
            'digits': digits,
            'date': date
        }
        serializer: CalendarSerializer = CalendarSerializer(data=entry)
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

    data = {}
    data["warnings"] = {
        "calendar": {
          # message: "The calendar is outdated. Please update it.",
          # type: "warning"
        },
        "declaration": {
          # message: "The declaration is outdated. Please update it.",
          # type: "warning"
        },
        "rut": {
          # message: "The RUT is outdated. Please update it.",
          # type: "warning"
        }
    }
    data["errors"] = {
        "calendar": {
        #   message: "The calendar is missing. Please upload it.",
        },
        "declaration": {

        },
    }

    #comparer data
    comparer = DatabaseComparer(cc)

    # for calendar
    calendar_warning = comparer.compare_calendar()
    if "error" in calendar_warning:
        data["errors"]["calendar"]["message"] = calendar_warning["error"]
        data["errors"]["calendar"]["type"] = "danger"
    else:
        data["warnings"]["calendar"]["message"] = calendar_warning["calendar_warning"]
        data["warnings"]["calendar"]["type"] = "warning"

    declaration_warning = comparer.compare_declaration()
    print(declaration_warning)
    if "error" in declaration_warning:
        data["errors"]["declaration"]["message"] = declaration_warning["error"]
        data["errors"]["declaration"]["type"] = "danger"

    if "issue" in declaration_warning:
        data["errors"]["declaration"]["message"] = declaration_warning["issue"]
        data["errors"]["declaration"]["type"] = "danger"

    data["warnings"]["declaration"] = declaration_warning["declaration"]

    return JsonResponse(data=data, status=status.HTTP_200_OK)

@api_view(["POST"])
def set_declaration(request, cc):
        document = request.FILES.get("file", None)
        if not document:
            return JsonResponse(data={"message": "No file was uploaded."},
                                status=status.HTTP_400_BAD_REQUEST)

        document_name = document.name
        if not document_name.endswith('.pdf'):
            return JsonResponse(data={"message": "Invalid file format. Please upload a PDF file."},
                                status=status.HTTP_400_BAD_REQUEST)

        #set document to media folder

        client = Client.objects.get(cc=cc)
        client_nit = client.nit

        #extract calendar from pdf
        document_info = PDFExtractor(document, "2")
        entry = document_info.get_data()
        entry["id"] = 0
        entry["client"] = client.id
        entry["anual_auditory_benefits"] = request.data.get("anual_auditory_benefits", "null")
        entry["semestrals_auditory_benefits"] = request.data.get("semestrals_auditory_benefits", "null")
        entry["uvt"] = request.data.get("uvt", 40000)
        print(entry)

        if client_nit != int(entry["nit"]):
            return JsonResponse(data={"message": "Client's NIT does not match with the NIT in the declaration."},
                                status=status.HTTP_400_BAD_REQUEST)

        before = Declaration.objects.filter(client=client, date=entry["date"])
        success_message = {"message": "Declaration was processed successfully."}
        if before:
            aditional_string = "You has already uploaded a declaration for this year. The previous declaration will be deleted."
            success_message["alert"] = aditional_string
            success_message["type"] = "info"
            for b in before:
                b.delete()

        #delete file from media folder

        serializer : DeclarationSerializer = DeclarationSerializer(data=entry)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(data=success_message, status=status.HTTP_201_CREATED)

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def get_declaration(request, cc) -> JsonResponse:
    try:
        client = Client.objects.get(cc=cc)
        id = client.id
        declaration = Declaration.objects.filter(client=id)
    except Declaration.DoesNotExist:
        return JsonResponse(data={"message": f"The declaration for the client with CC {cc} does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

    serializer = DeclarationSerializer(declaration, many=True)
    return JsonResponse(data=serializer.data, status=status.HTTP_200_OK, safe=False)

@api_view(["GET"])
def get_declaration_by_date(request, cc, year) -> JsonResponse:
    try:
        client = Client.objects.get(cc=cc)
        id = client.id
        date = f"{year}-01-01"
        declaration = Declaration.objects.get(client=id, date=date)
    except Declaration.DoesNotExist:
        return JsonResponse(data={"message": f"The declaration of de year {year} for the client with CC {cc} does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

    serializer = DeclarationSerializer(declaration)
    return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)

@api_view(["POST"])
def set_rut(request, cc):

        document = request.FILES.get("file", None)
        if not document:
            return JsonResponse(data={"message": "No file was uploaded."},
                                status=status.HTTP_400_BAD_REQUEST)

        document_name = document.name
        if not document_name.endswith('.pdf'):
            delete_from_media_folder(document)
            return JsonResponse(data={"message": "Invalid file format. Please upload a PDF file."},
                                status=status.HTTP_400_BAD_REQUEST)

        #set document to media folder

        client = Client.objects.get(cc=cc)
        client_nit = client.nit

        #extract calendar from pdf
        document_info = PDFExtractor(document, "1")
        entry = document_info.get_data()
        entry["id"] = 0
        entry["client"] = client.id

        if client_nit != int(entry["nit"]):
            return JsonResponse(data={"message": "Client's NIT does not match with the NIT in the RUT."},
                                status=status.HTTP_400_BAD_REQUEST)

        success_message = {"message": "Rut was processed successfully."}
        client_ruts = Rut.objects.filter(client=client)
        if client_ruts:
            aditional_string = "You has already uploaded a RUT for this client. The previous RUT will be deleted."
            success_message["alerts"] = {
                "update": aditional_string,
                "type": "info"
            }
            for client_rut in client_ruts:
                client_rut.delete()


        if entry["fiscal_responsibilities"] == True:
            client.fiscal_responsibilities = True
            client.save()
            success_message["alerts"] = {
                "update": "The client now has IVA fiscal responsibilities.",
                "type": "info",
            }

        if entry["fiscal_responsibilities"] == False:
            entry["fiscal_responsibilities"] = False

        if entry["fiscal_responsibilities"] == "":
            entry["fiscal_responsibilities"] = False
            success_message["alerts"] = {
                "warning": "The RUT does not have IVA fiscal responsibilities. Please update the rut.",
                "type": "danger"
            }

        serializer : RutSerializer = RutSerializer(data=entry)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(data=success_message, status=status.HTTP_201_CREATED)

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def get_rut(request, cc) -> JsonResponse:
    try:
        client = Client.objects.get(cc=cc)
        id = client.id
        rut = Rut.objects.get(client=id)
    except Rut.DoesNotExist:
        return JsonResponse(data={"message": f"The RUT for the client with CC {cc} does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

    serializer = RutSerializer(rut)
    return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)
