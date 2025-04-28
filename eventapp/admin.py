from django.contrib import admin
from .models import Event, Booking, ServiceItem, EventService, BookingService
# Register your models here.
admin.site.register(Event)
admin.site.register(Booking)
admin.site.register(ServiceItem)
admin.site.register(EventService)
admin.site.register(BookingService)