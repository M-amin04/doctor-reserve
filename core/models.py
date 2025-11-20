from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('patient', 'بیمار'),
        ('doctor', 'دکتر'),
        ('admin', 'ادمین'),
    )

    phone = models.CharField(max_length=15, blank=True, verbose_name='تلفن')
    national_code = models.CharField(max_length=12, blank=True, verbose_name='کد ملی')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='تاریخ تولد')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='patient', verbose_name='نوع کاربر')
    is_verified = models.BooleanField(default=False, verbose_name='تایید شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return f'{self.get_full_name()} - {self.get_user_type_display()}'

    @property
    def is_patient(self):
        return self.user_type == 'patient'

    @property
    def is_doctor(self):
        return self.user_type == 'doctor'


class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ('cardiologist', 'قلب و عروق'),
        ('dentist', 'دندانپزشک'),
        ('dermatologist', 'پوست و مو'),
        ('pediatrician', 'کودکان'),
        ('orthopedist', 'ارتوپد'),
        ('neurologist', 'مغز و اعصاب'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'doctor'})
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    experience = models.IntegerField(help_text='سال های تجربه')
    fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'دکتر'
        verbose_name_plural = 'دکترها'

    @property
    def average_rating(self):
        reviews = Review.objects.filter(doctor=self, is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(Avg('rating'))['rating__avg'], 1)
        return 0

    @property
    def total_reviews(self):
        return Review.objects.filter(doctor=self, is_approved=True).count()

    def __str__(self):
        return f'Dr. {self.user.first_name} {self.user.last_name}'


class TimeSlot(models.Model):
    DAY_OF_WEEK = [
        (0, 'شنبه'), (1, 'یکشنبه'), (2, 'دوشنبه'),
        (3, 'سه شنبه'), (4, 'چهارشنبه'), (5, 'پنجشنبه'), (6, 'جمعه')
    ]
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='timeslot', verbose_name='دکتر')
    day_of_week = models.IntegerField(choices=DAY_OF_WEEK, verbose_name='روز هفته')
    start_time = models.TimeField(verbose_name='ساعت شروع')
    end_time = models.TimeField(verbose_name='ساعت پایان')
    is_available = models.BooleanField(default=True, verbose_name='فعال')
    max_patients = models.PositiveIntegerField(default=1, verbose_name='حداکثر بیماران',help_text='حداکثر تعداد بیمار در این بازه زمانی')

    class Meta:
        verbose_name = 'بازه زمانی'
        verbose_name_plural = 'بازه‌های زمانی'
        unique_together = ['doctor', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']
        indexes = [
            models.Index(fields=['doctor', 'day_of_week', 'is_available']),
            models.Index(fields=['day_of_week', 'is_available']),
        ]

    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')}"

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('ساعت شروع باید قبل از ساعت پایان باشد')
        overlapping_slots = TimeSlot.objects.filter(doctor=self.doctor, day_of_week=self.day_of_week, is_available=True).exclude(pk=self.pk)

        for slot in overlapping_slots:
            if (self.start_time < slot.end_time and self.end_time > slot.start_time):
                raise ValidationError(f'این بازه زمانی با بازه {slot} تداخل دارد')

        @property
        def duration(self):
            from datetime import datetime, timedelta
            start = datetime.combine(timezone.now().date(), self.start_time)
            end = datetime.combine(timezone.now().date(), self.end_time)
            return end - start

        @property
        def is_active(self):
            return self.is_available and self.doctor.user.is_active

        def get_available_slots(self, date):
            from .models import Appointment
            appointments_count = Appointment.objects.filter(time_slot=self, appointment_date=date, status__in=['pending', 'confirmed']).count()
            return self.max_patients - appointments_count


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار تایید'),
        ('confirmed', 'تایید شده'),
        ('cancelled', 'لغو شده'),
        ('completed', 'تمام شده'),
        ('no_show', 'حاضر نشده'),
    ]

    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='appointments', verbose_name='بیمار',
                                limit_choices_to={'user_type': 'patient'})
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appoitments', verbose_name='دکتر')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='appointments',
                                  verbose_name='بازه زمانی')
    appointment_date = models.DateField(verbose_name='تاریخ نوبت')
    appointment_time = models.TimeField(verbose_name='ساعت نوبت')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    symptoms = models.TextField(blank=True, null=True, verbose_name='علائم بیماری', help_text='علائم و توضیحات بیمار')
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌های دکتر')
    prescription = models.TextField(blank=True, null=True, verbose_name='نسخه پزشکی')
    is_urgent = models.BooleanField(default=False, verbose_name='اورژانسی')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')

    class Meta:
        verbose_name = 'نوبت'
        verbose_name_plural = 'نوبت‌ها'
        unique_together = ['doctor', 'appointment_date', 'appointment_time']
        ordering = ['-appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['patient', 'appointment_date']),
            models.Index(fields=['doctor', 'appointment_date', 'status']),
            models.Index(fields=['appointment_date', 'status']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(appointment_date__gte=timezone.now().date()), name='appointment_date_future')]

    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.doctor.user.get_full_name()} - {self.appointment_date}"

    def clean(self):
        if self.appointment_date < timezone.now().date():
            raise ValidationError('تاریخ نوبت نمی‌تواند در گذشته باشد')

        if self.time_slot.doctor != self.doctor:
            raise ValidationError('بازه زمانی انتخاب شده متعلق به این دکتر نیست')

        if not self.time_slot.is_available:
            raise ValidationError('این بازه زمانی در دسترس نیست')

        conflicting_appointments = Appointment.objects.filter(
            doctor=self.doctor,
            appointment_date=self.appointment_date,
            appointment_time=self.appointment_time,
            status__in=['pending', 'confirmed']
        ).exclude(pk=self.pk)

        if conflicting_appointments.exists():
            raise ValidationError('این زمان قبلاً رزرو شده است')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_upcoming(self):
        now = timezone.now()
        appointment_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        return appointment_datetime > now and self.status in ['pending', 'confirmed']

    @property
    def is_past(self):
        return not self.is_upcoming

    @property
    def can_cancel(self):
        appointment_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        return (appointment_datetime - timezone.now() > timedelta(hours=2) and
                self.status in ['pending', 'confirmed'])

    @property
    def duration_minutes(self):
        return 30

    def get_appointment_datetime(self):
        return datetime.combine(self.appointment_date, self.appointment_time)

    def confirm(self):
        if self.status == 'pending':
            self.status = 'confirmed'
            self.save()

    def cancel(self, reason=None):
        if self.status in ['pending', 'confirmed']:
            self.status = 'cancelled'
            if reason:
                self.notes = f"لغو شده: {reason}\n{self.notes or ''}"
            self.save()

    def complete(self, prescription=None, notes=None):
        if self.status == 'confirmed':
            self.status = 'completed'
            if prescription:
                self.prescription = prescription
            if notes:
                self.notes = notes
            self.save()


class Review(models.Model):
    RATING_CHOICES = [
        (1, '۱ ستاره'),
        (2, '۲ ستاره'),
        (3, '۳ ستاره'),
        (4, '۴ ستاره'),
        (5, '۵ ستاره'),
    ]

    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='بیمار')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name='دکتر')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True, verbose_name='نوبت')
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='امتیاز')
    comment = models.TextField(blank=True, null=True, verbose_name='نظر')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ساخته شده')
    is_approved = models.BooleanField(default=False, verbose_name='تایید')

    class Meta:
        unique_together = ['patient', 'doctor', 'appointment']
        verbose_name = 'نظر و امتیاز'
        verbose_name_plural = 'نظرات و امتیازها'

    def __str__(self):
        return f'{self.patient.get_full_name()} - {self.doctor.user.get_full_name()} - {self.rating} ستاره'

    def clean(self):
        if self.patient and self.doctor:
            has_appointment = Appointment.objects.filter(
                patient=self.patient,
                doctor=self.doctor,
                status='completed'
            ).exists()

            if not has_appointment:
                raise ValidationError('شما فقط می‌توانید برای دکترهایی که نوبت داشته‌اید نظر دهید')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
