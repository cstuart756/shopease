from django.conf import settings
from django.db import models
from apps.products.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField(blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_total(self):
        total = sum([item.subtotal() for item in self.items.all()])
        self.total = total
        self.save()
        return self.total

    def __str__(self):
        return f"Order #{self.pk} by {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        # set price snapshot
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
