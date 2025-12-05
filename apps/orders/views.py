from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from apps.products.models import Product
from .models import Order, OrderItem
from .forms import CheckoutForm
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal

def _get_cart(session):
    return session.setdefault('cart', {})

class AddToCartView(View):
    def post(self, request, pk):
        cart = _get_cart(request.session)
        qty = int(request.POST.get('quantity', 1))
        item = cart.get(str(pk), {'quantity': 0})
        item['quantity'] = item.get('quantity', 0) + qty
        cart[str(pk)] = item
        request.session.modified = True
        return redirect('orders:cart')

class CartView(View):
    def get(self, request):
        cart = _get_cart(request.session)
        product_ids = [int(pid) for pid in cart.keys()]
        products = Product.objects.filter(id__in=product_ids)
        items = []
        total = Decimal('0.00')
        for p in products:
            qty = cart.get(str(p.id), {}).get('quantity', 0)
            subtotal = p.price * qty
            items.append({'product': p, 'quantity': qty, 'subtotal': subtotal})
            total += subtotal
        return render(request, 'orders/cart.html', {'items': items, 'total': total})

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        form = CheckoutForm()
        return render(request, 'orders/checkout.html', {'form': form})

    def post(self, request):
        form = CheckoutForm(request.POST)
        if not form.is_valid():
            return render(request, 'orders/checkout.html', {'form': form})
        cart = _get_cart(request.session)
        if not cart:
            return redirect('product_list')
        order = Order.objects.create(user=request.user, shipping_address=form.cleaned_data['shipping_address'])
        total = 0
        for pid, info in cart.items():
            product = get_object_or_404(Product, pk=int(pid))
            qty = int(info['quantity'])
            OrderItem.objects.create(order=order, product=product, quantity=qty, price=product.price)
            # update stock
            if product.stock >= qty:
                product.stock -= qty
                product.save()
            total += product.price * qty
        order.total = total
        order.save()
        # clear session cart
        request.session['cart'] = {}
        request.session.modified = True
        return redirect('products:product_list')
