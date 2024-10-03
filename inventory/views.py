# inventory/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import (
    Product, Inbound, Outbound, User,
    ScheduledOutbound, Customer
)
from .forms import (
    ProductForm, InboundForm, OutboundForm,
    UserRegistrationForm,
    ScheduledOutboundForm, UserEditForm,
    CustomerForm
)
from django.contrib.auth import login
from django.contrib import messages
from .utils import roles_required
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.models import F

User = get_user_model()

# ---------------------------------------------- #
# ----------- Logic for Admin ------------------ #
# ---------------------------------------------- #

@login_required
@roles_required(['Admin'])
def create_manager(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request=request)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'Manager'
            user.save()
            messages.success(request, "Manager successfully created.")
            return redirect('user_list')
    else:
        form = UserRegistrationForm(request=request)
    return render(request, 'inventory/user_form.html', {'form': form, 'title': 'Create Manager'})

@login_required
@roles_required(['Admin'])
def user_list(request):
    users = User.objects.filter(role__in=['Manager', 'Operator'])
    return render(request, 'inventory/user_list.html', {'users': users})

@login_required
@roles_required(['Admin'])
def create_user(request, role):
    if role not in ['Manager', 'Operator']:
        messages.error(request, "Invalid role specified.")
        return redirect('user_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, role=role)
        if form.is_valid():
            form.save()
            messages.success(request, f"{role} created successfully.")
            return redirect('user_list')
    else:
        form = UserRegistrationForm(role=role)
    return render(request, 'inventory/user_form.html', {'form': form, 'title': f'Create {role}'})

@login_required
@roles_required(['Admin'])
def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.role == 'Admin':
        messages.error(request, "Cannot edit an Admin user.")
        return redirect('user_list')

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully.")
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'inventory/user_form.html', {'form': form, 'title': 'Edit User'})

@login_required
@roles_required(['Admin'])
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect('user_list')
    return render(request, 'inventory/user_confirm_delete.html', {'user': user, 'title': 'Delete User'})

# ---------------------------------------------- #
# ----------- Logic for Inventory -------------- #
# ---------------------------------------------- #

@login_required
def inventory_list(request):
    products = Product.objects.all()
    query = request.GET.get('q')
    no_results = False
    if query:
        products = products.filter(name__icontains=query) | products.filter(sku__icontains=query)
        if not products.exists():
            no_results = True
    return render(request, 'inventory/inventory_list.html', {'products': products, 'no_results': no_results})

@login_required
def inventory_detail(request, sku):
    product = get_object_or_404(Product, sku=sku)
    return render(request, 'inventory/inventory_detail.html', {'product': product})

@login_required
@roles_required(['Admin', 'Manager'])
def inventory_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product successfully added to inventory.")
            return redirect('inventory_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/inventory_form.html', {'form': form, 'title': 'Add Product'})

@login_required
@roles_required(['Admin', 'Manager'])
def inventory_edit(request, sku):
    product = get_object_or_404(Product, sku=sku)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product details successfully updated.")
            return redirect('inventory_detail', sku=product.sku)
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/inventory_form.html', {'form': form, 'title': 'Edit Product'})

@login_required
@roles_required(['Admin'])
def inventory_delete(request, sku):
    product = get_object_or_404(Product, sku=sku)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product successfully deleted from inventory.")
        return redirect('inventory_list')
    return render(request, 'inventory/inventory_confirm_delete.html', {'product': product, 'title': 'Delete Product'})

# ---------------------------------------------- #
# ----------- Logic for Inbound ---------------- #
# ---------------------------------------------- #

@login_required
@roles_required(['Admin', 'Manager', 'Operator'])
def inbound_list(request):
    inbounds = Inbound.objects.all()
    return render(request, 'inventory/inbound_list.html', {'inbounds': inbounds})

@login_required
@roles_required(['Admin', 'Manager', 'Operator'])
def inbound_detail(request, pk):
    inbound = get_object_or_404(Inbound, pk=pk)
    return render(request, 'inventory/inbound_detail.html', {'inbound': inbound})

@login_required
@roles_required(['Admin', 'Manager', 'Operator'])
def inbound_add(request):
    if request.method == 'POST':
        form = InboundForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    product = form.cleaned_data.get('product')
                    new_product_sku = form.cleaned_data.get('new_product_sku')

                    if not product and new_product_sku:
                        new_product_name = form.cleaned_data.get('new_product_name')
                        new_category = form.cleaned_data.get('new_category')
                        new_supplier = form.cleaned_data.get('new_supplier')
                        new_location = form.cleaned_data.get('new_location')
                        new_tags = form.cleaned_data.get('new_tags')

                        product, created = Product.objects.get_or_create(
                            sku=new_product_sku,
                            defaults={
                                'name': new_product_name,
                                'category': new_category,
                                'supplier': new_supplier,
                                'location': new_location,
                                'quantity': 0,
                                'reserved_quantity': 0,
                                'tags': new_tags
                            }
                        )
                        if not created:
                            form.add_error(None, f"Product with SKU {new_product_sku} already exists.")
                            return render(request, 'inventory/inbound_form.html', {'form': form, 'title': 'Add Inbound'})

                    inbound = form.save(commit=False)
                    inbound.product = product
                    inbound.location = product.location
                    inbound.created_by = request.user
                    inbound.save()

                    product.quantity += inbound.quantity
                    product.save()

                    messages.success(request, "Inbound record successfully added and inventory updated.")
                    return redirect('inbound_list')
            except Exception as e:
                form.add_error(None, f'An unexpected error occurred: {str(e)}')
    else:
        form = InboundForm()
    return render(request, 'inventory/inbound_form.html', {'form': form, 'title': 'Add Inbound'})


@login_required
@roles_required(['Admin', 'Manager'])
def trigger_automated_inbound(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        new_location = request.POST.get('new_location', '').strip()
        try:
            product = Product.objects.get(sku=sku)
            location = new_location if new_location else product.location
            Inbound.objects.create(
                reference=f"AUTO-INBOUND-{product.sku}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                date_received=timezone.now(),
                product=product,
                quantity=100,
                location=location,
                remarks='Automated inbound triggered by SKU.',
                created_by=request.user
            )
            product.quantity += 100
            product.location = location
            product.save()

            messages.success(request, f'Automated inbound process completed for SKU {sku}.')
            return redirect('inventory_list')
        except Product.DoesNotExist:
            messages.error(request, f'Product with SKU {sku} does not exist.')
            return redirect('inventory_list')
    else:
        return redirect('inventory_list')

# ---------------------------------------------- #
# ----------- Logic for Outbound --------------- #
# ---------------------------------------------- #

@login_required
@roles_required(['Admin', 'Manager', 'Operator'])
def outbound_add(request):
    if request.method == 'POST':
        form = OutboundForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    outbound = form.save(commit=False)
                    outbound.status = 'Pending'
                    product = outbound.product
                    quantity = outbound.quantity

                    if product.available_quantity >= quantity:
                        product.reserved_quantity += quantity
                        product.save()
                        outbound.created_by = request.user
                        outbound.save()

                        messages.success(request, "Outbound record successfully added and inventory updated.")
                        return redirect('outbound_list')
                    else:
                        form.add_error('quantity', f"Not enough available stock. Available: {product.available_quantity}")
            except Exception as e:
                form.add_error(None, f'An unexpected error occurred: {str(e)}')
    else:
        form = OutboundForm()
    return render(request, 'inventory/outbound_form.html', {'form': form, 'title': 'Add Outbound'})


@login_required
@roles_required(['Admin', 'Manager', 'Operator'])
def outbound_list(request):
    outbounds = Outbound.objects.all()
    query = request.GET.get('q')
    no_results = False
    if query:
        outbounds = outbounds.filter(product__sku__icontains=query) | outbounds.filter(reference__icontains=query)
        if not outbounds.exists():
            no_results = True
    return render(request, 'inventory/outbound_list.html', {'outbounds': outbounds, 'no_results': no_results})

@login_required
@roles_required(['Admin', 'Manager', 'Operator'])
def outbound_detail(request, pk):
    outbound = get_object_or_404(Outbound, pk=pk)
    return render(request, 'inventory/outbound_detail.html', {'outbound': outbound})


def adjust_product_quantities(outbound, previous_status, new_status):
    product = outbound.product
    quantity = outbound.quantity

    status_changes = {
        ('Pending', 'Shipped'): {'reserved': -quantity, 'quantity': -quantity},
        ('Pending', 'Delivered'): {'reserved': -quantity, 'quantity': -quantity},
        ('Pending', 'Canceled'): {'reserved': -quantity},
        ('Shipped', 'Delivered'): {},
        ('Shipped', 'Pending'): {'reserved': +quantity, 'quantity': +quantity},
        ('Shipped', 'Canceled'): {'quantity': +quantity},
        ('Canceled', 'Pending'): {'reserved': +quantity},
        ('Canceled', 'Shipped'): {'quantity': -quantity, 'reserved': +quantity},
        ('Delivered', 'Pending'): {'reserved': +quantity, 'quantity': +quantity},
        ('Delivered', 'Canceled'): {'quantity': +quantity},
    }

    adjustments = status_changes.get((previous_status, new_status))

    if adjustments:
        if 'reserved' in adjustments:
            product.reserved_quantity += adjustments['reserved']
        if 'quantity' in adjustments:
            product.quantity += adjustments['quantity']
        product.save()

@login_required
@roles_required(['Admin', 'Manager'])
def outbound_update_status(request, pk):
    outbound = get_object_or_404(Outbound, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        previous_status = outbound.status
        if new_status != previous_status:
            try:
                with transaction.atomic():
                    adjust_product_quantities(outbound, previous_status, new_status)

                    outbound.status = new_status
                    outbound.modified_by = request.user
                    outbound.save()

                    messages.success(request, "Outbound status updated.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.info(request, "No status change detected.")
        return redirect('outbound_list')
    return render(request, 'inventory/outbound_update_status.html', {'outbound': outbound})


@login_required
@roles_required(['Admin', 'Manager'])
def scheduled_outbound_list(request):
    scheduled_outbounds = ScheduledOutbound.objects.all()
    return render(request, 'inventory/scheduled_outbound_list.html', {'scheduled_outbounds': scheduled_outbounds})


@login_required
@roles_required(['Admin', 'Manager'])
def trigger_scheduled_outbounds(request):
    if request.method == 'POST':
        automated_outbound_check()
        messages.success(request, 'Scheduled outbounds processed successfully.')
        return redirect('outbound_list')
    else:
        return redirect('scheduled_outbound_list')

def automated_outbound_check():
    now = timezone.now()
    scheduled_outbounds = ScheduledOutbound.objects.filter(scheduled_date__lte=now)
    for schedule in scheduled_outbounds:
        product = schedule.product
        quantity_to_ship = schedule.quantity

        if product.available_quantity >= quantity_to_ship:
            try:
                with transaction.atomic():
                    product.reserved_quantity += quantity_to_ship
                    product.save()

                    outbound = Outbound.objects.create(
                        reference=f"SCHED-OUTBOUND-{product.sku}-{now.strftime('%Y%m%d%H%M%S')}",
                        date_shipped=now,
                        product=product,
                        quantity=quantity_to_ship,
                        destination=schedule.destination,
                        customer_name=schedule.customer.name,
                        category='Sale',
                        status='Shipped',
                        created_by=None
                    )

                    product.quantity -= quantity_to_ship
                    product.reserved_quantity -= quantity_to_ship
                    product.save()

                    schedule.delete()

            except Exception as e:
                print(f"Error processing scheduled outbound for {product.sku}: {str(e)}")
        else:
            print(f"Insufficient stock for product {product.sku} to fulfill scheduled outbound.")

@login_required
@roles_required(['Admin', 'Manager'])
def scheduled_outbound_add(request):
    if request.method == 'POST':
        form = ScheduledOutboundForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Scheduled outbound added successfully.")
            return redirect('scheduled_outbound_list')
    else:
        form = ScheduledOutboundForm()
    return render(request, 'inventory/scheduled_outbound_form.html', {'form': form, 'title': 'Add Scheduled Outbound'})

# ---------------------------------------------- #
# ---------------- Utils Logic ----------------- #
# ---------------------------------------------- #

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request=request)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inventory_list')
    else:
        form = UserRegistrationForm(request=request)
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'inventory/profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'inventory/user_form.html', {'form': form, 'title': 'Edit Profile'})

@login_required
@roles_required(['Admin', 'Manager'])
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'inventory/customer_list.html', {'customers': customers})

@login_required
@roles_required(['Admin', 'Manager'])
def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer added successfully.")
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'inventory/customer_form.html', {'form': form, 'title': 'Add Customer'})
