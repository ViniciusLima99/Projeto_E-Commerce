def cart_totals(carrinho):
    return sum(
        [
            item.get('preco_quantitativo_promocional')
            if item.get('preco_quantativo_promocional')
            else item.get('preco_quantitativo')
            for item
            in carrinho.values()
        ]
    )