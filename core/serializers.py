from rest_framework.fields import SerializerMethodField, ReadOnlyField, CharField
from rest_framework.serializers import ModelSerializer
from .models import *
from django.contrib.auth import get_user_model


User = get_user_model()


class UserSerializer(ModelSerializer):
    user_type_display = CharField(source='get_user_type_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'national_code', 'user_type', 'user_type_display',
            'is_verified', 'date_joined'
        ]
        read_only_fields = ['date_joined']



class DoctorSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = '__all__'


class TimeSlotSerializer(ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'


class AppointmentSerializer(ModelSerializer):
    patient = UserSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'


class CreateAppointmentSerializer(ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'symptoms']


class ReviewSerializer(ModelSerializer):
    patient = UserSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    patient_name = SerializerMethodField()
    rating_display = SerializerMethodField()
    can_edit = SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'

    def get_patient_name(self, obj):
        return f'{obj.patient.first_name} {obj.patient.last_name}'

    def get_rating_display(self, obj):
        return f'{obj.rating} ستاره'

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user == obj.patient:
            return True
        return False


class CreateReviewSerializer(ModelSerializer):
    class Meta:
        model = Review
        fields = ['doctor', 'appointment', 'rating', 'comment']

    def validate(self, data):
        patient = self.context['request'].user
        doctor = data.get('doctor')
        appointment = data.get('appointment')

        if appointment and appointment.patient != patient:
            raise ValidationError("این نوبت متعلق به شما نیست")

        existing_review = Review.objects.filter(
            patient=patient,
            doctor=doctor,
            appointment=appointment
        ).exists()

        if existing_review:
            raise ValidationError("شما قبلاً برای این نوبت نظر داده‌اید")
        return data


class DoctorWithRatingSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    average_rating = ReadOnlyField()
    total_reviews = ReadOnlyField()

    class Meta:
        model = Doctor
        fields = '__all__'


