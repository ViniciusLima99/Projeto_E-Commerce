from django.contrib import admin
from . import models
from .models import Perfil

# Register your models here.
@admin.register(Perfil)
class ProdutoAdmin(admin.ModelAdmin):
    ...