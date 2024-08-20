from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, DeleteView, DetailView
from django.views import View
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from EcommerceApp.models import Variacao
from utils.cart_qtd import cart_total_qtd
from utils.cart_totals import cart_totals
from .models import Pedido, ItemPedido
# Create your views here.

class DispatchLoginRequiredMixin(View):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')
        return super().dispatch(request, *args, **kwargs)
    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        qs = qs.filter(user = self.request.user)
        return qs
class Pagar(DispatchLoginRequiredMixin, DetailView):
    template_name = 'pedidos/pagar.html'
    model = Pedido 
    pk_ùrl_kwarg = 'pk'
    context_object_name = 'pedido'

   
class SalvarPedido(View):
    template_name = 'pedidos/pagar.html'
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(
                self.request,
                'Você precisa fazer login'
            )
            return redirect('perfil:criar')
        if not self.request.session.get('carrinho'):
            messages.error(
                self.request,
                'Carrinho vazio'
            )
            return redirect('produto:lista')
        carrinho = self.request.session.get('carrinho')
        carrinho_variacao_ids = [v for v in carrinho]
        bd_variacoes = list(
            Variacao.objects.select_related('produto')
            .filter(id__in=carrinho_variacao_ids)
            )
        error_msg_estoque = ''

        for variacao in bd_variacoes:
            vid = str(variacao.pk)
            estoque = variacao.estoque
            quantidade_carrinho = carrinho[vid]['quantidade']
            preco_unt = carrinho[vid]['preco_unitario']
            preco_unt_promo = carrinho[vid]['preco_unitario_promocional']
            
            if estoque < quantidade_carrinho:
                carrinho[vid]['quantidade'] = estoque 
                carrinho[vid]['preco_quantitativo'] = estoque * preco_unt 
                carrinho[vid]['preco_quantitativo_promocional'] = estoque * preco_unt_promo
                
                error_msg_estoque = 'Estoque insuficiente para alguns produtos do seu carrinho.'
            if error_msg_estoque:
                messages.error(
                    self.request, 
                    error_msg_estoque
                )
                self.request.session.save()
                return redirect('produto:carrinho')
        quantidade_total_carrinho = cart_total_qtd(carrinho)
        valor_total_carrinho = cart_totals(carrinho)
        
        pedido = Pedido(
            user = self.request.user,
            total = valor_total_carrinho,
            qtd_total = quantidade_total_carrinho,
            status = 'C'
        )
        pedido.save()
        ItemPedido.objects.bulk_create(
            [
                ItemPedido(
                    pedido=pedido,
                    produto=item['produto_nome'],
                    produto_id=item['produto_id'],
                    variacao=item['variacao_nome'] ,
                    variacao_id= item['variacao_id'] ,
                    preco = item['preco_quantitativo'],
                    preco_promocional= item['preco_quantitativo_promocional'] ,
                    quantidade =item['quantidade'] ,
                    imagem= item['imagem'] ,
                ) for item in carrinho.values()
                
            ]
        )
        pedido.save()
        # contexto = {
        #     'quantidade_total_carrinho': quantidade_total_carrinho,
        #     'valor_total_carrinho': valor_total_carrinho
        # }
        del self.request.session['carrinho']
        
        return redirect(
            reverse(
                'pedido:pagar',
                kwargs={'pk': pedido.pk}
            )
        )
        

class Detalhe(DispatchLoginRequiredMixin, DetailView):
    model = Pedido 
    context_object_name = 'pedido' 
    template_name = 'pedidos/detalhe.html'
    pk_url_kwarg = 'pk'
    
class Lista(DispatchLoginRequiredMixin, ListView):
    model = Pedido 
    context_object_name = 'pedidos' 
    template_name = 'pedidos/listapedidos.html'
    paginate_by = 10
    ordering = ['-id']
    
    
