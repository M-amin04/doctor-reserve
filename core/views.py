from django.contrib.auth import authenticate
from django.db.models import Count, Q
from rest_framework.authtoken.models import Token
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsOwnerOrReadOnly
from .serializers import *


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def time_slot(self, request, pk=None):
        doctor = self.get_object()
        time_slot = TimeSlot.objects.filter(doctor=doctor, is_available=True)
        ser = TimeSlotSerializer(time_slot, many=True)
        return Response(ser.data)


class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateAppointmentSerializer
        return AppointmentSerializer

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Appointment.objects.all()
        elif hasattr(user, 'doctor'):
            return Appointment.objects.filter(doctor=user.doctor)
        else:
            return Appointment.objects.filter(patient=user)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        required_fields = {
            'patient': {
                'required': ['username', 'password', 'email', 'user_type'],
                'optional': ['first_name', 'last_name', 'phone', 'national_code', 'date_of_birth']
            },
            'doctor': {
                'required': [
                    'username', 'password', 'email', 'user_type',
                    'specialization', 'phone', 'address', 'experience', 'fee'
                ],
                'optional': ['first_name', 'last_name', 'national_code']
            }
        }

        return Response({
            'message': 'فیلدهای لازم برای ثبت‌نام',
            'field_schema': required_fields,
            'specialization_choices': dict(Doctor.SPECIALIZATION_CHOICES)
        })

    def post(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        print("📨 داده‌های دریافتی:", request.data)

        user_type = request.data.get('user_type', 'patient')

        required_fields = {
            'patient': ['username', 'password', 'email', 'user_type'],
            'doctor': [
                'username', 'password', 'email', 'user_type',
                'specialization', 'phone', 'address', 'experience', 'fee'
            ]
        }

        fields_required = required_fields.get(user_type, required_fields['patient'])
        missing_fields = [field for field in fields_required if field not in request.data]

        if missing_fields:
            return Response({
                'error': f'فیلدهای الزامی: {", ".join(missing_fields)}',
                'missing_fields': missing_fields,
                'required_fields': fields_required
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_data = {
                'username': request.data['username'],
                'password': request.data['password'],
                'email': request.data['email'],
                'first_name': request.data.get('first_name', ''),
                'last_name': request.data.get('last_name', ''),
                'phone': request.data.get('phone', ''),
                'national_code': request.data.get('national_code', ''),
                'user_type': user_type
            }

            if 'date_of_birth' in request.data:
                from datetime import datetime
                user_data['date_of_birth'] = datetime.strptime(
                    request.data['date_of_birth'], '%Y-%m-%d'
                ).date()

            user = User.objects.create_user(**user_data)

            if user.user_type == 'doctor':
                doctor_data = {
                    'user': user,
                    'specialization': request.data['specialization'],
                    'phone': request.data['phone'],
                    'address': request.data['address'],
                    'experience': int(request.data['experience']),
                    'fee': float(request.data['fee'])
                }
                Doctor.objects.create(**doctor_data)

            token, created = Token.objects.get_or_create(user=user)

            response_data = {
                'success': True,
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': user.user_type,
                    'phone': user.phone
                },
                'message': 'ثبت‌نام موفقیت‌آمیز بود'
            }

            if user.user_type == 'doctor':
                doctor = Doctor.objects.get(user=user)
                response_data['doctor_info'] = {
                    'specialization': doctor.get_specialization_display(),
                    'experience': doctor.experience,
                    'fee': doctor.fee
                }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"❌ خطا: {str(e)}")
            return Response({
                'error': str(e),
                'required_fields': required_fields.get(user_type)
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            })
        else:
            return Response(
                {'error': 'Incorrect username or password!'},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'exit is success'})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        })

    def put(self, request):
        user = request.user
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        user.save()

        return Response({
            'message': 'update profile has be success',
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        })


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateReviewSerializer
        return ReviewSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Review.objects.all()
        return Review.objects.filter(is_approved=True)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        if not self.request.user.is_patient:
            raise PermissionDenied("فقط بیماران می‌توانند نظر دهند")

        serializer.save(patient=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        review = self.get_object()
        review.is_approved = True
        review.save()

        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        review = self.get_object()
        return Response({'message': 'نظر پسندیده شد'})


class DoctorReviewsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, doctor_id):
        try:
            doctor = Doctor.objects.get(id=doctor_id)

            reviews_stats = Review.objects.filter(
                doctor=doctor,
                is_approved=True
            ).aggregate(
                total_reviews=Count('id'),
                average_rating=Avg('rating'),
                five_star=Count('id', filter=Q(rating=5)),
                four_star=Count('id', filter=Q(rating=4)),
                three_star=Count('id', filter=Q(rating=3)),
                two_star=Count('id', filter=Q(rating=2)),
                one_star=Count('id', filter=Q(rating=1)),
            )

            reviews = Review.objects.filter(
                doctor_id=doctor_id,
                is_approved=True
            ).order_by('-created_at')

            serializer = ReviewSerializer(reviews, many=True)

            return Response({
                'doctor': {
                    'id': doctor.id,
                    'name': doctor.user.get_full_name(),
                    'specialization': doctor.get_specialization_display()
                },
                'stats': reviews_stats,
                'reviews': serializer.data
            })

        except Doctor.DoesNotExist:
            return Response(
                {'error': 'دکتر یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )


class DoctorRatingStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, doctor_id):
        try:
            doctor = Doctor.objects.get(id=doctor_id)

            stats = Review.objects.filter(
                doctor=doctor,
                is_approved=True
            ).aggregate(
                total_reviews=Count('id'),
                average_rating=Avg('rating'),
                rating_breakdown=Count('rating')
            )

            rating_details = []
            for i in range(1, 6):
                count = Review.objects.filter(
                    doctor=doctor,
                    rating=i,
                    is_approved=True
                ).count()
                rating_details.append({
                    'stars': i,
                    'count': count,
                    'percentage': round((count / stats['total_reviews']) * 100, 1) if stats['total_reviews'] > 0 else 0
                })

            return Response({
                'doctor': {
                    'id': doctor.id,
                    'name': doctor.user.get_full_name(),
                    'specialization': doctor.get_specialization_display()
                },
                'stats': {
                    'total_reviews': stats['total_reviews'],
                    'average_rating': round(stats['average_rating'] or 0, 1),
                    'rating_breakdown': rating_details
                }
            })

        except Doctor.DoesNotExist:
            return Response(
                {'error': 'دکتر یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
