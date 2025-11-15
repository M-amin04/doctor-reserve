from rest_framework.fields import SerializerMethodField, ReadOnlyField
from rest_framework.serializers import ModelSerializer
from .models import Doctor, TimeSlot, Appointment, Review
from django.contrib.auth.models import User



class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


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

    class Meta:
        model = Review
        fields = '__all__'

    def get_patient_name(self, obj):
        return f'{obj.patient.first_name} {obj.patient.last_name}'


class CreateReviewSerializer(ModelSerializer):
    class Meta:
        model = Review
        fields = ['doctor', 'appointment', 'rating', 'comment']


class DoctorWithRatingSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    average_rating = ReadOnlyField()
    total_reviews = ReadOnlyField()

    class Meta:
        model = Doctor
        fields = '__all__'