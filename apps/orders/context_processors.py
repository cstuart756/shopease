def cart_total(request):
    cart = request.session.get('cart', {})
    total_items = sum(item.get('quantity',0) for item in cart.values())
    return {'cart_item_count': total_items}
