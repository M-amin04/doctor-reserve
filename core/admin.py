from django.contrib import admin
from .models import Doctor, TimeSlot, Appointment, Review
from django.db.models import Count
from django.utils import timezone

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'phone', 'experience', 'fee']
    list_filter = ['specialization', 'experience']
    search_fields = ['user__first_name', 'user__last_name', 'specialization']
    ordering = ['user__last_name']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available', 'doctor__specialization']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'appointment_time', 'status']
    list_filter = ['status', 'appointment_date', 'doctor__specialization']
    search_fields = [
        'patient__username',
        'patient__first_name',
        'patient__last_name',
        'doctor__user__first_name',
        'doctor__user__last_name'
    ]
    date_hierarchy = 'appointment_date'
    actions = ['confirm_appointments', 'cancel_appointments']

    def confirm_appointments(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f"{queryset.count()} نوبت تایید شد")

    confirm_appointments.short_description = "تایید نوبت‌های انتخاب شده"

    def cancel_appointments(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} نوبت لغو شد")

    cancel_appointments.short_description = "لغو نوبت‌های انتخاب شده"

    def changelist_view(self, request, extra_context=None):
        today = timezone.now().date()
        stats = {
            'total_appointments': Appointment.objects.count(),
            'today_appointments': Appointment.objects.filter(appointment_date=today).count(),
            'pending_appointments': Appointment.objects.filter(status='pending').count(),
            'confirmed_appointments': Appointment.objects.filter(status='confirmed').count(),
        }

        extra_context = extra_context or {}
        extra_context['stats'] = stats
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'doctor__specialization']
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} نظر تایید شد")

    approve_reviews.short_description = "تایید نظرات انتخاب شده"