from django.contrib import admin
from .models import Produto, Variacao
from . import models
from django.http import HttpRequest
# Register your models here.
class VariacaoInline(admin.TabularInline):
    model = models.Variacao
    extra = 1
    

admin.site.register(Variacao)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
   list_display = 'nome', 'descricao_curta', 'get_preco_formatado','get_preco_promocional_formatado',
   inlines =  VariacaoInline,
#    def has_add_permission(self, request: HttpRequest) -> bool:
#        return 

