from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views import View
from django.views.generic.detail import DetailView
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from perfil.models import Perfil
from django.db.models import Q

from . import models

class ListaProdutos(ListView):
    model = models.Produto
    template_name = 'produto/lista.html'
    context_object_name = 'produtos'
    paginate_by = 10
    ordering_by = ['-id']
    
class DetalheProduto(DetailView):
    model = models.Produto
    template_name = 'produto/detalhe.html'
    context_object_name = 'produto'
    slug_url_kwarg = 'slug'
class AdicionarAoCarrinho(View):
    def get(self, *args, **kwargs):
        http_refere = self.request.META.get(
            'HTTP_REFERER',   #se não houver referenciador da url atual, ele joga pro inicio
            reverse('produto:lista')
            )
        variacao_id = self.request.GET.get('vid')  #o segundo get é de dicionario
        #aqui resgatamos o variacao_id que foi passado na url
        if not variacao_id:
            messages.error(
                self.request,
                'Produto não existe'
            )
            return redirect(http_refere)
        variacao = get_object_or_404(models.Variacao, id=variacao_id)
        variacao_estoque = variacao.estoque
        produto = variacao.produto
        if variacao.estoque < 1:
            messages.error(
                self.request, 
                'Estoque insuficiente'
            )
        if not self.request.session.get('carrinho'):
            self.request.session['carrinho'] = {}
            self.request.session.save()
            
        carrinho = self.request.session['carrinho']
        imagem = produto.imagem
        if imagem:
            imagem = imagem.name
        else:
            imagem = ''
        if variacao_id in carrinho:
            quantidade_carrinho = carrinho[variacao_id]['quantidade']
            quantidade_carrinho += 1
            
            if variacao_estoque < quantidade_carrinho:
                messages.warning(
                    self.request,
                    f'Estoque insuficiente para {quantidade_carrinho}x no '
                    f'produto "{produto.nome}". Adicionamos {variacao_estoque}x'
                    f'no seu carrinho.'
                )
                quantidade_carrinho = variacao_estoque
            carrinho[variacao_id]['quantidade'] = quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo'] = variacao.preco * quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo'] = variacao.preco * quantidade_carrinho

        else:
            carrinho[variacao_id] = {
                'produto_id': produto.pk,
                'produto_nome': produto.nome,
                'variacao_nome': variacao.nome or '',
                'variacao_id': variacao.pk,
                'preco_unitario': variacao.preco,
                'preco_unitario_promocional': variacao.preco_promocional,
                'preco_quantitativo': variacao.preco,
                'preco_quantitativo_promocional': variacao.preco_promocional,
                'quantidade': 1,
                'slug': produto.slug,
                'imagem': imagem,
                
            }
        self.request.session.save()
        messages.success(
            self.request,
            f'Produto {produto.nome} {variacao.nome} adicionado ao seu'
            f'carrinho {carrinho[variacao_id]["quantidade"]}x.'

        )
        return redirect(http_refere)
    
    
class RemoverDoCarrinho(View):
    def get(self, *args, **kwargs):
        print(0)
        http_refere = self.request.META.get(
            'HTTP_REFERER',   #se não houver referenciador da url atual, ele joga pro inicio
            reverse('produto:lista')
        )
        variacao_id = self.request.GET.get('vid')  
        
        if not variacao_id:
            print(1)
            return redirect(http_refere)
        
        if not self.request.session.get('carrinho'):
            print(2)
            return redirect(http_refere)
        
        if variacao_id not in self.request.session['carrinho']:
            print(3)
            return redirect(http_refere)
        
        carrinho = self.request.session['carrinho'][variacao_id]
        
        del self.request.session['carrinho'][variacao_id]
        self.request.session.save()
        messages.success(
            self.request,
            f'Produto {carrinho["produto_nome"]} {carrinho["variacao_nome"]} Removido com sucesso'
        )
        return redirect(http_refere)
class Carrinho(View):
    def get(self, *args, **kwargs):
        context = {
            'carrinho': self.request.session.get('carrinho', {})
        }
        return render(
             self.request,
            'produto/carrinho.html',
            context,
        )
class Finalizar(View):
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')
        
        perfil = Perfil.objects.filter(user=self.request.user).exists()
        if not perfil:
            messages.error(
                self.request,
                'Usuário sem perfil'
            )
            return redirect('perfil:criar')
        if not self.request.session.get('carrinho'):
            messages.error(
                self.request,
                'Carrinho vazio'
            )
            return redirect('produto:lista')
        context = {
            'carrinho': self.request.session.get('carrinho', {}),
            'usuario': self.request.user,
        } 
        return render(
             self.request,
            'produto/finalizar.html',
            context,
        )
        
        
class Busca(ListaProdutos):
    def get_queryset(self, *args, **kwargs):
        termo = self.request.GET.get('termo') or self.request.session['termo']

        qs = super().get_queryset(*args, **kwargs)
        
        if not termo:
            return qs 
        self.request.session['termo'] = termo
        qs = qs.filter(
            Q(nome__icontains=termo) |
            Q(descricao_longa__icontains=termo) |
            Q(descricao_curta__icontains=termo) 

        )
        self.request.session.save()
        return qs 