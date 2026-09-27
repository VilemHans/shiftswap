from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Shift, ShiftRequest, Company, Profile

@login_required(login_url='login')
def dashboard(request):
    user_shifts = Shift.objects.filter(user=request.user).order_by('start_time')
    market_shifts = Shift.objects.filter(status='offered').exclude(user=request.user)
    
    # Žádosti o výměnu směn přihlášeného uživatele
    pending_requests = ShiftRequest.objects.filter(offered_by=request.user, status='pending')
    
    return render(request, 'core/dashboard.html', {
        'shifts': user_shifts,
        'market_shifts': market_shifts,
        'pending_requests': pending_requests
    })

@login_required(login_url='login')
def offer_shift(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id, user=request.user)
    shift.status = 'offered'
    shift.save()
    return redirect('dashboard')

@login_required(login_url='login')
def cancel_offer(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id, user=request.user, status='offered')
    shift.status = 'assigned'
    shift.save()
    # Smažeme případné čerstvé žádosti o tuto směnu
    ShiftRequest.objects.filter(shift=shift, status='pending').delete()
    return redirect('dashboard')

@login_required(login_url='login')
def request_shift(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id, status='offered')
    if shift.user != request.user:
        ShiftRequest.objects.get_or_create(
            shift=shift,
            offered_by=shift.user,
            accepted_by=request.user,
            status='pending'
        )
    return redirect('dashboard')

@login_required(login_url='login')
def approve_request(request, request_id):
    shift_request = get_object_or_404(ShiftRequest, id=request_id, offered_by=request.user)
    
    shift = shift_request.shift
    shift.user = shift_request.accepted_by
    shift.status = 'assigned'
    shift.save()

    shift_request.status = 'approved'
    shift_request.save()

    return redirect('dashboard')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')