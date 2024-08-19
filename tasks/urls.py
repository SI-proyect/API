from django.urls import path
from .views import (
    create_client,
    get_clients,
    get_client
    )

CLIENT_ENDPOINT_INIT = "clients"

urlpatterns = [
        path(CLIENT_ENDPOINT_INIT + "/create", create_client, name="create_client"),
        path(CLIENT_ENDPOINT_INIT, get_clients, name="get_clients"),
        path(CLIENT_ENDPOINT_INIT + "/<int:cc>", get_client, name="get_client")
        ]