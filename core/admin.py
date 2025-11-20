from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Doctor, TimeSlot, Appointment, Review, CustomUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_type', 'is_verified', 'is_active']
    list_filter = ['user_type', 'is_verified', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'national_code']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'national_code', 'date_of_birth')
        }),
        (_('Permissions'), {
            'fields': (
            'user_type', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'phone'),
        }),
    )




@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'phone', 'experience', 'fee']
    list_filter = ['specialization', 'experience']
    search_fields = ['user__first_name', 'user__last_name', 'specialization']
    ordering = ['user__last_name']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time', 'is_available', 'max_patients']
    list_filter = ['day_of_week', 'is_available', 'doctor__specialization']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name']
    list_editable = ['is_available', 'max_patients']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'appointment_time', 'status', 'is_urgent', 'created_at']
    list_filter = ['status', 'appointment_date', 'is_urgent', 'doctor__specialization']
    search_fields = [
        'patient__first_name', 'patient__last_name',
        'doctor__user__first_name', 'doctor__user__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'appointment_date'
    actions = ['confirm_appointments', 'cancel_appointments', 'mark_completed']

    def confirm_appointments(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} نوبت تایید شد')

    confirm_appointments.short_description = 'تایید نوبت‌های انتخاب شده'

    def cancel_appointments(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} نوبت لغو شد')

    cancel_appointments.short_description = 'لغو نوبت‌های انتخاب شده'

    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} نوبت انجام شده标记 شد')

    mark_completed.short_description = '标记 نوبت‌های انتخاب شده как انجام شده'

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
    list_display = ['doctor_name', 'rating_stars', 'is_approved', 'created_at', 'has_appointment']
    list_filter = ['rating', 'is_approved', 'doctor__specialization', 'created_at']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name', 'comment']
    readonly_fields = ['created_at']
    actions = ['approve_reviews', 'disapprove_reviews']
    list_editable = ['is_approved']


    def doctor_name(self, obj):
        return obj.doctor.user.get_full_name()
    doctor_name.short_description = 'دکتر'

    def rating_stars(self, obj):
        return '⭐' * obj.rating
    rating_stars.short_description = 'امتیاز'

    def has_appointment(self, obj):
        return obj.appointment is not None
    has_appointment.short_description = 'دارای نوبت'
    has_appointment.boolean = True

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} نظر تایید شد')
    approve_reviews.short_description = 'تایید نظرات انتخاب شده'

    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} نظر رد شد')
    disapprove_reviews.short_description = 'رد نظرات انتخاب شده'