from django.urls import path
from .views import (
    create_client,
    get_clients,
    get_client,
    delete_client,
    set_calendar,
    get_calendar, get_client_alerts, set_declaration, set_rut,
)

CLIENT_ENDPOINT_INIT = "clients"
CALENDAR_ENDPOINT_INIT = "calendar"

urlpatterns = [
        path(CLIENT_ENDPOINT_INIT + "/create", create_client, name="create_client"),
        path(CLIENT_ENDPOINT_INIT, get_clients, name="get_clients"),
        path(CLIENT_ENDPOINT_INIT + "/<int:cc>", get_client, name="get_client"),
        path(CLIENT_ENDPOINT_INIT + "/delete/<int:cc>", delete_client, name="delete_client"),
        path(CALENDAR_ENDPOINT_INIT + "/new", set_calendar, name="set_calendar"),
        path(CALENDAR_ENDPOINT_INIT, get_calendar, name="get_calendar"),
        path(CLIENT_ENDPOINT_INIT + "/<int:cc>/alerts", get_client_alerts, name="get_client_alerts"),
        path(CLIENT_ENDPOINT_INIT + "/<int:cc>/declaration/set", set_declaration, name="set_declaration"),
        path(CLIENT_ENDPOINT_INIT + "/<int:cc>/rut/set", set_rut, name="set_rut"),
        ]