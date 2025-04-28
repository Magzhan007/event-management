from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from .models import Event, Booking, ServiceItem, EventService, BookingService, Payment
from .forms import BookingForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
def index(request):
    return render(request,'index.html')
def about(request):
    return render(request,'about.html')
def events(request):
    dict_eve={
        'eve':Event.objects.all()
    }
    return render(request,'events.html',dict_eve)
def booking(request):
    if request.method=='POST':
        form=BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')

    form=BookingForm()
    dict_form={
        'form':form
    }
    return render(request,'booking.html',dict_form)
def contact(request):
    return render(request,'contact.html')


# Event List View
def event_list(request):
    events = Event.objects.all()

    # 计算每个 event 的总价格
    event_data = []
    
    for event in events:
        services = EventService.objects.filter(event=event)
        total_price = event.price  # 先加上基础价格

        service_details = []
        for service in services:
            default_qty = service.default_quantity  # 默认数量 = 可用数量
            service_cost = default_qty * service.service.unit_price  # 价格计算
            total_price += service_cost  # 加到总价里
            
            service_details.append({
                "service": service.service,
                "quantity_available": service.quantity_available,
                "unit_price": service.service.unit_price,
                "default_quantity": default_qty,
                "total_cost": service_cost,
            })

        event_data.append({'event': event, 'total_price': total_price, "services": service_details})
        
    return render(request, 'events/event_list.html', {'events': events, 'event_data': event_data})

# Event Detail View
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    services = EventService.objects.filter(event=event)

    # 计算总价
    total_price = event.price  # 先加上基础价格
    for service in services:
        total_price += service.default_quantity * service.service.unit_price  # 用最大可用数量来计算

    return render(request, 'events/event_detail.html', {
        'event': event,
        'services': services,
        'total_price': total_price  # 传递总价
    })
# Booking View
@login_required
def book_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    services = EventService.objects.filter(event=event)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.cus_name = request.user
            booking.event = event
            booking.status = "pending"

            total_price = event.price  # ✅ 先把基础价格加上

            # 先保存 booking 记录
            booking.save()

            # 记录用户选择的服务项，并计算价格
            for service in services:
                quantity = int(request.POST.get(f'service_{service.service.id}', service.default_quantity))  # 🟢 默认数量

                if 0 <= quantity <= service.quantity_available:
                    BookingService.objects.create(
                        booking=booking,
                        service=service.service,
                        quantity=quantity
                    )
                    total_price += service.service.unit_price * quantity  # ✅ 计算服务项价格

                else:
                    messages.error(request, f"{service.service.name} 最多只能预订 {service.quantity_available} 个！")
                    return redirect('book_event', event_id=event.id)

            # ✅ 更新报价
            booking.price_quote = total_price
            booking.save()

            messages.success(request, "Order Submitted Successfully!")
            return redirect('booking_success', booking_id=booking.id)

    else:
        form = BookingForm()

    return render(request, 'events/book_event.html', {'form': form, 'event': event, 'services': services})

# Booking Success View
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, cus_name=request.user)
    booked_services = BookingService.objects.filter(booking=booking)

    # 计算总价
    total_price = booking.event.price  # 初始价格
    for bs in booked_services:
        
        total_price += bs.service.unit_price * bs.quantity

    return render(request, 'events/booking_success.html', {
        'booking': booking,
        'booked_services': booked_services,
        'total_price': total_price
    })

@login_required
def my_orders(request):
    bookings = Booking.objects.filter(cus_name=request.user).order_by('-booked_on')
    return render(request, 'events/my_orders.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    """ 允许用户取消待审核或已报价的订单 """
    booking = get_object_or_404(Booking, id=booking_id, cus_name=request.user)

    if booking.status in ["pending", "quoted"]:
        booking.status = "cancelled"
        booking.save()
        messages.success(request, "The order was successfully cancelled.")
    else:
        messages.error(request, "This order cannot be cancelled.")

    return redirect("my_orders")



def can_assign_more(request):
    return request.user.assigned_orders.filter(status="assigned").count() < 5

@login_required
def manager_orders(request):
    """ 管理员接单页面 """
    if not request.user.is_staff:
        return redirect("index")  # 只有管理员能访问
    orders = Booking.objects.filter(status="pending", assigned_manager__isnull=True)

    return render(request, "orders/manager_orders.html", {"orders": orders, "can_assign_more": can_assign_more(request)})

@login_required
def manager_order_detail(request, booking_id):
    if not request.user.is_staff:
        return redirect("index")

    booking = get_object_or_404(Booking, id=booking_id)

    # 只允许未分配的订单进入详情页
    if booking.assigned_manager and booking.assigned_manager != request.user:
        return redirect("manager_orders")

    booked_services = BookingService.objects.filter(booking=booking)

    return render(
        request,
        "orders/manager_order_detail.html",
        {"booking": booking, "booked_services": booked_services, "can_assign_more": can_assign_more(request)},
    )

@login_required
def assign_order(request, booking_id):
    """ 管理员抢单 """
    booking = get_object_or_404(Booking, id=booking_id, status="pending", assigned_manager__isnull=True)

    if request.user.assigned_orders.filter(status="assigned").count() >= 5:
        messages.error(request, "You have reached your maximum order management limit.")
    else:
        booking.assigned_manager = request.user
        booking.status = "assigned"
        booking.save()
        messages.success(request, "Order taken successfully!")

    return redirect("manager_orders")

@login_required
def my_assigned_orders(request):
    """ 查看管理员已接单的订单 """
    assigned_orders = request.user.assigned_orders.filter(status__in=["assigned", "quoted", "paid"])
    return render(request, "orders/my_assigned_orders.html", {"assigned_orders": assigned_orders})

@login_required
def confirm_quote(request, booking_id):
    if not request.user.is_staff:
        return redirect("index")

    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        quote_price = request.POST.get("quote_price")
        if quote_price:
            booking.price_quote = quote_price
            booking.status = "quoted"  # 更新状态
            booking.assigned_manager = request.user  # 绑定管理员
            booking.save()
            messages.success(request, "Confirmed Successfully")
    
    return redirect("my_assigned_orders")  # ✅ 这里确保回到原页面

@login_required
def release_order(request, booking_id):
    """ 释放订单 """
    booking = get_object_or_404(Booking, id=booking_id, assigned_manager=request.user, status="assigned")
    booking.assigned_manager = None
    booking.status = "pending"
    booking.save()
    messages.success(request, "The order has been released and can accept again")
    return redirect("my_assigned_orders")




@login_required
def pay_order(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, cus_name=request.user)

    if booking.status == "paid":
        messages.info(request, "This order is already paid.")
        return redirect("my_orders")

    booked_services = BookingService.objects.filter(booking=booking)
    total_price = booking.price_quote

    if request.method == "POST":
        card_number = request.POST.get("card_number", "")
        expiry = request.POST.get("expiry", "")
        cvv = request.POST.get("cvv", "")

        if len(card_number) < 12 or not card_number.isdigit():
            messages.error(request, "Invalid card number.")
            return redirect("pay_order", booking_id=booking.id)

        # 🧾 模拟支付处理...
        last4 = card_number[-4:]

        # ✅ 保存支付记录
        Payment.objects.create(
            booking=booking,
            user=request.user,
            method="credit",
            card_last4=last4,
            amount=total_price
        )

        # ✅ 更新订单状态
        booking.status = "paid"
        booking.save()

        messages.success(request, f"Payment successful. Card ending in {last4}.")
        return redirect("my_orders")

    return render(request, "pay_order.html", {
        "booking": booking,
        "booked_services": booked_services,
        "total_price": total_price
    })
