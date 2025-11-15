from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorViewSet, TimeSlotViewSet, AppointmentViewSet, RegisterView, LoginView, LogoutView, ProfileView, \
    DoctorReviewsView

router = DefaultRouter()
router.register('doctors', DoctorViewSet)
router.register('timeslots', TimeSlotViewSet)
router.register('appointments', AppointmentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/doctors/<int:doctor_id>/reviews/', DoctorReviewsView.as_view(), name='doctor-reviews'),
]
