# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Attendance, Profile, Leave, Holiday, Task, WorkLog
from home.serializers import UserSerializer


User = get_user_model()

# class UserSerializer(serializers.ModelSerializer):
#     uid = serializers.CharField(read_only=True)

#     class Meta:
#         model = User
#         fields = [
#             'uid', 'username', 'email', 'role',
#             'first_name', 'last_name', 'password'
#         ]
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         password = validated_data.pop('password')
#         user = User(**validated_data)
#         user.set_password(password)
#         user.is_active = True
#         user.save()                # <-- **SAVE** the instance
#         return user


class WorkLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkLog
        fields = '__all__'
        read_only_fields = ['user', 'date', 'check_in', 'check_out']


class AttendanceSerializer(serializers.ModelSerializer):
    late_minutes = serializers.IntegerField(read_only=True)
    working_hours = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            'uid', 'date', 'check_in', 'check_out',
            'status', 'late_minutes', 'working_hours'
        ]

    def get_working_hours(self, obj):
        if obj.working_hours:
            total = obj.working_hours.total_seconds()
            h = int(total // 3600)
            m = int((total % 3600) // 60)
            return f"{h}:{m:02}"
        return "0:00"



class AttendanceByDateSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()  # ← Use method
    working_hours = serializers.DurationField(read_only=True)

    class Meta:
        model = Attendance
        fields = ['user', 'full_name', 'date', 'check_in', 'check_out', 'status', 'working_hours']

    def get_full_name(self, obj):
        profile = obj.user.profile
        return (
            profile.full_name or 
            obj.user.get_full_name() or 
            obj.user.username
        )

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    delete_code = serializers.CharField(read_only=True)
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            # System
            'id',
            'slug',
            'delete_code',

            # User
            'user',

            # Basic Info
            'full_name',
            'phone',
            'department',
            'designation',
            'join_date',

            # Contact Information (NEW)
            'email',
            'address',
            'reports_to',

            # Skills & Education (NEW)
            'education',
            'skills',
        ]

        extra_kwargs = {
            'delete_code': {'read_only': True},
            'slug': {'read_only': True},
            'user': {'read_only': True},
        }

    def get_skills(self, obj):
        """
        Return skills as a list instead of comma-separated string
        """
        return obj.skill_list()


class LeaveSerializer(serializers.ModelSerializer):
    total_days = serializers.ReadOnlyField()

    class Meta:
        model = Leave
        fields = [
            'id',
            'leave_type',
            'start_date',
            'end_date',
            'total_days',
            'status',
            'created_at',
            'reason'
        ]

    def validate(self, data):
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError(
                {"end_date": "End date cannot be before start date"}
            )
        return data




class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = "__all__"
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'date': {'required': True}
        }

working_hours = serializers.SerializerMethodField()
def get_working_hours(self, obj):
  if obj.working_hours:
    hours = obj.working_hours.total_seconds() // 3600
    mins = (obj.working_hours.total_seconds() // 60) % 60
    secs = obj.working_hours.total_seconds() % 60
    return f"{int(hours):02}:{int(mins):02}:{int(secs):02}"
  return "00:00:00"




# accounts/serializers.py (final version – accept username as string)

# -------------------------------------------------
# TaskSerializer – username only
# -------------------------------------------------
class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    created_by_name  = serializers.SerializerMethodField()

    # Accept username string in request, but internally map to User object
    assigned_to = serializers.CharField(write_only=True)

    class Meta:
        model = Task
        fields = [
            'uid', 'title', 'description',
            'assigned_to', 'assigned_to_name',
            'created_by_name', 'created_at', 'due_date', 'status'
        ]

    def validate_assigned_to(self, username):
        username = username.strip()
        try:
            return User.objects.get(username__iexact=username, role='staff')
        except User.DoesNotExist:
            available = list(User.objects.filter(role='staff').values_list('username', flat=True))
            raise serializers.ValidationError(
                f"Staff user '{username}' not found. Available staff: {available}"
            )

    def create(self, validated_data):
        # assigned_to will already be the User object from validate_assigned_to
        return Task.objects.create(**validated_data)

    def get_assigned_to_name(self, obj):
        if not obj.assigned_to:
            return "Unassigned"
        profile = obj.assigned_to.profile
        return profile.full_name or obj.assigned_to.get_full_name() or obj.assigned_to.username

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return "Unknown"
        profile = obj.created_by.profile
        return profile.full_name or obj.created_by.get_full_name() or obj.created_by.username


    