from django.db import models
from django.contrib.auth.models import User

class ServiceItem(models.Model):
    name = models.CharField(max_length=50, unique=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.name} - ${self.unit_price:.2f}"

class Event(models.Model):
    img = models.ImageField(upload_to="pic")
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    services = models.ManyToManyField(ServiceItem, through='EventService')
    
    def __str__(self):
        return f"{self.name} - ${self.price:.2f}"

class EventService(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceItem, on_delete=models.CASCADE)
    default_quantity = models.PositiveIntegerField(default=0)  # 🟢 默认提供的数量
    quantity_available = models.PositiveIntegerField(default=0)  # 🔵 最大可预订数量
    
    def __str__(self):
        return f"{self.event.name} - {self.service.name} (默认 {self.default_quantity} / 最多 {self.quantity_available})"
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', '待确认报价'),
        ("assigned", "已接单"),
        ('quoted', '待支付'),
        ('paid', '已支付'),
        ('cancelled', '已取消'),
    ]

    cus_name = models.ForeignKey(User, on_delete=models.CASCADE)
    cus_ph = models.CharField(max_length=12)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    booking_date = models.DateField()
    booked_on = models.DateField(auto_now=True)
    services = models.ManyToManyField(ServiceItem, through='BookingService')
    price_quote = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 价格报价
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # 订单状态
    assigned_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')  # 指派的管理员

    def can_be_assigned(self):
        """ 确保管理员最多只能接手 5 个订单 """
        return self.status == "pending" and self.assigned_manager is None
    
    def __str__(self):
        return f"{self.event.name} - {self.cus_name} ({self.get_status_display()})"

class BookingService(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.booking.cus_name} - {self.service.name} x {self.quantity}"

class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=[('credit', 'Credit Card')])
    card_last4 = models.CharField(max_length=4)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    paid_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.id} for Booking #{self.booking.id}"