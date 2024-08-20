from django.contrib import admin
from .models import Pedido, ItemPedido
from . import models
# Register your models here.

   
class ItemPedidoInline(admin.TabularInline):
    model = models.ItemPedido
    extra = 1
admin.site.register(ItemPedido)

   
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
#    list_display = 'nome',
   inlines = ItemPedidoInline,