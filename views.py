from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import Shift, ShiftRequest


@login_required(login_url='login')
def dashboard(request):
    user_shifts = Shift.objects.filter(user=request.user).order_by('start_time')
    market_shifts = Shift.objects.filter(status='offered').exclude(user=request.user)
    pending_requests = ShiftRequest.objects.filter(offered_by=request.user, status='pending')

    # IDs směn, o které již přihlášený uživatel zažádal a žádost čeká na schválení
    user_requested_shift_ids = set(
        ShiftRequest.objects.filter(
            accepted_by=request.user,
            status='pending'
        ).values_list('shift_id', flat=True)
    )

    for shift in market_shifts:
        shift.is_requested = shift.id in user_requested_shift_ids

    # Příprava událostí pro kalendář
    events = []

    # 1. Moje směny (modrá/indigo barva)
    for shift in user_shifts:
        events.append({
            'title': f"Moje směna ({shift.note or 'Bez poznámky'})",
            'start': shift.start_time.isoformat(),
            'end': shift.end_time.isoformat() if shift.end_time else None,
            'color': '#4f46e5',  # Indigo
        })

    # 2. Volné směny od kolegů z burzy (oranžová barva)
    for shift in market_shifts:
        is_req = shift.id in user_requested_shift_ids
        title_prefix = "⏳ Zažádáno" if is_req else "Volná"
        events.append({
            'title': f"{title_prefix}: {shift.user.username if shift.user else 'Kolega'}",
            'start': shift.start_time.isoformat(),
            'end': shift.end_time.isoformat() if shift.end_time else None,
            'color': '#f59e0b' if not is_req else '#d97706',  # Oranžová / sytější jantarová
            'textColor': '#ffffff'
        })

    return render(request, 'core/dashboard.html', {
        'shifts': user_shifts,
        'market_shifts': market_shifts,
        'user_requested_shift_ids': user_requested_shift_ids,
        'pending_requests': pending_requests,
        'calendar_events': events
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
def cancel_request(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id, status='offered')
    ShiftRequest.objects.filter(
        shift=shift,
        accepted_by=request.user,
        status='pending'
    ).delete()
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