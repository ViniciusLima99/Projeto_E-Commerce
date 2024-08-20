from django.template import Library
from utils import formata_valor, cart_total_qtd, cart_totals
register = Library()

@register.filter
def formata_preco(val):
    return formata_valor(val)

@register.filter
def cart_total_qtd_(carrinho):
    return cart_total_qtd(carrinho)

@register.filter
def cart_totals_(carrinho):
    return cart_totals(carrinho)