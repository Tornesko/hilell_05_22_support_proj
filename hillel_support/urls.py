from django.contrib import admin
from django.urls import path

from core.api.exchange_rates import btc_usd, history, home
from core.api.tickets import get_all_tickets

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home),
    # Exchange rates
    path("btc_usd/", btc_usd),
    path("history/", history),
    # Tickets
    path("tickets/", get_all_tickets),
]
