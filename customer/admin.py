from django.contrib import admin
from .models import Transformer,Customer,Connector,Task

# Register your models here.

admin.site.register(Transformer)
admin.site.register(Connector)
admin.site.register(Customer)
admin.site.register(Task)
