from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import ContractForm
from .models import Contract, Category
from django.utils import timezone
from datetime import timedelta

# ==========================================
# AUTHENTICATION VIEWS
# ==========================================
""""
def signup_view(request):
     Handles new user registration.
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log the user in after they sign up
            login(request, user)
            return redirect('contract_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

"""

def login_view(request):
    """Handles existing user login."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('contract_list')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    """Logs the user out and sends them to the welcome page."""
    if request.method == 'POST':
        logout(request)
        return redirect('welcome')
    # Provide a fallback GET request if you aren't using a form to logout
    logout(request)
    return redirect('welcome')

# ==========================================
# APPLICATION VIEWS
# ==========================================

# THE WELCOME PAGE (Homepage)
def welcome(request):
    return render(request, 'contracts/welcome.html')

# THE DASHBOARD (List of Contracts)
@login_required(login_url='login')
def contract_list(request):
    # Base query
    contracts = Contract.objects.all().order_by('category__name', 'end_date')
    categories = Category.objects.all() # Fetch categories for the dropdown

    # 1. Filter by Category
    category_id = request.GET.get('category')
    if category_id:
        contracts = contracts.filter(category_id=category_id)

    # 2. Filter by Status (Translating days left into date filters)
    status_filter = request.GET.get('status')
    today = timezone.now().date()

    if status_filter == 'expired':
        contracts = contracts.filter(end_date__lt=today)
    elif status_filter == 'critical':
        contracts = contracts.filter(end_date__gte=today, end_date__lte=today + timedelta(days=30))
    elif status_filter == 'warning':
        contracts = contracts.filter(end_date__gt=today + timedelta(days=30), end_date__lte=today + timedelta(days=90))
    elif status_filter == 'healthy':
        contracts = contracts.filter(end_date__gt=today + timedelta(days=90))

    context = {
        'contracts': contracts,
        'categories': categories,
    }
    return render(request, 'contracts/contract_list.html', context)

# ADD NEW CONTRACT
@login_required(login_url='login')
def add_contract(request):
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('contract_list')
    else:
        form = ContractForm()

    return render(request, 'contracts/add_contract.html', {'form': form})

# EDIT EXISTING CONTRACT
@login_required(login_url='login')
def edit_contract(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)

    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            form.save()
            return redirect('contract_list')
    else:
        form = ContractForm(instance=contract)

    return render(request, 'contracts/edit_contract.html', {'form': form, 'contract': contract})