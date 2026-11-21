from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from functools import wraps

from .models import Employee
from .forms import EmployeeForm, EmployeeUpdateForm
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q,Count
from django.core.paginator import Paginator

def boss_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Access denied")
        return view_func(request, *args, **kwargs)

    return login_required(wrapper)


@login_required
def dashboard(request):
    if request.user.is_superuser:
        employees = Employee.objects.all()

        # Search and filtering
        search_query = request.GET.get("q", "")
        selected_department = request.GET.get("department", "")

        if search_query:
            employees = employees.filter(
                Q(full_name__icontains=search_query)
                | Q(user__username__icontains=search_query)
            )

        if selected_department:
            employees = employees.filter(department=selected_department)

        # Department list
        departments = (
            Employee.objects.order_by("department")
            .values_list("department", flat=True)
            .distinct()
        )

        # Dashboard statistics
        total_employees = Employee.objects.count()

        total_departments = Employee.objects.values("department").distinct().count()

        recent_employees = Employee.objects.order_by("-created_at")[:5]

        department_stats = (
            Employee.objects.values("department")
            .annotate(employee_count=Count("id"))
            .order_by("department")
        )

        # Pagination
        paginator = Paginator(employees, 10)
        page_number = request.GET.get("page")
        employees = paginator.get_page(page_number)

        return render(
            request,
            "dashboard.html",
            {
                "employees": employees,
                "departments": departments,
                "search_query": search_query,
                "selected_department": selected_department,
                "total_employees": total_employees,
                "total_departments": total_departments,
                "recent_employees": recent_employees,
                "department_stats": department_stats,
            },
        )

    else:
        employee = Employee.objects.filter(user=request.user).first()

    return render(request, "employee_dashboard.html", {"employee": employee})


@boss_required
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)

        if form.is_valid():
            with transaction.atomic():

                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password']
                )

                employee = form.save(commit=False)
                employee.user = user
                employee.save()

            return redirect('dashboard')

    else:
        form = EmployeeForm()

    return render(request, 'add_employee.html', {
        'form': form
    })


@boss_required
def update_employee(request, id):
    employee = get_object_or_404(Employee, id=id)

    if request.method == 'POST':
        form = EmployeeUpdateForm(
            request.POST,
            instance=employee
        )

        if form.is_valid():
            employee = form.save(commit=False)

            employee.user.username = form.cleaned_data['username']
            employee.user.email = form.cleaned_data['email']

            with transaction.atomic():
                employee.user.save()
                employee.save()

            return redirect('dashboard')

        

    else:
        form = EmployeeUpdateForm(instance=employee)

    return render(request, 'update_employee.html', {
        'form': form
    })


@boss_required
def delete_employee(request, id):
    employee = get_object_or_404(Employee, id=id)

    if request.method == 'POST':

        if employee.user.is_superuser:
            return HttpResponseForbidden(
                "Administrator accounts cannot be deleted here."
            )

        user = employee.user
        user.delete()

        return redirect('dashboard')

    return render(request, 'delete_employee.html', {
        'employee': employee
    })


def custom_403(request, exception):
    return render(request, "403.html", status=403)


def custom_404(request, exception):
    return render(request, "404.html", status=404)
