from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg


class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ('cardiologist', 'قلب و عروق'),
        ('dentist', 'دندانپزشک'),
        ('dermatologist', 'پوست و مو'),
        ('pediatrician', 'کودکان'),
        ('orthopedist', 'ارتوپد'),
        ('neurologist', 'مغز و اعصاب'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    experience = models.IntegerField(help_text='سال های تجربه')
    fee = models.DecimalField(max_digits=10, decimal_places=2)

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
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAY_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.doctor} - {self.get_day_of_week_display()} {self.start_time}'


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('confirmed', 'تایید شده'),
        ('cancelled', 'لغو شده'),
        ('completed', 'تمام شده'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    symptoms = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.patient.username} - Dr.{self.doctor.user.last_name}'


class Review(models.Model):
    RATING_CHOICES = [
        (1, '۱ ستاره'),
        (2, '۲ ستاره'),
        (3, '۳ ستاره'),
        (4, '۴ ستاره'),
        (5, '۵ ستاره'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ['patient', 'doctor', 'appointment']

    def __str__(self):
        return f'{self.patient.username} - {self.doctor.user.last_name} - {self.rating} star'
