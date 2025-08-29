from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from .models import Expense
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum
from datetime import date
from django.contrib.auth.decorators import login_required
from decimal import Decimal



def home(request):
    return render(request, 'home.html')



def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'register.html')
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('user_dashboard')  # redirect to dashboard after login
        else:
            messages.error(request, "Invalid username or password")
            return redirect('user_dashboard')

    return render(request, 'login.html')



import json







from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta   

from .models import Expense, AiSuggestion
from .utils import get_ai_budget_suggestion


@login_required(login_url='login')
def dashboard(request):
    user = request.user
    today = date.today()
    
    # Fetch all expenses (user + shared)
    expenses = Expense.objects.filter(Q(user=user)).order_by('-date')

    # Totals
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_expenses = expenses.filter(date__month=today.month, date__year=today.year)\
                               .aggregate(Sum('amount'))['amount__sum'] or 0
    suggested_budget = float(monthly_expenses) * 1.2

    # 🔥 Always recalculate AI suggestion dynamically
    ai_suggestion = get_ai_budget_suggestion(user)

    context = {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'monthly_expenses': monthly_expenses,
        'suggested_budget': suggested_budget,
        'ai_suggestion': ai_suggestion,
    }

    return render(request, 'user_dashboard.html', context)



@login_required(login_url='login')
def add_expense(request):
    if request.method == "POST":
        title = request.POST['title']
        amount = request.POST['amount']
        category = request.POST['category']
        description = request.POST['description']
        visibility = request.POST.get('visibility', 'Private')

        Expense.objects.create(
            user=request.user,
            title=title,
            amount=amount,
            category=category,
            description=description,
            visibility=visibility
        )
        return redirect('user_dashboard')
    ai_suggestion = get_ai_budget_suggestion(request.user)

    return render(request, 'add_expense.html',{'ai_suggestion': ai_suggestion})
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    if request.method == "POST":
        expense.title = request.POST.get("title").capitalize()
        expense.amount = request.POST.get("amount")
        expense.date = request.POST.get("date")
        expense.category = request.POST.get("category")
        expense.save()
        return redirect("user_dashboard")  # redirect to dashboard after saving

    return render(request, "edit_expense.html", {"expense": expense})
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    if request.method == "POST":
        expense.delete()
        return redirect("user_dashboard") 

    
    return render(request, "delete_expense.html", {"expense": expense})
def logout_view(request):
    logout(request)  # Logs out the user
    return render(request, "home.html")
def admin_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:  # allow only staff/admin
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or not an admin.")
    
    return render(request, 'admin_login.html')
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from expenses.models import Expense
from django.db.models import Sum
import calendar
from datetime import datetime  # <-- import datetime
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q


def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url='admin_login')(view_func)


import json
from decimal import Decimal


@login_required(login_url='login')
@admin_required
def admin_dashboard(request):
    # Admin sees ALL expenses
    expenses = Expense.objects.all().order_by('-date')

    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Monthly expenses
    today = date.today()
    monthly_expenses = expenses.filter(date__month=today.month, date__year=today.year)\
                               .aggregate(Sum('amount'))['amount__sum'] or 0

    suggested_budget = float(monthly_expenses) * 1.2

    # Category-wise for chart
    category_labels = ['Food', 'Travel', 'Shopping', 'Bills', 'Other']
    category_values = [
        float(expenses.filter(category=cat).aggregate(Sum('amount'))['amount__sum'] or 0)
        for cat in category_labels
    ]

    # Monthly totals for chart
    monthly_labels = [calendar.month_abbr[i] for i in range(1, 13)]
    monthly_values = [
        float(expenses.filter(date__month=i, date__year=today.year).aggregate(Sum('amount'))['amount__sum'] or 0)
        for i in range(1, 13)
    ]
    total_users = User.objects.count() 

    context = {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'monthly_expenses': monthly_expenses,
        'suggested_budget': suggested_budget,
        'category_labels': json.dumps(category_labels),
        'category_values': json.dumps(category_values),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_values': json.dumps(monthly_values),
        'total_users': total_users,
    }
    return render(request, 'admin_dashboard.html', context)





@login_required(login_url='admin_login')
def manage_users(request):
    # Get all users ordered by username
    users = User.objects.all().order_by('username')
    return render(request, 'manage_users.html', {'users': users})


@login_required(login_url='admin_login')
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.is_active = True if request.POST.get('is_active') == 'on' else False
        user.save()
        messages.success(request, 'User updated successfully!')
        return redirect('manage_users')

    return render(request, 'edit_user.html', {'user': user})

@login_required(login_url='admin_login')
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully!')
    return redirect('manage_users')
@login_required(login_url='admin_login')
def manage_expenses(request):
    # Get all expenses ordered by date (latest first)
    expenses = Expense.objects.all().order_by('-date')
    return render(request, 'manage_expenses.html', {'expenses': expenses})
@login_required(login_url='admin_login')
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    if request.method == 'POST':
        expense.name = request.POST.get('name')
        expense.amount = request.POST.get('amount')
        expense.category = request.POST.get('category')
        expense.date = request.POST.get('date')
        expense.save()
        messages.success(request, 'Expense updated successfully!')
        return redirect('manage_expenses')

    return render(request, 'edit_expense.html', {'expense': expense})
@login_required(login_url='admin_login')
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    expense.delete()
    messages.success(request, 'Expense deleted successfully!')
    return redirect('manage_expenses')

import openpyxl

from django.http import HttpResponse

@login_required(login_url='admin_login')
@admin_required
def download_expense_report(request):
    # Create a workbook and select the active worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Expenses Report"

    # Add headers
    headers = ['ID', 'User', 'Title', 'Amount', 'Category', 'Date', 'Description', 'Visibility']
    ws.append(headers)

    # Fetch all expenses
    expenses = Expense.objects.all().order_by('-date')

    for exp in expenses:
        ws.append([
            exp.id,
            exp.user.username,
            exp.title,
            float(exp.amount),  # Convert Decimal to float
            exp.category,
            exp.date.strftime("%Y-%m-%d"),
            exp.description,
            getattr(exp, 'visibility', 'Private')  # if you have a visibility field
        ])

    # Prepare response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"Expense_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'

    # Save workbook to response
    wb.save(response)
    return response

def admin_logout(request):
    logout(request)
    return redirect('/')

