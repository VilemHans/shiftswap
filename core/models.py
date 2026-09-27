from django.db import models
from django.contrib.auth.models import User

# Model pro firmu / provozovnu
class Company(models.Model):
    name = models.CharField(max_length=100, verbose_name="Název provozovny")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Rozšíření profilu uživatele o firmu a roli
class Profile(models.Model):
    ROLE_CHOICES = (
        ('manager', 'Manažer'),
        ('employee', 'Zaměstnanec'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

# Model pro Směnu
class Shift(models.Model):
    STATUS_CHOICES = (
        ('assigned', 'Přiřazeno'),
        ('offered', 'Nabídnuto k výměně'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shifts')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    start_time = models.DateTimeField(verbose_name="Začátek směny")
    end_time = models.DateTimeField(verbose_name="Konec směny")
    note = models.TextField(blank=True, verbose_name="Poznámka")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')

    def __str__(self):
        return f"Směna: {self.user.username} ({self.start_time.strftime('%d.%m. %H:%M')})"

# Model pro Žádost o výměnu
class ShiftRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Čeká na schválení manažerem'),
        ('approved', 'Schváleno'),
        ('rejected', 'Zamítnuto'),
    )
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    offered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offered_requests')
    accepted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accepted_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Žádost o výměnu: {self.shift} -> pro {self.accepted_by.username}"