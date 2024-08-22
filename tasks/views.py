from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status

from .serializers import ClientSerializer
from .models import Client


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