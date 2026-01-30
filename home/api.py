from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, permissions, filters, generics, views
from django_filters import rest_framework as django_filters
from datetime import date
from datetime import datetime, timedelta
from rest_framework import status, viewsets

# from CRM import accounts
from .serializers import *
from .models import *
from django.shortcuts import render
from django.shortcuts import get_object_or_404
import random
import string
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import TokenAuthentication
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.db.models import Sum
from django.utils import timezone
from calendar import month_name
from calendar import monthrange, monthcalendar, day_name
import calendar
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
import pandas as pd
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.timezone import localtime
from django.core.exceptions import FieldError

from django.http import Http404
from rest_framework.authentication import BasicAuthentication


from django.db.models import Sum, IntegerField
from django.db.models.functions import Cast
from django.db.models import Prefetch

import logging

from rest_framework import permissions
from django.utils.timezone import localtime
from django.utils.timezone import make_aware
from django.utils.timezone import get_current_timezone


from rest_framework.permissions import BasePermission
from django.apps import apps
from accounts import models
from accounts.models import Leave, Profile, Holiday, UserLocation


logger = logging.getLogger(__name__)
User = apps.get_model('home', 'User')



class IsLeadOwnerOrAdminOrTeamLeader(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False
        
      
        if user.is_superuser:
            return True
        
        # Allow admin, TL, staff to change status
        if getattr(user, "is_admin", False):
            return True
        
        if getattr(user, "is_team_leader", False):
            return True
        
        if getattr(user, "is_staff_new", False):
            return True

        return False

from rest_framework.permissions import BasePermission

class IsOnlyAdminUser(BasePermission):
    """
    Allow access only to users with is_admin==True and NOT superuser.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # Allow only if is_admin True AND is_superuser False
        return getattr(user, "is_admin", False) and not getattr(user, "is_superuser", False)


class MarketingAccessPermission(BasePermission):
    """
    Allow access to: Superuser, Admin, Team Leader, Staff.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False
        
        # Allowed roles
        if user.is_superuser:
            return True
        if getattr(user, "is_admin", False):
            return True
        if getattr(user, "is_team_leader", False):
            return True
        if getattr(user, "is_staff_new", False):
            return True
        
        return False



# @method_decorator(csrf_exempt, name='dispatch')
# class LoginApiView(APIView):

#     permission_classes = [AllowAny]

#     @swagger_auto_schema(
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username or Email'),
#                 'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
#             },
#             required=['username', 'password'],
#         ),
#         responses={
#             200: 'Login successful',
#             400: 'Invalid input or credentials'
#         }
#     )

#     def post(self, request):
#         res = {}
#         username = request.data.get("username", None)
#         password = request.data.get("password", None)

#         if username is None:
#             res['status'] = False
#             res['message'] = "Email is required"
#             res['data'] = []
#             return Response(res, status=status.HTTP_400_BAD_REQUEST)

#         if password is None:
#             res['status'] = False
#             res['message'] = "Password is required"
#             res['data'] = []
#             return Response(res, status=status.HTTP_400_BAD_REQUEST)

#         user = authenticate(username=username, password=password)
#         user.is_user_login = True
#         user.save()
#         if not user.is_staff_new:
#             res['status'] = False
#             res['message'] = "Only satff user allowed to login!"
#             res['data'] = []
#             return Response(res, status=status.HTTP_400_BAD_REQUEST)
#         if user is None:
#             res['status'] = False
#             res['message'] = "Invalid Email or Password!"
#             res['data'] = []
#             return Response(res, status=status.HTTP_400_BAD_REQUEST)
#         serializer = UserSerializer(
#             user, read_only=True, context={'request': request})
#         if serializer:
#             res['status'] = True
#             res['message'] = "Authenticated successfully"
#             res['data'] = serializer.data
#             return Response(res, status=status.HTTP_200_OK)

#         else:
#             res['status'] = False
#             res['message'] = "No recored found for entered data"
#             res['data'] = []
#             return Response(res, status=status.HTTP_400_BAD_REQUEST)




class IsCustomStaffUser(permissions.BasePermission):
    """
    Custom permission to only allow users with is_staff_new=True.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff_new
    


class IsCustomAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow users with is_admin=True.
    """
    def has_permission(self, request, view):
        
        return request.user and request.user.is_authenticated and request.user.is_admin
    

    
class CustomIsSuperuser(permissions.BasePermission):
    """
    Custom permission to only allow Superusers.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser  
      


class IsCustomTeamLeaderUser(permissions.BasePermission):
    """
    Allows access only to Team Leader users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_team_leader)
    


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000



class ActivityLogPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500



class IsManagerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admins, superusers, or team leaders.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_superuser or 
             request.user.is_admin or 
             request.user.is_team_leader)
        )



# LOGIN API VIEW [MANUAL AUTH]

@method_decorator(csrf_exempt, name='dispatch')
class LoginApiView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username or Email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
            required=['username', 'password'],
        ),
        responses={
            200: 'Login successful',
            400: 'Invalid input or credentials'
        }
    )
    def post(self, request):
        username_or_email = request.data.get("username", None)
        password = request.data.get("password", None)

        if not username_or_email or not password:
            return Response(
                {'status': False, 'message': 'Username and Password are required', 'data': []}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            
            user = User.objects.get(email=username_or_email)
        except User.DoesNotExist:
            
            try:
                user = User.objects.get(username=username_or_email)
            except User.DoesNotExist:
               
                return Response(
                    {'status': False, 'message': 'Invalid username or password', 'data': []}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not user.check_password(password):
            return Response(
                {'status': False, 'message': 'Invalid username or password', 'data': []}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.is_superuser:
            if user.user_active is False:
                return Response(
                    {'status': False, 'message': "Your account is inactive. Please contact admin.", 'data': []}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not (user.is_admin or user.is_team_leader or user.is_staff_new or user.is_it_staff):
                 return Response(
                    {'status': False, 'message': "User role not defined for API access.", 'data': []}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        user.is_user_login = True
        user.save()

        serializer = UserSerializer(user, read_only=True, context={'request': request})
        
        return Response(
            {'status': True, 'message': 'Authenticated successfully', 'data': serializer.data}, 
            status=status.HTTP_200_OK
        )
    

        
class staff_assigned_leads(APIView):
    """
    API to retrieve assigned leads and performance statistics for the logged-in staff.
    """

    permission_classes = [IsAuthenticated , CustomIsSuperuser]

    def get(self, request):
        
        res = {}
        staff = request.user
        staff_instance = Staff.objects.filter(email=staff.email).last()
        myleads = LeadUser.objects.filter(status="Leads", assigned_to=staff_instance,)

        serializer = StaffAssignedSerializer(myleads, many=True)

        
        today = timezone.now().date()
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            start_date = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)) - timedelta(seconds=1)
        else:
            start_date = timezone.make_aware(datetime.combine(today, datetime.min.time()))
            end_date = timezone.make_aware(datetime.combine(today, datetime.max.time()))

        lead_filter = {'updated_date__range': [start_date, end_date]}

        leads = LeadUser.objects.filter(status="Leads", assigned_to=staff_instance)
        interested = LeadUser.objects.filter(status="Intrested", assigned_to=staff_instance, **lead_filter)
        not_interested = LeadUser.objects.filter(status="Not Interested", assigned_to=staff_instance, **lead_filter)
        other_location = LeadUser.objects.filter(status="Other Location", assigned_to=staff_instance, **lead_filter)
        not_picked = LeadUser.objects.filter(status="Not Picked", assigned_to=staff_instance, **lead_filter)
        lost = LeadUser.objects.filter(status="Lost", assigned_to=staff_instance, **lead_filter)
        visits = LeadUser.objects.filter(status="Visit", assigned_to=staff_instance, **lead_filter)

        total_leads = leads.count()
        total_interested_leads = interested.count()
        total_not_interested_leads = not_interested.count()
        total_other_location_leads = other_location.count()
        total_not_picked_leads = not_picked.count()
        total_lost_leads = lost.count()
        total_visits_leads = visits.count()
        total_calls = total_interested_leads + total_not_interested_leads + total_other_location_leads + total_not_picked_leads + total_lost_leads + total_visits_leads

        whatsapp_marketing = Marketing.objects.filter(source="whatsapp", user=request.user).last()
        projects = Project.objects.all()

        leads_data = LeadUserSerializer(leads, many=True).data
        whatsapp_marketing_data = MarketingSerializer(whatsapp_marketing).data if whatsapp_marketing else None
        projects_data = ProjectSerializer(projects, many=True).data

        data1 = {
            'total_calls': total_calls,
            'total_leads': total_leads,
            'total_interested_leads': total_interested_leads,
            'total_not_interested_leads': total_not_interested_leads,
            'total_other_location_leads': total_other_location_leads,
            'total_not_picked_leads': total_not_picked_leads,
            'total_lost_leads': total_lost_leads,
            'total_visits_leads': total_visits_leads,
            'whatsapp_marketing': whatsapp_marketing_data,
            'projects': projects_data,}


        res['status'] = True
        res['message'] = "leads are retrived succefully"
        res['data'] = serializer.data
        res['other_data'] = data1
        return Response(res, status=status.HTTP_200_OK)
    


class StatusUpdateAPIView(APIView):
    """
    API to update the status of a specific lead and record the activity history.
    """
    permission_classes = [IsAuthenticated  ]

    def post(self, request):
        res = {}
        data = {}

        merchant_id = request.data.get('leads_id')
        new_status = request.data.get('new_status')
        remark = request.data.get('remark')
        follow_up_date = request.data.get('follow_up_date')
        follow_up_time = request.data.get('follow_up_time')

        if merchant_id is None:
            res['status'] = False
            res['message'] = "lead id is required"
            res['data'] = []
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        
        if new_status is None:
            res['status'] = False
            res['message'] = "status is required"
            res['data'] = []
            return Response(res, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_superuser:
            user_type = "Super User"
        elif request.user.is_admin:
            user_type = "Admin User"
        elif request.user.is_team_leader:
            user_type = "Team Leader User"
        elif request.user.is_staff_new:
            user_type = "Staff User"

        if merchant_id and new_status:
            try:
                status_update_user = LeadUser.objects.get(id=merchant_id)
                previous_status = status_update_user.status

                tagline = f"Lead status changed from {previous_status} to {new_status} by user[Email: {request.user.email}, {user_type}]"
                status_update_user.status = new_status
                status_update_user.message = remark

                if new_status == 'Intrested':
                    if follow_up_date:
                        status_update_user.follow_up_date = follow_up_date
                    if follow_up_time:
                        status_update_user.follow_up_time = follow_up_time

                status_update_user.save()
                data['id'] = status_update_user.id
                data['status'] = status_update_user.status
                data['follow_up_date'] = status_update_user.follow_up_date
                data['follow_up_time'] = status_update_user.follow_up_time


                Leads_history.objects.create(
                    leads=status_update_user,
                    lead_id=merchant_id,
                    status=new_status,
                    name=status_update_user.name,
                    message=remark,
                )

                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

                if request.user.is_staff_new:
                    admin_email = request.user.email
                    admin_instance = Staff.objects.filter(email=admin_email).last()
                    team_leader = admin_instance.team_leader

                    ActivityLog.objects.create(
                        team_leader=team_leader,
                        description=tagline,
                        ip_address=ip,
                        email=request.user.email,
                        user_type=user_type,
                        activity_type=f"Status changed to {new_status}",
                        name=request.user.name,
                    )
            except LeadUser.DoesNotExist:
                return Response({"error": "LeadUser does not exist."}, status=status.HTTP_404_NOT_FOUND)

            # Update Team_LeadData
            # try:
            #     status_update_team_lead = Team_LeadData.objects.get(id=merchant_id)
            #     status_update_team_lead.status = new_status
            #     status_update_team_lead.save()

            #     # Activity log for Team_LeadData
            #     ActivityLog.objects.create(
            #         team_leader=team_leader,
            #         description=f"Lead status changed for Team LeadData by {user_type}",
            #         ip_address=ip,
            #         email=request.user.email,
            #         user_type=user_type,
            #         activity_type=f"Status changed to {new_status}",
            #         name=request.user.name,
            #     )
            # except Team_LeadData.DoesNotExist:
            #     return Response({"error": "Team_LeadData does not exist."}, status=status.HTTP_404_NOT_FOUND)
            res['status'] = True
            res['message'] = "Status updated successfully."
            res['data'] = data
            return Response(res, status=status.HTTP_200_OK)

        return Response({"error": "Invalid data provided."}, status=status.HTTP_400_BAD_REQUEST)
    

    
class AutoAssignLeadsAPIView(APIView):
    """
    API to automatically assign a batch of leads to the staff member.
    """
    permission_classes = [IsAuthenticated ,  CustomIsSuperuser]

    def post(self, request):
        user_email = request.user.email
        request_user = get_object_or_404(Staff, email=user_email)
        team_leader = request_user.team_leader
        current_total_assign_leads = LeadUser.objects.filter(assigned_to=request_user, status='Leads').count()

        if current_total_assign_leads == 0:
            team_leader_total_leads = Team_LeadData.objects.filter(assigned_to=None, status='Leads')
            leads_count = 0
            leads_assigned = []

            for lead in team_leader_total_leads:
                if leads_count != 20:
                    lead_user = LeadUser.objects.create(
                        name=lead.name,
                        email=lead.email,
                        call=lead.call,
                        send=False,
                        status=lead.status,
                        assigned_to=request_user,
                        team_leader=team_leader,
                        user=lead.user,
                    )
                    lead.assigned_to = request_user
                    lead.save()
                    leads_assigned.append(LeadUserSerializer(lead_user).data)
                    leads_count += 1

            return Response({"message": "Leads assigned successfully.", "leads": leads_assigned}, status=status.HTTP_201_CREATED)

        return Response({"error": "You already have leads."}, status=status.HTTP_400_BAD_REQUEST)
    

    
class LeadsReportAPIView(APIView):
    """
    API to generate a report of leads filtered by their current status.
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser]

    def get(self, request):
        res = {}
        lead_status = request.data.get('status')

        if lead_status is None:
            res['status'] = True
            res['message'] = "lead status is required."
            res['data'] = []
            return Response(res, status=status.HTTP_200_OK)
        
        staff_instance = Staff.objects.filter(user__email=request.user.email).last()
        users_lead_lost = LeadUser.objects.filter(status=lead_status, assigned_to=staff_instance).order_by('-updated_date')
        serializer = LeadUserSerializer(users_lead_lost, many=True)

        res['status'] = True
        res['message'] = lead_status + " leads fetch successfully."
        res['data'] = serializer.data
        return Response(res, status=status.HTTP_200_OK)
    

    
class LeadHistoryAPIView(APIView):
    """
    API to retrieve the historical activity logs of a specific lead.
    """
    permission_classes = [IsAuthenticated, CustomIsSuperuser]

    def get(self, request):
        res = {}
        
        lead_id = request.query_params.get('lead_id')

        if lead_id is None:
            res['status'] = False
            res['message'] = "lead_id is required."
            res['data'] = []
            return Response(res, status=status.HTTP_400_BAD_REQUEST)

        users_lead_lost = Leads_history.objects.filter(lead_id=lead_id).order_by('-updated_date')
        serializer = LeadsHistorySerializer(users_lead_lost, many=True)

        res['status'] = True
        res['message'] = "Leads history fetched successfully."
        res['data'] = serializer.data
        return Response(res, status=status.HTTP_200_OK)



class AddLeadBySelfAPI(APIView):
    """
    API to manually add a new lead into the system.
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser]
    parser_classes = (MultiPartParser, FormParser) 

    def post(self, request):
        user = request.user
        data = request.data
        
        name = data.get('name')
        email = data.get('email')
        mobile = data.get('mobile')
        status_value = data.get('status')
        description = data.get('description')

        if not mobile:
            return Response({"message": "Mobile number is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        mobile_str = str(mobile)
        if LeadUser.objects.filter(call=mobile_str).exists():
            return Response({"message": "Mobile number already exists."}, status=status.HTTP_400_BAD_REQUEST)

        lead_data = {
            'user': user.id,
            'name': name,
            'email': email,
            'call': mobile_str,
            'message': description,
            'status': status_value
        }
        
        if user.is_team_leader:
            team_leader_instance = Team_Leader.objects.filter(email=user.email).last()
            if not team_leader_instance:
                return Response({"error": f"Team Leader profile not found for {user.email}."}, status=status.HTTP_404_NOT_FOUND)
            
            lead_data.update({'team_leader': team_leader_instance.id})
            serializer = LeadUserSerializer(data=lead_data)
        
        elif user.is_staff_new:
            staff_instance = Staff.objects.filter(email=user.email).last()
            if not staff_instance:
                return Response({"error": f"Staff profile not found for {user.email}."}, status=status.HTTP_404_NOT_FOUND)
            
            if not staff_instance.team_leader:
                 return Response({"error": f"Staff {user.email} is not assigned to any Team Leader."}, status=status.HTTP_400_BAD_REQUEST)

            lead_data.update({
                'team_leader': staff_instance.team_leader.id,
                'assigned_to': staff_instance.id
            })
            serializer = LeadUserSerializer(data=lead_data)
        
        elif user.is_admin:

            serializer = LeadUserSerializer(data=lead_data)
        
        else:
            return Response({"error": "Unauthorized role for this action"}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'lead add successfully', 'status': status.HTTP_201_CREATED, 'data': serializer.data})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
class StaffProfileAPIView(APIView):
    """
    API to manage the profile of the logged-in Staff member.
    """
    
    permission_classes = [IsAuthenticated , CustomIsSuperuser]

    def get(self, request):
        staff_instance = get_object_or_404(Staff, email=request.user.email)
        serializer = StaffProfileSerializer(staff_instance)
        data = serializer.data
        data['image'] = staff_instance.user.profile_image.url
        return Response({'mesage': 'Profile fetch successfully.', 'status': status.HTTP_200_OK, 'data': data,},)
    
    def post(self, request):
        admin = get_object_or_404(Staff, email=request.user.email)
        user_instance = User.objects.filter(email=admin.email).last()
        
        new_email = request.data.get('email')
        if new_email != admin.email and Staff.objects.filter(email=new_email).exclude(id=admin.id).exists():
            return Response({"error": "Email Already Exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        staff_serializer = StaffProfileSerializer(admin, data=request.data, partial=True)
        if staff_serializer.is_valid():
            staff_serializer.save()
        else:
            return Response(staff_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        image = request.FILES.get("profile_image")
        user_data = {
            # 'email': new_email,
            # 'username': new_email,
            'name': request.data.get('name'),
            'mobile': request.data.get('mobile'),
            'profile_image': request.FILES.get("profile_image")
        }
        user_serializer = UserSerializer(user_instance, data=user_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"success": "Your profile has been successfully updated."}, status=status.HTTP_200_OK)


    
class EditRecordAPIView(APIView):
    """
    API to fetch details of a specific Marketing record based on the source.
    """
    permission_classes = [IsAuthenticated, MarketingAccessPermission]

    def get(self, request, source):
        user = request.user
        record = Marketing.objects.filter(source=source, user=user).last()
        create_id = 2 if record is None else 1

        if record:
            data = {
                'm_id': record.id,
                'source': record.source,
                'url': record.url,
                'message': record.message,
                'media_file': record.media_file.url if record.media_file else '',
                'create_id': create_id,
            }
        else:
            data = {
                'source': source,
                'create_id': create_id,
            }
        
        return Response(data, status=status.HTTP_200_OK)
    


class UpdateRecordAPIView(APIView):
    """
    API to create or update a marketing record.
    """
    permission_classes = [IsAuthenticated, MarketingAccessPermission]

    def post(self, request):
        data = request.data
        source = data.get('source')
        message = data.get('message')
        url = data.get('url')
        media_file = data.get('media_file')
        create_id = data.get('create_id')
        user = request.user

        if create_id == "2":
            # Create a new marketing record
            marketing = Marketing.objects.create(
                user=user,
                source=source,
                message=message,
                url=url,
                media_file=media_file
            )
            serializer = MarketingSerializer(marketing)
            return Response({'message': 'Record created successfully', 'status': '200', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            # Update the last record for the user and source
            marketing_instance = Marketing.objects.filter(user=user, source=source).last()
            if not marketing_instance:
                return Response({'error': 'Record not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            marketing_instance.message = message
            marketing_instance.url = url
            marketing_instance.media_file = media_file
            marketing_instance.save()

            serializer = MarketingSerializer(marketing_instance)
            return Response({'message': 'Record updated successfully', 'status': '200', 'data': serializer.data}, status=status.HTTP_200_OK)
        


class CustomPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000



class ActivityLogsAPIView(APIView):
    """
    API to retrieve activity logs based on the logged-in user's role and hierarchy.
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser]

    def get(self, request):
        user = request.user
        logs = ActivityLog.objects.none()

        if user.is_superuser:
            logs = ActivityLog.objects.all().order_by('-created_date')
        elif user.is_admin:
            admin_user = Admin.objects.filter(email=user.email).last()
            logs = ActivityLog.objects.filter(admin=admin_user).order_by('-created_date')
        elif user.is_team_leader:
            team_leader_user = Team_Leader.objects.filter(email=user.email).last()
            logs = ActivityLog.objects.filter(team_leader=team_leader_user).order_by('-created_date')
        elif user.is_staff_new:
            staff_instance = Staff.objects.filter(email=user.email).last()
            logs = ActivityLog.objects.filter(Q(user=user) | Q(staff=staff_instance)).order_by('-created_date')

        serializer = ActivityLogSerializer(logs, many=True)

        return Response(serializer.data)
    


class IncentiveSlabStaffView(APIView):
    """
    API to retrieve incentive slabs and sales history for a staff member.
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser]

    def get(self, request, staff_id):

        months_list = [(i, month_name[i]) for i in range(1, 13)]

        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))

        if hasattr(request.user, 'is_staff_new') and request.user.is_staff_new:
            user_type = request.user.is_freelancer
        else:
            staff_instance = Staff.objects.filter(id=staff_id).last()
            user_type = User.objects.filter(email=staff_instance.email).last().is_freelancer if staff_instance else None

        slab = Slab.objects.all()

        if request.user.is_superuser or request.user.is_team_leader or request.user.is_admin:
            sell_property = Sell_plot.objects.filter(
                staff=staff_id,
                updated_date__year=year,
                updated_date__month=month
            ).order_by('-created_date')
            total_earn_amount = sell_property.aggregate(total_earn=Sum('earn_amount'))
        else:
            sell_property = Sell_plot.objects.filter(
                staff__email=request.user.email,
                updated_date__year=year,
                updated_date__month=month
            ).order_by('-created_date')
            total_earn_amount = sell_property.aggregate(total_earn=Sum('earn_amount'))

        total_earn = total_earn_amount['total_earn'] if total_earn_amount['total_earn'] else 0

        sell_property_data = SellPlotSerializer(sell_property, many=True).data

        response_data = {
            'slab': slab.values(),
            'sell_property': sell_property_data,
            'total_earn': total_earn,
            'year': year,
            'month': month,
            'months_list': months_list,
            'user_type': user_type,
        }
        return Response(response_data)



class StaffProductivityCalendarAPIView(APIView):
    """
    API to generate a productivity calendar and salary report for a staff member.
    """
    def get(self, request, staff_id, year=None, month=None):
        year = int(request.GET.get('year', datetime.now().year))
        month = int(request.GET.get('month', datetime.now().month))

        if request.user.is_superuser or request.user.is_team_leader or request.user.is_admin:
            staff = Staff.objects.get(id=staff_id)
        else:
            staff = Staff.objects.get(user__id=staff_id)

        days_in_month = monthrange(year, month)[1]
        salary_arg = staff.salary if staff.salary else 0
        daily_salary = round(float(salary_arg) / days_in_month)

        leads_data = LeadUser.objects.filter(
            assigned_to=staff,
            updated_date__year=year,
            updated_date__month=month,
            status='Intrested'
        ).values('updated_date__day').annotate(count=Count('id'))

        productivity_data = {}
        total_salary = 0

        for lead in leads_data:
            day = lead['updated_date__day']
            leads_count = lead['count']
            daily_earned_salary = daily_salary if leads_count >= 10 else round((daily_salary / 10) * leads_count, 2)
            productivity_data[day] = {'leads': leads_count, 'salary': daily_earned_salary}
            total_salary += daily_earned_salary

        calendar_data = monthcalendar(year, month)
        weekdays = list(day_name)
        structured_calendar_data = []

        for week in calendar_data:
            for i, day in enumerate(week):
                if day != 0:
                    structured_calendar_data.append({'day': day, 'day_name': weekdays[i]})

        months_list = [(i, calendar.month_name[i]) for i in range(1, 13)]

        response_data = {
            'staff': StaffProfileSerializer(staff).data,
            'year': year,
            'month': month,
            'productivity_data': [{'day': day, 'day_name': weekdays[(day - 1) % 7], 'leads': data['leads'], 'salary': data['salary']}
                                  for day, data in productivity_data.items()],
            'structured_calendar_data': structured_calendar_data,
            'days_in_month': days_in_month,
            'total_salary': round(total_salary, 2),
            'monthly_salary': salary_arg,
            'months_list': months_list,
        }

        return Response(response_data)
    


User = get_user_model()

# SUPER ADMIN DASHBOARD API

class SuperAdminDashboardAPIView(APIView):
    """
    API view for the Super Admin Dashboard (Admin Users page).
    Provides aggregated lead counts and stats about ALL ADMINS.
    Only accessible by superusers.
    """
    permission_classes = [IsAuthenticated, CustomIsSuperuser] # Sirf Superuser ke liye

    def get(self, request, *args, **kwargs):
        
        admin_users = User.objects.filter(is_admin=True)
        admin_profiles = Admin.objects.filter(self_user__in=admin_users)
        admin_serializer = DashboardAdminSerializer(admin_profiles, many=True) 
        
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        total_upload_leads = Team_LeadData.objects.filter().count()
        total_left_leads = Team_LeadData.objects.filter(status='Leads', assigned_to=None).count()
        total_assign_leads = LeadUser.objects.filter(status='Leads').count()
        interested_leads_staff = LeadUser.objects.filter(status='Intrested').count()
        not_interested_leads_staff = LeadUser.objects.filter(status='Not Interested').count()
        other_location_leads_staff = LeadUser.objects.filter(status='Other Location').count()
        not_picked_leads_staff = LeadUser.objects.filter(status='Not Picked').count()
        lost_leads_staff = LeadUser.objects.filter(status='Lost').count()
        lost_visit_staff = LeadUser.objects.filter(status='Visit').count()

        pending_followup_staff = LeadUser.objects.filter(
                Q(status='Intrested') & Q(follow_up_date__isnull=False)
            ).count()
        today_followup_staff = LeadUser.objects.filter(
                Q(status='Intrested') & Q(follow_up_date=today)
            ).count()
        tomorrow_followup_staff = LeadUser.objects.filter(
                Q(status='Intrested') & Q(follow_up_date=tomorrow)
            ).count()

        interested_leads_team_leader = Team_LeadData.objects.filter(status='Intrested').count()
        not_interested_leads_team_leader  = Team_LeadData.objects.filter(status='Not Interested').count()
        other_location_leads_team_leader  = Team_LeadData.objects.filter(status='Other Location').count()
        not_picked_leads_team_leader = Team_LeadData.objects.filter(status='Not Picked').count()
        lost_leads_team_leader  = Team_LeadData.objects.filter(status='Lost').count()
        lost_visit_team_leader  = Team_LeadData.objects.filter(status='Visit').count()

        total_interested = interested_leads_staff + interested_leads_team_leader
        total_not_interested = not_interested_leads_staff + not_interested_leads_team_leader
        total_other_location = other_location_leads_staff + other_location_leads_team_leader
        total_not_picked = not_picked_leads_staff + not_picked_leads_team_leader
        total_lost = lost_leads_staff + lost_leads_team_leader
        total_visits = lost_visit_staff + lost_visit_team_leader

        total_pending_followup = pending_followup_staff
        total_today_followup = today_followup_staff
        total_tomorrow_followup = tomorrow_followup_staff

        data = {
            'users': admin_serializer.data,
            'total_upload_leads': total_upload_leads,
            'total_assign_leads': total_assign_leads,
            'total_interested': total_interested,
            'total_not_interested': total_not_interested,
            'total_other_location': total_other_location,
            'total_not_picked': total_not_picked,
            'total_lost': total_lost,
            'total_visits': total_visits,
            'total_left_leads': total_left_leads,
            'total_pending_followup': total_pending_followup,
            'total_today_followup': total_today_followup,
            'total_tomorrow_followup': total_tomorrow_followup,
          
        }
        
        return Response(data, status=status.HTTP_200_OK)
    


# NEW DASHBOARD API (Date Filter )

class SuperUserDashboardAPIView(APIView):
    """
    Super User Dashboard API, with date filtering .
    
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser]

    def get(self, request, *args, **kwargs):
        
        us = request.user
        admin_profiles = Admin.objects.filter(user=us)
        
        admin_serializer = DashboardAdminSerializer(admin_profiles, many=True)

        # Date filtering logic
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        lead_filter = {}
        start_date_for_context = None
        end_date_for_context = None

        if start_date_str and end_date_str:
            try:
                start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
                end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)) - timedelta(seconds=1)
                
                lead_filter = {'updated_date__range': [start_date, end_date]}
                start_date_for_context = start_date_str
                end_date_for_context = end_date_str
            except ValueError:
                pass 

        total_upload_leads = Team_LeadData.objects.filter(status='Leads').count()
        total_assign_leads = LeadUser.objects.filter(status='Leads').count()
        interested_leads_staff = LeadUser.objects.filter(status='Intrested', **lead_filter).count()
        not_interested_leads_staff = LeadUser.objects.filter(status='Not Interested', **lead_filter).count()
        other_location_leads_staff = LeadUser.objects.filter(status='Other Location', **lead_filter).count()
        not_picked_leads_staff = LeadUser.objects.filter(status='Not Picked', **lead_filter).count()
        lost_leads_staff = LeadUser.objects.filter(status='Lost', **lead_filter).count()
        lost_visit_staff = LeadUser.objects.filter(status='Visit', **lead_filter).count()
        
        interested_leads_team_leader = Team_LeadData.objects.filter(status='Intrested', **lead_filter).count()
        not_interested_leads_team_leader  = Team_LeadData.objects.filter(status='Not Interested', **lead_filter).count()
        other_location_leads_team_leader  = Team_LeadData.objects.filter(status='Other Location', **lead_filter).count()
        not_picked_leads_team_leader = Team_LeadData.objects.filter(status='Not Picked', **lead_filter).count()
        lost_leads_team_leader  = Team_LeadData.objects.filter(status='Lost', **lead_filter).count()
        lost_visit_team_leader  = Team_LeadData.objects.filter(status='Visit', **lead_filter).count()

        total_interested = interested_leads_staff + interested_leads_team_leader
        total_not_interested = not_interested_leads_staff + not_interested_leads_team_leader
        total_other_location = other_location_leads_staff + other_location_leads_team_leader
        total_not_picked = not_picked_leads_staff + not_picked_leads_team_leader
        total_lost = lost_leads_staff + lost_leads_team_leader
        total_visits = lost_visit_staff + lost_visit_team_leader

        total_calls = total_interested + total_not_interested + total_other_location + total_not_picked + total_lost + total_visits

        total_users = User.objects.count()
        logged_in_users = User.objects.filter(is_user_login=True).count()
        logged_out_users = User.objects.filter(is_user_login=False).count()

        data_points = [
            { "label": "Interested", "y": total_interested  },
            { "label": "Lost",  "y": total_lost  },
            { "label": "Visits",  "y": total_visits  },
            { "label": "Not Interested", "y": total_not_interested  },
            { "label": "Other Location",  "y": total_other_location  },
            { "label": "Not Picked",  "y": total_not_picked  },
            { "label": "Total Calls",  "y": total_calls  },
        ]

        setting_obj = Settings.objects.filter().last()
        
        setting_serializer = DashboardSettingsSerializer(setting_obj)

        # Final JSON response
        data = {
            'users': admin_serializer.data,
            'data_points': data_points,
            'total_upload_leads': total_upload_leads,
            'total_assign_leads': total_assign_leads,
            'total_interested': total_interested,
            'total_not_interested': total_not_interested,
            'total_other_location': total_other_location,
            'total_not_picked': total_not_picked,
            'total_lost': total_lost,
            'total_visits': total_visits,
            'start_date': start_date_for_context,
            'end_date': end_date_for_context,
            'total_users': total_users,
            'logged_in_users': logged_in_users,
            'logged_out_users': logged_out_users,
            'setting': setting_serializer.data if setting_obj else None,
        }
        
        return Response(data, status=status.HTTP_200_OK)



# ADMIN SIDE LEADS RECORD API 

class AdminSideLeadsRecordAPIView(APIView):
    """
    API to retrieve and filter lead records for the administrative dashboard based on status tags.
    [FIX]: Follow-up tags are now only queried from the LeadUser model.
    """
    
    permission_classes = [IsAuthenticated, CustomIsSuperuser] # Sirf Superuser chala sakta hai
    pagination_class = StandardResultsSetPagination 

    def get(self, request, tag, *args, **kwargs):
        paginator = self.pagination_class()
        
        staff_leads_qs = LeadUser.objects.none()
        team_leads_qs = Team_LeadData.objects.none()

        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        if tag == "total_visit":
            staff_leads_qs = LeadUser.objects.filter(status='Visit')
            team_leads_qs = Team_LeadData.objects.filter(status='Visit')
            
        elif tag == "lost":
            staff_leads_qs = LeadUser.objects.filter(status='Lost')
            team_leads_qs = Team_LeadData.objects.filter(status='Lost')
            
        elif tag == "not_picked":
            staff_leads_qs = LeadUser.objects.filter(status='Not Picked')
            team_leads_qs = Team_LeadData.objects.filter(status='Not Picked')
            
        elif tag == "other_location":
            staff_leads_qs = LeadUser.objects.filter(status='Other Location')
            team_leads_qs = Team_LeadData.objects.filter(status='Other Location')
            
        elif tag == "not_interested":
            staff_leads_qs = LeadUser.objects.filter(status='Not Interested')
            team_leads_qs = Team_LeadData.objects.filter(status='Not Interested')
            
        elif tag == "total_leads":
            team_leads_qs = Team_LeadData.objects.filter(status='Leads')
            
        elif tag == "total_assigned_lead_tag":
            staff_leads_qs = LeadUser.objects.filter(status='Leads')
            
        elif tag == "interested":
            staff_leads_qs = LeadUser.objects.filter(status='Intrested')
            team_leads_qs = Team_LeadData.objects.filter(status='Intrested')
        
        
        elif tag == "pending_followups":
            staff_leads_qs = LeadUser.objects.filter(Q(status='Intrested') & Q(follow_up_date__isnull=False))
           

        elif tag == "today_followups":
            staff_leads_qs = LeadUser.objects.filter(Q(status='Intrested') & Q(follow_up_date=today))
       

        elif tag == "tomorrow_followups":
            staff_leads_qs = LeadUser.objects.filter(Q(status='Intrested') & Q(follow_up_date=tomorrow))
            
        

        else:
            return Response({"error": "Invalid tag provided"}, status=status.HTTP_400_BAD_REQUEST)

        staff_serializer = ApiLeadUserSerializer(staff_leads_qs.order_by('-updated_date'), many=True)
        team_serializer = ApiTeamLeadDataSerializer(team_leads_qs.order_by('-updated_date'), many=True)

        combined_data = staff_serializer.data + team_serializer.data
        
        page = paginator.paginate_queryset(combined_data, request, view=self)
        
        if page is not None:
            return paginator.get_paginated_response(page)

        return Response(combined_data, status=status.HTTP_200_OK)    
    


# FILE UPLOAD API (Excel/CSV)

class ExcelUploadAPIView(APIView):
    """
    Excel (.xlsx) ya CSV (.csv) file se leads upload karne ke liye API.
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser] 
    parser_classes = (MultiPartParser, FormParser)


    def post(self, request, *args, **kwargs):
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            return Response(
                {"error": "File not provided. Please upload a file with the key 'excel_file'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if excel_file.name.endswith('.csv'):
               
                df = pd.read_csv(excel_file, encoding='utf-8-sig') 
            elif excel_file.name.endswith('.xlsx'):
                df = pd.read_excel(excel_file, engine='openpyxl')
            else:
                return Response(
                    {"error": "Unsupported file format. Please upload a .csv or .xlsx file."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {"error": f"Error reading file: {e}. Make sure the file is not corrupt."},
                status=status.HTTP_400_BAD_REQUEST
            )

        df.columns = df.columns.str.lower().str.strip()
       
        required_columns = ['name', 'call', 'send', 'status']
        if not all(col in df.columns for col in required_columns):
            return Response(
                {"error": f"File is missing required columns. Make sure these columns exist (all lowercase): {required_columns}. Found columns: {list(df.columns)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_count = df.shape[0]
        duplicates = []
        created_count = 0
        
        team_leader = None
        if request.user.is_team_leader:
            try:
                team_leader = Team_Leader.objects.get(user=request.user)
            except Team_Leader.DoesNotExist:
                return Response(
                    {"error": "Team Leader profile not found for this user."},
                    status=status.HTTP_404_NOT_FOUND
                )

        for i, row in df.iterrows():
           
            name = row['name']
            call = row['call']
            status_val = row['status']
            send_val = row['send']

            if not name or pd.isna(name):
                continue
            if not status_val.lower() not in ["lead", "leads"]:
                continue
            try:
                if Team_LeadData.objects.filter(call=call).exists():
                    duplicates.append(call)
                    continue

                if request.user.is_team_leader:
                    Team_LeadData.objects.create(
                        call=call,
                        name=name,
                        send=send_val,
                        status=status_val,
                        team_leader=team_leader,
                        user=request.user
                    )
                    created_count += 1
                
                elif request.user.is_superuser:
                    Team_LeadData.objects.create(
                        call=call,
                        name=name,
                        send=send_val,
                        status=status_val,
                        user=request.user
                    )
                    created_count += 1

            except IntegrityError:
                duplicates.append(call)
                continue
            except Exception as e:
                return Response(
                    {"error": f"An error occurred at row {i}: {e}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        message = f"Excel file uploaded successfully! Total Rows: {user_count}, Created: {created_count}, Duplicates Found: {len(duplicates)}"
        
        return Response(
            {
                "message": message,
                "total_rows": user_count,
                "new_leads_created": created_count,
                "duplicates_found": len(duplicates),
                "duplicate_calls_list": duplicates
            },
            status=status.HTTP_201_CREATED
        )



# FREELANCER (ASSOCIATES) DASHBOARD API 

class FreelancerDashboardAPIView(APIView):
    """
    API for the Super Admin's Freelancer (Associates) Dashboard.
    
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser]

    def get(self, request, *args, **kwargs):
        
        # ---  Freelancer List ---
        my_staff = Staff.objects.filter(user__is_freelancer=True)
        staff_serializer = ApiStaffSerializer(my_staff, many=True)

        # ---  Lead Counts] ---
        total_interested_leads = LeadUser.objects.filter(status="Intrested", assigned_to__user__is_freelancer=True).count()
        total_not_interested_leads = LeadUser.objects.filter(status="Not Interested", assigned_to__user__is_freelancer=True).count()
        total_other_location_leads = LeadUser.objects.filter(status="Other Location", assigned_to__user__is_freelancer=True).count()
        total_not_picked_leads = LeadUser.objects.filter(status="Not Picked", assigned_to__user__is_freelancer=True).count()
        total_visits_leads = LeadUser.objects.filter(status="Visit", assigned_to__user__is_freelancer=True).count()
       

        # ---  Total Earning Calculation  ---
        
        total_earn_aggregation = Sell_plot.objects.filter(staff__user__is_freelancer=True).aggregate(total_earn=Sum('earn_amount'))
        
        total_earning = total_earn_aggregation.get('total_earn')
        if total_earning is None: 
            total_earning = 0

        data = {
            'total_interested_leads': total_interested_leads,
            'total_not_interested_leads': total_not_interested_leads,
            'total_other_location_leads': total_other_location_leads,
            'total_not_picked_leads': total_not_picked_leads,
            'total_visits_leads': total_visits_leads,
            'total_earning': total_earning,
            'my_staff': staff_serializer.data, 
        }
        
        return Response(data, status=status.HTTP_200_OK)



# IT STAFF LIST API

class ITStaffListAPIView(APIView):
    """
    API for the Super Admin's IT Staff list page.
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser]

    def get(self, request, *args, **kwargs):
        
        # --- 1. IT Staff List ---
        it_staff_list = Staff.objects.filter(user__is_it_staff=True)
        
        # --- 2. Serialize Data ---
        serializer = ApiStaffSerializer(it_staff_list, many=True)

        # --- 3. Final Response ---
        return Response(serializer.data, status=status.HTTP_200_OK)
    


# ATTENDANCE CALENDAR API 

class AttendanceCalendarAPIView(APIView):
    """
    API provides calendar data, present/absent counts, and color status for each day.
    """
    permission_classes = [IsAuthenticated] 
    
    def get(self, request, id, *args, **kwargs):
        
        # Get year and month from query parameters
        try:
            year = int(request.query_params.get('year', datetime.today().year))
            month = int(request.query_params.get('month', datetime.today().month))
        except ValueError:
            return Response({"error": "Invalid year or month format."}, status=status.HTTP_400_BAD_REQUEST)

        # Get User and Staff Instance
        try:
            if id == 0:
                user_to_check = request.user
            elif id > 0:
                staff_instance = Staff.objects.filter(id=id).last()
                if not staff_instance:
                    return Response({"error": "Staff member not found."}, status=status.HTTP_404_NOT_FOUND)
                user_to_check = staff_instance.user
            else:
                return Response({"error": "Invalid ID."}, status=status.HTTP_400_BAD_REQUEST)
        except Staff.DoesNotExist:
             return Response({"error": "Staff member not found."}, status=status.HTTP_404_NOT_FOUND)

        # Calendar Data Initialization
        days_in_month = monthrange(year, month)[1]
        
        tasks_for_month = Task.objects.filter(
            user=user_to_check, 
            task_date__month=month, 
            task_date__year=year
        )
        task_dates = {task.task_date for task in tasks_for_month}
        
        present_count = 0
        absent_count = 0
        
        # Structure Data for Calendar (Red/Green Logic)
        weekdays = list(calendar.day_name)
        today = timezone.now().date()
        daily_attendance_list = []
        
        for day in range(1, days_in_month + 1):
            date_obj = datetime(year, month, day).date()
            is_present = date_obj in task_dates
            
            if date_obj > today:
                status_text = "Future"
                color = "white"
            elif is_present:
                status_text = "Present"
                color = "green"
                present_count += 1
            else:
                status_text = "Absent"
                color = "red"
                absent_count += 1 

            daily_attendance_list.append({
                "date": date_obj, 
                "has_task": is_present,
                "day_name": weekdays[date_obj.weekday()],
                "status": status_text,
                "status_color": color, 
            })

        # Final Response
        months_list = [(i, calendar.month_name[i]) for i in range(1, 13)]
        
        days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
       
        
        calendar_serializer = AttendanceCalendarDaySerializer(daily_attendance_list, many=True)
        
        data = {
            "id": id,
            "user_email": user_to_check.email,
            "month": month,
            "year": year,
            "present_count": present_count,
            "absent_count": absent_count,
            "total_days_checked": days_in_month,
            "days_of_week": days_of_week, 
            "calendar_data": calendar_serializer.data,
        }
        
        return Response(data, status=status.HTTP_200_OK)



# STAFF PRODUCTIVITY API

class StaffProductivityAPIView(APIView):
    """
    API for the Staff Productivity page.
    Calculates leads, calls, and percentages for staff based on user role and filters.
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser] # Use the custom permission

    def get(self, request, *args, **kwargs):
        # Get Filters from query params
        date_filter = request.query_params.get('date', None)
        end_date_str = request.query_params.get('endDate', None)
        teamleader_id = request.query_params.get('teamleader_id', None)
        admin_id = request.query_params.get('admin_id', None)

        # Staff Queryset based on User Role
        staffs = Staff.objects.none() 
        fiter_value = 0 # Corresponds to 'fiter' in original view

        if request.user.is_superuser:
            fiter_value = 1
            staffs = Staff.objects.filter(user__user_active=True, user__is_freelancer=False)
            if admin_id:
                staffs = staffs.filter(team_leader__admin=admin_id)
            if teamleader_id:
                staffs = staffs.filter(team_leader=teamleader_id)
        
        elif request.user.is_admin:
            fiter_value = 4
            staffs = Staff.objects.filter(team_leader__admin__self_user=request.user, user__user_active=True, user__is_freelancer=False)
            if teamleader_id:
                staffs = staffs.filter(team_leader=teamleader_id)

        elif request.user.is_team_leader:
            fiter_value = 2
            user_instance = request.user.username
            team_leader_instance = Team_Leader.objects.filter(email=user_instance).last()
            staffs = Staff.objects.filter(team_leader=team_leader_instance, user__user_active=True, user__is_freelancer=False)
        
        total_staff_count = staffs.count()

        # Initialize totals and staff data list
        staff_data_list = []
        total_all_leads = 0
        total_all_interested = 0
        total_all_not_interested = 0
        total_all_other_location = 0
        total_all_not_picked = 0
        total_all_lost = 0
        total_all_visit = 0
        total_all_calls = 0

        # Date Filter Logic
        lead_filter = {}
        lead_filter1 = {}
        date_filter_applied = False
        
        if date_filter and end_date_str:
            try:
                start_date = timezone.make_aware(datetime.strptime(date_filter, '%Y-%m-%d'))
                end_date_dt = datetime.strptime(end_date_str, '%Y-%m-%d')
                end_date = timezone.make_aware(end_date_dt + timedelta(days=1)) - timedelta(seconds=1)
                lead_filter = {'updated_date__range': [start_date, end_date]}
                lead_filter1 = {'created_date__range': [start_date, end_date]}
                date_filter_applied = True
            except ValueError:
                pass # Invalid date format, filters will be empty
        
        elif date_filter:
            try:
                date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
                lead_filter = {'updated_date__date': date_obj}
                lead_filter1 = {'created_date__date': date_obj}
                date_filter_applied = True
            except ValueError:
                pass # Invalid date format

        # Loop and Aggregate Data
        for staff in staffs:
            
            # Date filter logic from original view
            if date_filter_applied:
                leads_by_date = LeadUser.objects.filter(
                    assigned_to=staff, **lead_filter
                ).aggregate(
                    interested=Count('id', filter=Q(status='Intrested')),
                    not_interested=Count('id', filter=Q(status='Not Interested')),
                    other_location=Count('id', filter=Q(status='Other Location')),
                    not_picked=Count('id', filter=Q(status='Not Picked')),
                    lost=Count('id', filter=Q(status='Lost')),
                    visit=Count('id', filter=Q(status='Visit'))
                )
                
                leads_by_date1 = LeadUser.objects.filter(
                    assigned_to=staff, **lead_filter1
                ).aggregate(
                    total_leads=Count('id'),
                )
            
            else: # No date filter applied (original 'else' block)
                leads_by_date_all = LeadUser.objects.filter(assigned_to=staff).aggregate(
                    total_leads=Count('id'),
                    interested=Count('id', filter=Q(status='Intrested')),
                    not_interested=Count('id', filter=Q(status='Not Interested')),
                    other_location=Count('id', filter=Q(status='Other Location')),
                    not_picked=Count('id', filter=Q(status='Not Picked')),
                    lost=Count('id', filter=Q(status='Lost')),
                    visit=Count('id', filter=Q(status='Visit'))
                )
                leads_by_date = leads_by_date_all
                leads_by_date1 = {'total_leads': leads_by_date_all['total_leads']}

            
            # Calculations
            total_calls = (
                leads_by_date.get('interested', 0) + 
                leads_by_date.get('not_interested', 0) + 
                leads_by_date.get('other_location', 0) + 
                leads_by_date.get('not_picked', 0) + 
                leads_by_date.get('lost', 0) + 
                leads_by_date.get('visit', 0)
            )
            total_leads_for_staff = leads_by_date1.get('total_leads', 0)
            visit_percentage = (leads_by_date.get('visit', 0) / total_leads_for_staff * 100) if total_leads_for_staff > 0 else 0
            interested_percentage = (leads_by_date.get('interested', 0) / total_leads_for_staff * 100) if total_leads_for_staff > 0 else 0

            staff_data_list.append({
                'id': staff.id,
                'name': staff.name,
                'total_leads': total_leads_for_staff,
                'interested': leads_by_date.get('interested', 0),
                'not_interested': leads_by_date.get('not_interested', 0),
                'other_location': leads_by_date.get('other_location', 0),
                'not_picked': leads_by_date.get('not_picked', 0),
                'lost': leads_by_date.get('lost', 0),
                'visit': leads_by_date.get('visit', 0),
                'visit_percentage': round(visit_percentage, 2),
                'interested_percentage': round(interested_percentage, 2),
                'total_calls': total_calls,
            })

            # Add to grand totals
            total_all_leads += total_leads_for_staff
            total_all_interested += leads_by_date.get('interested', 0)
            total_all_not_interested += leads_by_date.get('not_interested', 0)
            total_all_other_location += leads_by_date.get('other_location', 0)
            total_all_not_picked += leads_by_date.get('not_picked', 0)
            total_all_lost += leads_by_date.get('lost', 0)
            total_all_visit += leads_by_date.get('visit', 0)
            total_all_calls += total_calls
        
        # Calculate Grand Totals
        total_visit_percentage = (total_all_visit / total_all_leads * 100) if total_all_leads > 0 else 0
        total_interested_percentage = (total_all_interested / total_all_leads * 100) if total_all_leads > 0 else 0

        # Get data for filters (Admins and Team Leaders)
        admins_qs = Admin.objects.all()
        teamleader_qs = Team_Leader.objects.filter(admin__self_user=request.user)
        
        admins_data = DashboardAdminSerializer(admins_qs, many=True).data
        teamleader_data = ProductivityTeamLeaderSerializer(teamleader_qs, many=True).data
        staff_data_serialized = StaffProductivityDataSerializer(staff_data_list, many=True).data

        # Build Final Response
        data = {
            'staff_data': staff_data_serialized,
            'selected_date': date_filter,
            'total_all_leads': total_all_leads,
            'total_all_interested': total_all_interested,
            'total_all_not_interested': total_all_not_interested,
            'total_all_other_location': total_all_other_location,
            'total_all_not_picked': total_all_not_picked,
            'total_all_lost': total_all_lost,
            'total_all_visit': total_all_visit,
            'total_all_calls': total_all_calls,
            'total_visit_percentage': round(total_visit_percentage, 2),
            'total_interested_percentage': round(total_interested_percentage, 2),
            'total_staff_count': total_staff_count,
            'admins_filter_list': admins_data,
            'teamleader_filter_list': teamleader_data,
            'fiter': fiter_value,
        }
        
        return Response(data, status=status.HTTP_200_OK)
    


# TEAM LEADER PRODUCTIVITY API 

class TeamLeaderProductivityAPIView(APIView):
    """
    API for the Team Leader Productivity page.
    """
    permission_classes = [IsAuthenticated, CustomIsSuperuser]

    def get(self, request, *args, **kwargs):
        # Get Filters from query params
        date_filter = request.query_params.get('date', None)
        end_date_str = request.query_params.get('endDate', None)
        admin_id = request.query_params.get('admin_id', None)
        
        # Team Leader Queryset based on User Role
        team_leaders = Team_Leader.objects.none()
        fiter_value = 0

        if request.user.is_superuser:
            fiter_value = 3
            team_leaders = Team_Leader.objects.filter(user__user_active=True)
            if admin_id:
                team_leaders = team_leaders.filter(admin=admin_id)
        
        elif request.user.is_admin:
            fiter_value = 5
            team_leaders = Team_Leader.objects.filter(admin__self_user=request.user, user__user_active=True)
            if admin_id: 
                team_leaders = team_leaders.filter(admin=admin_id)
        
        elif request.user.is_team_leader:
             return Response({"error": "Team Leaders cannot view this page."}, status=status.HTTP_403_FORBIDDEN)

        total_team_leaders_count = team_leaders.count()

        # Initialize totals and data list
        team_leader_data_list = []
        total_all_leads = 0
        total_all_interested = 0
        total_all_not_interested = 0
        total_all_other_location = 0
        total_all_not_picked = 0
        total_all_lost = 0
        total_all_visit = 0
        total_all_calls = 0

        # Loop over each Team Leader and Aggregate Data
        for team_leader in team_leaders:
            leads_data_agg = {
                'total_leads': 0, 'interested': 0, 'not_interested': 0,
                'other_location': 0, 'not_picked': 0, 'lost': 0, 'visit': 0
            }
            
            staff_members = Staff.objects.filter(team_leader=team_leader)

            for staff in staff_members:
                
                lead_filter = {}
                lead_filter1 = {}
                
                if date_filter and end_date_str:
                    try:
                        start_date = timezone.make_aware(datetime.strptime(date_filter, '%Y-%m-%d'))
                        end_date_dt = datetime.strptime(end_date_str, '%Y-%m-%d')
                        end_date = timezone.make_aware(end_date_dt + timedelta(days=1)) - timedelta(seconds=1)
                        lead_filter = {'updated_date__range': [start_date, end_date]}
                        lead_filter1 = {'created_date__range': [start_date, end_date]}
                    except ValueError:
                        pass 
                elif date_filter:
                    try:
                        date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
                        lead_filter = {'updated_date__date': date_obj}
                        lead_filter1 = {'created_date__date': date_obj}
                    except ValueError:
                        pass 
                if lead_filter or lead_filter1:
                     leads_by_date = LeadUser.objects.filter(
                        assigned_to=staff, **lead_filter
                    ).aggregate(
                        interested=Count('id', filter=Q(status='Intrested')),
                        not_interested=Count('id', filter=Q(status='Not Interested')),
                        other_location=Count('id', filter=Q(status='Other Location')),
                        not_picked=Count('id', filter=Q(status='Not Picked')),
                        lost=Count('id', filter=Q(status='Lost')),
                        visit=Count('id', filter=Q(status='Visit'))
                    )
                     leads_by_date1 = LeadUser.objects.filter(
                        assigned_to=staff, **lead_filter1
                    ).aggregate(total_leads=Count('id'))
                else:
                   
                    leads_by_date_all = LeadUser.objects.filter(assigned_to=staff).aggregate(
                        total_leads=Count('id'),
                        interested=Count('id', filter=Q(status='Intrested')),
                        not_interested=Count('id', filter=Q(status='Not Interested')),
                        other_location=Count('id', filter=Q(status='Other Location')),
                        not_picked=Count('id', filter=Q(status='Not Picked')),
                        lost=Count('id', filter=Q(status='Lost')),
                        visit=Count('id', filter=Q(status='Visit'))
                    )
                    leads_by_date = leads_by_date_all
                    leads_by_date1 = {'total_leads': leads_by_date_all['total_leads']}

                leads_data_agg['total_leads'] += leads_by_date1.get('total_leads', 0)
                leads_data_agg['interested'] += leads_by_date.get('interested', 0)
                leads_data_agg['not_interested'] += leads_by_date.get('not_interested', 0)
                leads_data_agg['other_location'] += leads_by_date.get('other_location', 0)
                leads_data_agg['not_picked'] += leads_by_date.get('not_picked', 0)
                leads_data_agg['lost'] += leads_by_date.get('lost', 0)
                leads_data_agg['visit'] += leads_by_date.get('visit', 0)

            total_calls_tl = (
                leads_data_agg['interested'] + leads_data_agg['not_interested'] + 
                leads_data_agg['other_location'] + leads_data_agg['not_picked'] + 
                leads_data_agg['lost'] + leads_data_agg['visit']
            )
            visit_percentage = (leads_data_agg['visit'] / leads_data_agg['total_leads'] * 100) if leads_data_agg['total_leads'] > 0 else 0
            interested_percentage = (leads_data_agg['interested'] / leads_data_agg['total_leads'] * 100) if leads_data_agg['total_leads'] > 0 else 0

            team_leader_data_list.append({
                'id': team_leader.id,
                'name': team_leader.name,
                'total_leads': leads_data_agg['total_leads'],
                'interested': leads_data_agg['interested'],
                'not_interested': leads_data_agg['not_interested'],
                'other_location': leads_data_agg['other_location'],
                'not_picked': leads_data_agg['not_picked'],
                'lost': leads_data_agg['lost'],
                'visit': leads_data_agg['visit'],
                'visit_percentage': round(visit_percentage, 2),
                'interested_percentage': round(interested_percentage, 2),
                'total_calls': total_calls_tl,
            })

            total_all_leads += leads_data_agg['total_leads']
            total_all_interested += leads_data_agg['interested']
            total_all_not_interested += leads_data_agg['not_interested']
            total_all_other_location += leads_data_agg['other_location']
            total_all_not_picked += leads_data_agg['not_picked']
            total_all_lost += leads_data_agg['lost']
            total_all_visit += leads_data_agg['visit']
            total_all_calls += total_calls_tl
        
        # Calculate Grand Totals
        total_visit_percentage = (total_all_visit / total_all_leads * 100) if total_all_leads > 0 else 0
        total_interested_percentage = (total_all_interested / total_all_leads * 100) if total_all_leads > 0 else 0

        # Get data for filters (Admins)
        admins_qs = Admin.objects.all()
        admins_data = DashboardAdminSerializer(admins_qs, many=True).data
        team_leader_data_serialized = StaffProductivityDataSerializer(team_leader_data_list, many=True).data

        # Build Final Response
        data = {
            'staff_data': team_leader_data_serialized,
            'selected_date': date_filter,
            'task_type': 'teamleader',
            'total_all_leads': total_all_leads,
            'total_all_interested': total_all_interested,
            'total_all_not_interested': total_all_not_interested,
            'total_all_other_location': total_all_other_location,
            'total_all_not_picked': total_all_not_picked,
            'total_all_lost': total_all_lost,
            'total_all_visit': total_all_visit,
            'total_all_calls': total_all_calls,
            'total_visit_percentage': round(total_visit_percentage, 2),
            'total_interested_percentage': round(total_interested_percentage, 2),
            'total_staff_count': total_team_leaders_count,
            'admins_filter_list': admins_data,
            'fiter': fiter_value,
        }
        
        return Response(data, status=status.HTTP_200_OK)
    


# ADMIN ADD API

class AdminAddAPIView(APIView):
    """
    API for make new admin for superuser.
    """
    permission_classes = [IsAuthenticated, CustomIsSuperuser] 
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        serializer = AdminCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            admin_instance = serializer.save()
            
            read_serializer = DashboardAdminSerializer(admin_instance)
            
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



# ADMIN EDIT API (SMART AUTO-FIX VERSION)

class AdminEditAPIView(APIView):
    """
    API to Get and Update an Admin profile.
    Special Feature: It auto-fixes incorrectly linked profiles via Email.
    """
    permission_classes = [IsAuthenticated, CustomIsSuperuser] 
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self, id):
        """
        This method performs an AUTOMATIC FIX:
        1. Searches for Admin by User ID (from URL).
        2. If not found, checks by Email.
        3. If Email matches, it corrects the Admin's User link.
        """
        try:
            target_user = User.objects.get(id=id)

            try:
                return Admin.objects.get(user=target_user)
            
            except Admin.DoesNotExist:
                
                try:
                    # Find the Admin with the same email
                    broken_admin = Admin.objects.get(email=target_user.email)

                    # If found, fix the connection
                    # (It was previously wrongly linked to Superuser, now it will link to the correct ID)
                    broken_admin.user = target_user
                    broken_admin.save()

                    print(f" AUTO-FIXED: Admin '{broken_admin.name}' link is now corrected to User ID {target_user.id}!")
                    return broken_admin

                except Admin.DoesNotExist:
                    # If not found by Email either, then the profile truly doesn't exist
                    raise Http404("Admin profile does not exist for this User.")
                

        except User.DoesNotExist:
            raise Http404("Invalid User ID (User does not exist).")

    def get(self, request, id, *args, **kwargs):
        """
        Fetch full details of an Admin.
        """
        admin = self.get_object(id)
        
        serializer = DashboardAdminSerializer(admin)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id, *args, **kwargs):
        """
        Update an Admin profile.
        """
        admin = self.get_object(id)
        
        serializer = AdminUpdateSerializer(admin, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_admin = serializer.save()
            
            read_serializer = DashboardAdminSerializer(updated_admin)
            return Response(read_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




#  Pagination Class (so that data will come in page with  10-10 leads ) 

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100



# TEAM CUSTOMER (INTERESTED) LEADS API

class TeamCustomerLeadsAPIView(APIView):
    """
    API to retrieve leads with 'Intrested' status, filtered by follow-up status and user role (Superuser or Team Leader).
    """

    permission_classes = [IsAuthenticated , CustomIsSuperuser]
    pagination_class = StandardResultsSetPagination # Reuse pagination

    @property
    def paginator(self):
        """Paginator instance for the view."""
        if not hasattr(self, '_paginator'):
            self._paginator = self.pagination_class()
        return self._paginator

    def get(self, request, tag, *args, **kwargs):
        
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        user = request.user
        
        search_query = request.query_params.get('search', None)
        
        # Default empty queryset and serializer
        interested_leads_qs = LeadUser.objects.none()
        serializer_class = ApiLeadUserSerializer # Default serializer

        if search_query:
            interested_leads_qs = LeadUser.objects.filter(
                Q(name__icontains=search_query) | 
                Q(call__icontains=search_query) | 
                Q(team_leader__name__icontains=search_query),
                status='Intrested'
            )
            serializer_class = ApiLeadUserSerializer
        
        elif user.is_superuser:
            if tag == 'pending_follow':
                interested_leads_qs = LeadUser.objects.filter(
                    Q(status='Intrested') & Q(follow_up_date__isnull=False)
                ).order_by('-updated_date').select_related('team_leader')
            elif tag == 'today_follow':
                interested_leads_qs = LeadUser.objects.filter(
                    Q(status='Intrested') & Q(follow_up_date=today)
                ).order_by('-updated_date').select_related('team_leader')
            elif tag == 'tommorrow_follow':
                interested_leads_qs = LeadUser.objects.filter(
                    Q(status='Intrested') & Q(follow_up_date=tomorrow)
                ).order_by('-updated_date').select_related('team_leader')
            else:
                interested_leads_qs = LeadUser.objects.filter(status='Intrested').order_by('-updated_date').select_related('team_leader')
            
            serializer_class = ApiLeadUserSerializer

        elif Team_Leader.objects.filter(email=user.email).exists():
            try:
                team_leader_instance = Team_Leader.objects.get(user=user)
            except Team_Leader.DoesNotExist:
                 return Response({"error": "Team Leader profile not found."}, status=status.HTTP_404_NOT_FOUND)

            if tag == 'pending_follow':
                interested_leads_qs = LeadUser.objects.filter(
                    Q(status='Intrested') & Q(follow_up_date__isnull=False),
                    team_leader=team_leader_instance,
                ).order_by('-updated_date')
            elif tag == 'today_follow':
                interested_leads_qs = LeadUser.objects.filter(
                    Q(status='Intrested') & Q(follow_up_date=today),
                    team_leader=team_leader_instance,
                ).order_by('-updated_date')
            elif tag == 'tommorrow_follow':
                interested_leads_qs = LeadUser.objects.filter(
                    Q(status='Intrested') & Q(follow_up_date=tomorrow),
                    team_leader=team_leader_instance,
                ).order_by('-updated_date')
            else: # Default 'interested' tag
                interested_leads_qs = LeadUser.objects.filter(
                    follow_up_time__isnull=True, 
                    team_leader=team_leader_instance,
                    status='Intrested'
                ).order_by('-updated_date')
            
            serializer_class = ApiLeadUserSerializer

        else:
            try:
                
                team_leader = Team_Leader.objects.filter(email=user.email).last()
                if team_leader:
                    interested_leads_qs = Team_LeadData.objects.filter(team_leader=team_leader, status='Intrested')
                    serializer_class = ApiTeamLeadDataSerializer
                else:
                     interested_leads_qs = Team_LeadData.objects.none()
                     serializer_class = ApiTeamLeadDataSerializer
            except Exception:
                 return Response({"error": "Could not determine user role for this view."}, status=status.HTTP_400_BAD_REQUEST)


        paginated_qs = self.paginator.paginate_queryset(interested_leads_qs, request, view=self)
        serializer = serializer_class(paginated_qs, many=True)
        
        return self.paginator.get_paginated_response(serializer.data)
    



# USER ACTIVE TOGGLE API 

class ToggleUserActiveAPIView(APIView):
    """
    API to toggle the 'user_active' status for Staff, Admin, or TeamLeader.
    
    """
    permission_classes = [IsAuthenticated, CustomIsSuperuser  ] 

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        user_type = request.data.get('user_type')
        is_active_str = request.data.get('is_active') 

        if not all([user_id, user_type, is_active_str is not None]):
            return Response(
                {"error": "user_id (profile_id), user_type, aur is_active zaroori hain."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_active_bool = str(is_active_str).lower() == 'true'
        
        user_instance_email = None
        try:
            if user_type == 'staff':
                profile = Staff.objects.get(id=user_id)
                user_instance_email = profile.email
            elif user_type == 'admin':
                profile = Admin.objects.get(id=user_id)
                user_instance_email = profile.email
            elif user_type == 'teamlead':
                profile = Team_Leader.objects.get(id=user_id)
                user_instance_email = profile.email
            else:
                return Response(
                    {"error": "Invalid user_type. Sirf 'staff', 'admin', ya 'teamlead' allowed hai."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except (Staff.DoesNotExist, Admin.DoesNotExist, Team_Leader.DoesNotExist):
             return Response(
                {"error": f"Profile not found for user_type '{user_type}' with id {user_id}."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not user_instance_email:
            return Response({"error": "Profile mil gayi lekin usse koi email linked nahi hai."}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_to_update = User.objects.get(email=user_instance_email)
            user_to_update.user_active = is_active_bool 
            user_to_update.save()
            
            return Response(
                {
                    'status': 'success', 
                    'user_email': user_to_update.email,
                    'user_active_is_now': user_to_update.user_active
                },
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": f"User not found with email {user_instance_email}."},
                status=status.HTTP_404_NOT_FOUND
            )



# API: SUPERUSER STAFF LEADS (BY STATUS)

class SuperUserStaffLeadsAPIView(APIView):
    """
    API to retrieve a paginated list of all staff-assigned leads, filtered by status tag.
    This view is intended for administrative oversight.
    """

    permission_classes = [IsAuthenticated, CustomIsSuperuser]
    pagination_class = StandardResultsSetPagination 

    def get(self, request, tag, format=None):
        paginator = self.pagination_class()
        
        base_queryset = LeadUser.objects.all()

        status_map = {
            'total_lead': 'Leads',
            'visits': 'Visit',
            'interested': 'Intrested',
            'not_interested': 'Not Interested',
            'other_location': 'Other Location',
            'not_picked': 'Not Picked',
            'lost': 'Lost'
        }

        if tag in status_map:
            queryset = base_queryset.filter(status=status_map[tag])
        else:
            return Response(
                {"error": f"Invalid tag: {tag}. Valid tags are: {list(status_map.keys())}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = queryset.order_by('-updated_date')
        
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = ApiLeadUserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ApiLeadUserSerializer(queryset, many=True)
        return Response(serializer.data)



# API: ADMIN STAFF LEADS 

class AdminStaffLeadsAPIView(APIView):
    """
    API endpoint exclusively for the Admin role, designed to filter and retrieve leads assigned to their subordinate Team Leaders and Staff.
    """

   
    
    permission_classes = [IsAuthenticated, IsCustomAdminUser] 
    pagination_class = StandardResultsSetPagination

    def get(self, request, tag, format=None):
        paginator = self.pagination_class()
        user = request.user
        
        admin_instance = Admin.objects.filter(user=user).last() 
        if not admin_instance:
            admin_instance = Admin.objects.filter(self_user=user).last()
            if not admin_instance:
                 return Response({"error": "Admin profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        teamleader_instance = Team_Leader.objects.filter(admin=admin_instance)
        base_queryset = LeadUser.objects.filter(team_leader__in=teamleader_instance)

        status_map = {
            'total_lead': 'Leads',
            'visits': 'Visit',
            'interested': 'Intrested',
            'not_interested': 'Not Interested',
            'other_location': 'Other Location',
            'not_picked': 'Not Picked'
            
        }

        if tag in status_map:
            queryset = base_queryset.filter(status=status_map[tag])
        else:
            return Response(
                {"error": f"Invalid tag: {tag}. Valid tags are: {list(status_map.keys())}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = queryset.order_by('-updated_date')
        
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = ApiLeadUserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ApiLeadUserSerializer(queryset, many=True)
        return Response(serializer.data)



# STAFF ADD API 

class StaffAddAPIView(APIView):
    """
    API endpoint for creating a new Staff user and their associated profile.
    (Can be executed by Team Leader, Admin, or Superuser).
    [FIXED] UnboundLocalError has been resolved.
    """
    
    permission_classes = [CustomIsSuperuser]
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        serializer = StaffCreateSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            staff_instance = serializer.save()
        except Exception as e:
            return Response({"error": f"Failed to save serializer: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            read_serializer = StaffProfileSerializer(staff_instance, context={'request': request})
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"message": f"Staff created (ID: {staff_instance.id}) but response serialization failed: {e}"}, 
                status=status.HTTP_201_CREATED
            )
        


# TEAM LEADER ADD API (ADD_TEAM_LEADER_USER)

class TeamLeaderSuperAdminAddAPIView(APIView):
    """
    api to make new teamleader only for superuser
    """
    permission_classes = [CustomIsSuperuser] 
    parser_classes = (MultiPartParser, FormParser) 

    def post(self, request, *args, **kwargs):
       
        if request.user.is_superuser and not request.data.get('admin_id'):
           
            return Response({"error": "Admin ID is required for Superusers to assign the new Team Leader."}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = TeamLeaderCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                team_leader_instance = serializer.save()
            except Exception as e:
                 return Response({"error": f"Failed to save: {e}"}, status=status.HTTP_400_BAD_REQUEST)
            
            read_serializer = ProductivityTeamLeaderSerializer(team_leader_instance, context={'request': request})
            
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# TEAM LEADER EDIT API (GET / PATCH) 

class TeamLeaderEditAPIView(APIView):
    """
    this api is used for edit the team leader by superuser.
    """
    
    permission_classes = [IsAuthenticated, CustomIsSuperuser] 
    
    parser_classes = (MultiPartParser, FormParser) 

    def get_object(self, id):
        
        try:
            return Team_Leader.objects.get(user__id=id)
        except Team_Leader.DoesNotExist:
            raise Http404

    def get(self, request, id, *args, **kwargs):
        """
        fetch all details of one teamleader.
        """
        teamleader = self.get_object(id)
        serializer = ProductivityTeamLeaderSerializer(teamleader, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id, *args, **kwargs):
        """
        update profile of one teamleader .
        """
        teamleader = self.get_object(id)
        serializer = TeamLeaderUpdateSerializer(teamleader, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_teamleader = serializer.save()
            read_serializer = ProductivityTeamLeaderSerializer(updated_teamleader, context={'request': request})
            return Response(read_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, id, *args, **kwargs):
        
        return self.patch(request, id, format)




# STAFF EDIT API (GET / PATCH)

class StaffEditAPIView(APIView):
    """
    API for get and update Staff/Freelancer  profile .
    """
    permission_classes = [ IsAuthenticated , CustomIsSuperuser] 
    parser_classes = (MultiPartParser, FormParser) 

    def get_object(self, id):
        """
        Staff object get by helper method 
        """
        try:
            return Staff.objects.get(id=id)
        except Staff.DoesNotExist:
            raise Http404

    def get(self, request, id, *args, **kwargs):
        """
        fetch all details of one Staff/Freelancer .
        """
        staff = self.get_object(id)
        
        serializer = FullStaffSerializer(staff, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id, *args, **kwargs):
        """
        update profile of one Staff/Freelancer profile.
        """
        staff = self.get_object(id)
        
        serializer = StaffUpdateSerializer(staff, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_staff = serializer.save()
           
            read_serializer = StaffProfileSerializer(updated_staff, context={'request': request})
            return Response(read_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# INCENTIVE SLAB API

class IncentiveSlabStaffAPIView(APIView):
    """
    API to retrieve sales performance and incentive calculations for a staff member, based on month and year.
    """

    permission_classes = [IsAuthenticated , CustomIsSuperuser]

    def get(self, request, staff_id, *args, **kwargs):

        # Filters and Params
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))
        
        # Base Query and User Type Check
        sell_property_qs = Sell_plot.objects.none()
        total_earn = 0
        user_type = None
        
        if request.user.is_staff_new and staff_id == request.user.id:
            staff_email = request.user.email
            sell_property_qs = Sell_plot.objects.filter(
                staff__email=staff_email, 
                updated_date__year=year,
                updated_date__month=month
            )
            # Freelancer check
            user_type = request.user.is_freelancer
            
        elif request.user.is_superuser or request.user.is_team_leader or request.user.is_admin:
            
            if int(staff_id) == 0:
                 return Response({"error": "Staff ID is required."}, status=status.HTTP_400_BAD_REQUEST)
                 
            sell_property_qs = Sell_plot.objects.filter(
                staff__id=staff_id, 
                updated_date__year=year,
                updated_date__month=month
            )
            
            # Freelancer status check 
            try:
                staff_instance = Staff.objects.get(id=staff_id)
                user_type = staff_instance.user.is_freelancer
            except Staff.DoesNotExist:
                 return Response({"error": "Staff member not found."}, status=status.HTTP_404_NOT_FOUND)

        else:
             return Response({"error": "You do not have permission for this action."}, status=status.HTTP_403_FORBIDDEN)
        
        
        # Aggregate Total Earnings
        total_earn_amount = sell_property_qs.aggregate(total_earn=Sum('earn_amount'))
        total_earn = total_earn_amount['total_earn'] if total_earn_amount['total_earn'] else 0
        
        # Serialize Data
        slab_data = Slab.objects.all()
        
        response_data = {
            'sell_property': SellPlotSerializer(sell_property_qs.order_by('-created_date'), many=True).data,
            'slab': SlabSerializer(slab_data, many=True).data, 
            'total_earn': total_earn,
            'year': year,
            'month': month,
            'months_list': [(i, month_name[i]) for i in range(1, 13)],
            'user_type': user_type, # True/False
        }
        return Response(response_data, status=status.HTTP_200_OK)



# STAFF PRODUCTIVITY CALENDAR API

class StaffProductivityCalendarAPIView(APIView):
    """
    API fetches Staff productivity data (leads and calculated salary) 
    for a specific month and year, structured for a calendar view.
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser]
    
    def get(self, request, staff_id, *args, **kwargs):
        
        # Get year and month from query parameters
        try:
            year = int(request.query_params.get('year', datetime.now().year))
            month = int(request.query_params.get('month', datetime.now().month))
        except ValueError:
            return Response({"error": "Invalid year or month format."}, status=status.HTTP_400_BAD_REQUEST)

        # Get Staff Instance and Authorization Check
        try:
            staff = Staff.objects.get(id=staff_id)
        except Staff.DoesNotExist:
            if staff_id == request.user.id and not request.user.is_superuser:
                 staff = Staff.objects.get(user=request.user)
            else:
                return Response({"error": "Staff member not found."}, status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        if not (user.is_superuser or user.is_admin or user.is_team_leader or user.id == staff.user.id):
             return Response({"error": "You do not have permission to view this calendar."}, status=status.HTTP_403_FORBIDDEN)

        days_in_month = monthrange(year, month)[1]
        salary_arg = staff.salary if staff.salary else 0
        
        try:
            salary_float = float(salary_arg)
        except ValueError:
            salary_float = 0

        daily_salary = round(salary_float / days_in_month) if days_in_month > 0 else 0

        leads_data = LeadUser.objects.filter(
            assigned_to=staff,
            updated_date__year=year,
            updated_date__month=month,
            status='Intrested'
        ).values('updated_date__day').annotate(count=Count('id'))

        productivity_data_dict = {day: {'leads': 0, 'salary': 0} for day in range(1, days_in_month + 1)}
        total_salary = 0
        
        for lead in leads_data:
            day = lead['updated_date__day']
            leads_count = lead['count']
            
            if leads_count >= 10:
                daily_earned_salary = daily_salary
            else:
                daily_earned_salary = round((daily_salary / 10) * leads_count, 2)
            
            productivity_data_dict[day] = {'leads': leads_count, 'salary': daily_earned_salary}
            total_salary += daily_earned_salary

        # Structure Data for Calendar
        weekdays = list(calendar.day_name)
        
        productivity_list = []
        for day in range(1, days_in_month + 1):
            date_obj = datetime(year, month, day).date()
            day_data = productivity_data_dict.get(day, {'leads': 0, 'salary': 0})
            
            productivity_list.append({
                'day': day,
                'date': date_obj, 
                'day_name': weekdays[date_obj.weekday()],
                'leads': day_data['leads'],
                'salary': day_data['salary']
            })

        # Final Response
        months_list = [(i, calendar.month_name[i]) for i in range(1, 13)]

        response_data = {
            'staff': StaffProfileSerializer(staff, context={'request': request}).data,
            'year': year,
            'month': month,
            'monthly_salary': salary_arg,
            'total_salary': round(total_salary, 2),
            'months_list': months_list,
            'daily_productivity_data': DailyProductivitySerializer(productivity_list, many=True).data, # Serializer use karo
        }

        return Response(response_data, status=status.HTTP_200_OK)  




# TEAM LEADER PERTICULAR LEADS API

class TeamLeaderParticularLeadsAPIView(APIView):
    """
    API fetches leads assigned to a specific staff member (ID) filtered by status tag.
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser]
    pagination_class = StandardResultsSetPagination # Reuse Standard pagination

    @property
    def paginator(self):
        """Paginator instance for the view."""
        if not hasattr(self, '_paginator'):
            self._paginator = self.pagination_class()
        return self._paginator

    def get(self, request, id, tag, *args, **kwargs):
        
        # Base Query based on Tag
        tag = tag.lower()
        if tag == "intrested":
            status_filter = {'status': 'Intrested'}
        elif tag == "not interested":
            status_filter = {'status': 'Not Interested'}
        elif tag == "other location":
            status_filter = {'status': 'Other Location'}
        elif tag == "lost":
            status_filter = {'status': 'Lost'}
        elif tag == "visit":
            status_filter = {'status': 'Visit'}
        elif tag == "all":
            status_filter = {} # No status filter, shows all leads
        else:
            status_filter = {'status': tag.capitalize()} # Catch other statuses

        
        # Final Query: Filter by Staff ID and Status
        staff_leads_qs = LeadUser.objects.filter(
            assigned_to__id=id,
            **status_filter
        ).order_by('-updated_date')
        
        # Paginate and Serialize
        paginated_qs = self.paginator.paginate_queryset(staff_leads_qs, request, view=self)
        serializer = ApiLeadUserSerializer(paginated_qs, many=True)
        
        response = self.paginator.get_paginated_response(serializer.data)
        response.data['staff_id'] = id
        response.data['status_tag'] = tag
        
        return response
    


# ADMIN PRODUCTIVITY API

class AdminProductivityAPIView(APIView):
    """
    API fetches total productivity (aggregated leads/calls) for ALL Admin users.
    
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser] # Sirf Superuser chala sakta hai
    
    def get(self, request, *args, **kwargs):
        
        # Retrieve all active Admin profiles
        admin_profiles = Admin.objects.filter(self_user__user_active=True)
        total_admins_count = admin_profiles.count()

        # Initialize totals and data list
        admin_data_list = []
        total_all_leads = 0
        total_all_interested = 0
        total_all_not_interested = 0
        total_all_other_location = 0
        total_all_not_picked = 0
        total_all_lost = 0
        total_all_visit = 0
        total_all_calls = 0
        
        date_filter = request.query_params.get('date', None)
        end_date_str = request.query_params.get('endDate', None)

        lead_filter = {}
        lead_filter1 = {}
        date_filter_applied = False
        
        if date_filter and end_date_str:
            try:
                start_date = timezone.make_aware(datetime.strptime(date_filter, '%Y-%m-%d'))
                end_date_dt = datetime.strptime(end_date_str, '%Y-%m-%d')
                end_date = timezone.make_aware(end_date_dt + timedelta(days=1)) - timedelta(seconds=1)
                lead_filter = {'updated_date__range': [start_date, end_date]}
                lead_filter1 = {'created_date__range': [start_date, end_date]}
                date_filter_applied = True
            except ValueError: pass 
        
        elif date_filter:
            try:
                date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
                lead_filter = {'updated_date__date': date_obj}
                lead_filter1 = {'created_date__date': date_obj}
                date_filter_applied = True
            except ValueError: pass

        # Loop over each Admin profile
        for admin_profile in admin_profiles:
            admin_agg_data = {
                'total_leads': 0, 'interested': 0, 'not_interested': 0,
                'other_location': 0, 'not_picked': 0, 'lost': 0, 'visit': 0
            }

            # Get all staff members under this Admin (via Team Leaders)
            staff_members = Staff.objects.filter(team_leader__admin=admin_profile)

            for staff in staff_members:
                if date_filter_applied:
                     leads_by_date = LeadUser.objects.filter(assigned_to=staff, **lead_filter).aggregate(
                         interested=Count('id', filter=Q(status='Intrested')),
                         not_interested=Count('id', filter=Q(status='Not Interested')),
                         other_location=Count('id', filter=Q(status='Other Location')),
                         not_picked=Count('id', filter=Q(status='Not Picked')),
                         lost=Count('id', filter=Q(status='Lost')), visit=Count('id', filter=Q(status='Visit'))
                     )
                     leads_by_date1 = LeadUser.objects.filter(assigned_to=staff, **lead_filter1).aggregate(total_leads=Count('id'))
                else:
                    leads_by_date_all = LeadUser.objects.filter(assigned_to=staff).aggregate(
                        total_leads=Count('id'), interested=Count('id', filter=Q(status='Intrested')),
                        not_interested=Count('id', filter=Q(status='Not Interested')), other_location=Count('id', filter=Q(status='Other Location')),
                        not_picked=Count('id', filter=Q(status='Not Picked')), lost=Count('id', filter=Q(status='Lost')), visit=Count('id', filter=Q(status='Visit'))
                    )
                    leads_by_date = leads_by_date_all
                    leads_by_date1 = {'total_leads': leads_by_date_all['total_leads']}

                admin_agg_data['total_leads'] += leads_by_date1.get('total_leads', 0)
                admin_agg_data['interested'] += leads_by_date.get('interested', 0)
                admin_agg_data['not_interested'] += leads_by_date.get('not_interested', 0)
                admin_agg_data['other_location'] += leads_by_date.get('other_location', 0)
                admin_agg_data['not_picked'] += leads_by_date.get('not_picked', 0)
                admin_agg_data['lost'] += leads_by_date.get('lost', 0)
                admin_agg_data['visit'] += leads_by_date.get('visit', 0)

            # Admin Total Calculations
            total_calls_admin = (
                admin_agg_data['interested'] + admin_agg_data['not_interested'] + 
                admin_agg_data['other_location'] + admin_agg_data['not_picked'] + 
                admin_agg_data['lost'] + admin_agg_data['visit']
            )
            total_leads_admin = admin_agg_data['total_leads']
            visit_percentage = (admin_agg_data['visit'] / total_leads_admin * 100) if total_leads_admin > 0 else 0
            interested_percentage = (admin_agg_data['interested'] / total_leads_admin * 100) if total_leads_admin > 0 else 0

            admin_data_list.append({
                'id': admin_profile.id,
                'name': admin_profile.name,
                'total_leads': total_leads_admin,
                'interested': admin_agg_data['interested'],
                'not_interested': admin_agg_data['not_interested'],
                'other_location': admin_agg_data['other_location'],
                'not_picked': admin_agg_data['not_picked'],
                'lost': admin_agg_data['lost'],
                'visit': admin_agg_data['visit'],
                'visit_percentage': round(visit_percentage, 2),
                'interested_percentage': round(interested_percentage, 2),
                'total_calls': total_calls_admin,
            })

            # Grand Totals Update
            total_all_leads += total_leads_admin
            total_all_interested += admin_agg_data['interested']
            total_all_not_interested += admin_agg_data['not_interested']
            total_all_other_location += admin_agg_data['other_location']
            total_all_not_picked += admin_agg_data['not_picked']
            total_all_lost += admin_agg_data['lost']
            total_all_visit += admin_agg_data['visit']
            total_all_calls += total_calls_admin
        
        # Final Grand Totals
        total_visit_percentage = (total_all_visit / total_all_leads * 100) if total_all_leads > 0 else 0
        total_interested_percentage = (total_all_interested / total_all_leads * 100) if total_all_leads > 0 else 0

        data = {
            'admin_data': StaffProductivityDataSerializer(admin_data_list, many=True).data, # Reuse Staff serializer for data structure
            'task_type': 'admin',
            'total_all_leads': total_all_leads,
            'total_all_interested': total_all_interested,
            'total_all_calls': total_all_calls,
            'total_visit_percentage': round(total_visit_percentage, 2),
            'total_interested_percentage': round(total_interested_percentage, 2),
            'total_staff_count': total_admins_count, 
            'fiter': 3 if request.user.is_superuser else 5, 
        }
        
        return Response(data, status=status.HTTP_200_OK)
    



# FREELANCER PRODUCTIVITY API

class FreelancerProductivityAPIView(APIView):
    """
    API fetches total productivity (aggregated leads/calls)
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser] 
    
    def get(self, request, *args, **kwargs):
        
        date_filter = request.query_params.get('date', None)
        end_date_str = request.query_params.get('endDate', None)
        teamleader_id = request.query_params.get('teamleader_id', None)
        admin_id = request.query_params.get('admin_id', None)
        
        staffs = Staff.objects.filter(user__user_active=True, user__is_freelancer=True)
        fiter_value = 0 
        
        current_user = request.user

        if current_user.is_superuser:
            fiter_value = 1
            if admin_id:
                staffs = staffs.filter(team_leader__admin=admin_id)
            if teamleader_id:
                staffs = staffs.filter(team_leader=teamleader_id)
        
        elif current_user.is_admin:
            fiter_value = 4
            staffs = staffs.filter(team_leader__admin__self_user=current_user)
            if teamleader_id:
                staffs = staffs.filter(team_leader=teamleader_id)

        elif current_user.is_team_leader:
            fiter_value = 2
            team_leader_instance = Team_Leader.objects.filter(user=current_user).last()
            staffs = Staff.objects.filter(team_leader=team_leader_instance)
        
        total_staff_count = staffs.count()

        staff_data_list = []
        total_all_leads = 0
        total_all_interested = 0
        total_all_calls = 0
        total_all_visit = 0
        
        lead_filter = {}
        lead_filter1 = {}
        date_filter_applied = False
        
        if date_filter and end_date_str:
            try:
                start_date = timezone.make_aware(datetime.strptime(date_filter, '%Y-%m-%d'))
                end_date_dt = datetime.strptime(end_date_str, '%Y-%m-%d')
                end_date = timezone.make_aware(end_date_dt + timedelta(days=1)) - timedelta(seconds=1)
                lead_filter = {'updated_date__range': [start_date, end_date]}
                lead_filter1 = {'created_date__range': [start_date, end_date]}
                date_filter_applied = True
            except ValueError: pass 
        
        elif date_filter:
            try:
                date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
                lead_filter = {'updated_date__date': date_obj}
                lead_filter1 = {'created_date__date': date_obj}
                date_filter_applied = True
            except ValueError: pass

        # Loop and Aggregate Data
        for staff in staffs:
            
            # Aggregate leads by Staff Member
            if date_filter_applied:
                 leads_by_date = LeadUser.objects.filter(assigned_to=staff, **lead_filter).aggregate(
                     interested=Count('id', filter=Q(status='Intrested')), 
                     not_interested=Count('id', filter=Q(status='Not Interested')),
                     other_location=Count('id', filter=Q(status='Other Location')),
                     not_picked=Count('id', filter=Q(status='Not Picked')), 
                     lost=Count('id', filter=Q(status='Lost')), visit=Count('id', filter=Q(status='Visit'))
                 )
                 leads_by_date1 = LeadUser.objects.filter(assigned_to=staff, **lead_filter1).aggregate(total_leads=Count('id'))
            else:
                leads_by_date_all = LeadUser.objects.filter(assigned_to=staff).aggregate(
                    total_leads=Count('id'), interested=Count('id', filter=Q(status='Intrested')),
                    not_interested=Count('id', filter=Q(status='Not Interested')), other_location=Count('id', filter=Q(status='Other Location')),
                    not_picked=Count('id', filter=Q(status='Not Picked')), lost=Count('id', filter=Q(status='Lost')), visit=Count('id', filter=Q(status='Visit'))
                )
                leads_by_date = leads_by_date_all
                leads_by_date1 = {'total_leads': leads_by_date_all['total_leads']}

            
            total_calls = (
                leads_by_date.get('interested', 0) + leads_by_date.get('not_interested', 0) + 
                leads_by_date.get('other_location', 0) + leads_by_date.get('not_picked', 0) + 
                leads_by_date.get('lost', 0) + leads_by_date.get('visit', 0)
            )
            total_leads_for_staff = leads_by_date1.get('total_leads', 0)
            visit_percentage = (leads_by_date.get('visit', 0) / total_leads_for_staff * 100) if total_leads_for_staff > 0 else 0
            interested_percentage = (leads_by_date.get('interested', 0) / total_leads_for_staff * 100) if total_leads_for_staff > 0 else 0

            staff_data_list.append({
                'id': staff.id, 'name': staff.name,
                'total_leads': total_leads_for_staff,
                'interested': leads_by_date.get('interested', 0),
                'not_interested': leads_by_date.get('not_interested', 0),
                'other_location': leads_by_date.get('other_location', 0),
                'not_picked': leads_by_date.get('not_picked', 0),
                'lost': leads_by_date.get('lost', 0),
                'visit': leads_by_date.get('visit', 0),
                'visit_percentage': round(visit_percentage, 2),
                'interested_percentage': round(interested_percentage, 2),
                'total_calls': total_calls,
            })

            # Grand Totals Update
            total_all_leads += total_leads_for_staff
            total_all_interested += leads_by_date.get('interested', 0)
            total_all_calls += total_calls
            total_all_visit += leads_by_date.get('visit', 0)
        
        #Final Grand Totals
        total_visit_percentage = (total_all_visit / total_all_leads * 100) if total_all_leads > 0 else 0
        total_interested_percentage = (total_all_interested / total_all_leads * 100) if total_all_leads > 0 else 0

        # Final Response
        data = {
            'staff_data': StaffProductivityDataSerializer(staff_data_list, many=True).data, # Reuse Staff serializer
            'task_type': 'freelancer',
            'total_all_leads': total_all_leads,
            'total_all_interested': total_all_interested,
            'total_all_calls': total_all_calls,
            'total_visit_percentage': round(total_visit_percentage, 2),
            'total_interested_percentage': round(total_interested_percentage, 2),
            'total_staff_count': total_staff_count, 
            'fiter': fiter_value,
        }
        
        return Response(data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated , CustomIsSuperuser]) 
def get_team_leader_dashboard_api(request):

    user = request.user

    if not user.is_team_leader:
        return Response(
            {"error": "Only Team Leaders can access this endpoint."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        team_lead = Team_Leader.objects.get(user=user)
    except Team_Leader.DoesNotExist:
        return Response(
            {"error": "Team Leader profile not found for this user."},
            status=status.HTTP_404_NOT_FOUND
        )

    staff_members = Staff.objects.filter(team_leader=team_lead)
    
    unassigned_leads = Team_LeadData.objects.filter(assigned_to=None, team_leader=team_lead)

    interested_leads = LeadUser.objects.filter(status="Intrested")

    lost_leads = LeadUser.objects.filter(status="Lost")

    total_leads, total_lost_leads, total_customer, total_maybe = 0, 0, 0, 0

    for staff in staff_members:
        staff_leads = LeadUser.objects.filter(assigned_to=staff)
        total_leads += staff_leads.filter(status="Leads").count()
        total_lost_leads += staff_leads.filter(status="Lost_Leads").count()
        total_customer += staff_leads.filter(status="Customer").count()
        total_maybe += staff_leads.filter(status="Maybe").count()

    total_leads += unassigned_leads.filter(status="Leads").count()
    total_lost_leads += unassigned_leads.filter(status="Lost_Leads").count()
    total_customer += unassigned_leads.filter(status="Customer").count()
    total_maybe += unassigned_leads.filter(status="Maybe").count()
    
    # Final counts
    total_uplode_leads = unassigned_leads.count()
    customer_count = interested_leads.count()
    lost_count = lost_leads.count()

    user_logs_data = ApiStaffSerializer(staff_members, many=True).data
    leads2_data = ApiTeamLeadDataSerializer(unassigned_leads, many=True).data
    leads3_data = ApiLeadUserSerializer(interested_leads, many=True).data
    leads4_data = ApiLeadUserSerializer(lost_leads, many=True).data

    #  Final response
    response_data = {
        'total_uplode_leads': total_uplode_leads,
        'total_leads': total_leads,
        'total_lost_leads': total_lost_leads,
        'total_customer': total_customer,
        'total_maybe': total_maybe,
        'customer_count': customer_count,
        'lost_count': lost_count,
        'user_logs': user_logs_data, 
        'leads2': leads2_data,       
        'leads3': leads3_data,       
        'leads4': leads4_data      
    }

    return Response(response_data, status=status.HTTP_200_OK)



class TeamCustomerLeadsAPIView(APIView):
    """
    API to retrieve leads with 'Intrested' status, filtered by follow-up status and user role.
    """
 
    permission_classes = [IsAuthenticated , CustomIsSuperuser]
    pagination_class = StandardResultsSetPagination
    
    def get(self, request, tag, format=None):
        
        paginator = self.pagination_class()
        
        
        search_query = request.query_params.get('search', None)
        
        if search_query:
           
            queryset = LeadUser.objects.filter(
                Q(name__icontains=search_query) | Q(call__icontains=search_query) | Q(team_leader__name__icontains=search_query),
                status='Intrested'
            )
            serializer_class = ApiLeadUserSerializer 
        
        else:
           
            user = request.user
            today = timezone.now().date()
            tomorrow = today + timedelta(days=1)
            team_leader_instance = Team_Leader.objects.filter(email=user.email).last()
            
            queryset = None
            serializer_class = None 

            if user.is_superuser:
                base_queryset = LeadUser.objects.filter(status='Intrested')
                if tag == 'pending_follow':
                    queryset = base_queryset.filter(follow_up_date__isnull=False)
                elif tag == 'today_follow':
                    queryset = base_queryset.filter(follow_up_date=today)
                elif tag == 'tommorrow_follow':
                    queryset = base_queryset.filter(follow_up_date=tomorrow)
                else:
                    queryset = base_queryset
                serializer_class = ApiLeadUserSerializer

            elif user.is_team_leader:
                base_queryset = LeadUser.objects.filter(team_leader=team_leader_instance, status='Intrested')
                if tag == 'pending_follow':
                    queryset = base_queryset.filter(follow_up_date__isnull=False)
                elif tag == 'today_follow':
                    queryset = base_queryset.filter(follow_up_date=today)
                elif tag == 'tommorrow_follow':
                    queryset = base_queryset.filter(follow_up_date=tomorrow)
                else:
                   
                    queryset = base_queryset.filter(follow_up_time__isnull=True)
                serializer_class = ApiLeadUserSerializer

            else:
                
                queryset = Team_LeadData.objects.filter(team_leader=team_leader_instance, status='Intrested')
                serializer_class = ApiTeamLeadDataSerializer
        
        if queryset is not None:
            queryset = queryset.order_by('-updated_date')
        else:
            queryset = LeadUser.objects.none() # Empty result

        page = paginator.paginate_queryset(queryset, request, view=self)
        
        if serializer_class is None:
             return Response({"error": "Could not determine serializer."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if page is not None:
            serializer = serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Non-paginated response
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



# API: EXPORT LEADS (STATUS WISE) 

class ExportLeadsStatusWiseAPIView(APIView):
    """
    API to export leads data to an Excel file (.xlsx) filtered by status and date range.
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser]

    def post(self, request, *args, **kwargs):
        serializer = LeadExportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')
        all_interested = validated_data.get('all_interested')
        staff_id = validated_data.get('staff_id')
        
        lead_status = validated_data.get('lead_status') 
        
        staff_instance = None
        
        end_date_for_range = end_date + timedelta(days=1)
        
        leads = None
        if all_interested != "1":
            staff_instance = Staff.objects.filter(id=staff_id).last()
            if not staff_instance:
                 return Response({"error": f"Staff with id={staff_id} not found."}, status=status.HTTP_404_NOT_FOUND)

            leads = LeadUser.objects.filter(
                updated_date__range=[start_date, end_date_for_range],
                status=lead_status, 
                assigned_to=staff_instance,
            )
        else:
            if request.user.is_superuser:
                leads = LeadUser.objects.filter(
                    updated_date__range=[start_date, end_date_for_range],
                    status="Intrested",
                )
            elif request.user.is_team_leader:
                user_email = request.user.username 
                team_leader_instance = Team_Leader.objects.filter(email=user_email).last()
                leads = LeadUser.objects.filter(
                    team_leader=team_leader_instance,
                    updated_date__range=[start_date, end_date_for_range],
                    status="Intrested",
                )
            else:
                return Response({"error": "You do not have permission for 'all_interested' export."}, status=status.HTTP_403_FORBIDDEN)
        
        if leads is None:
            leads = LeadUser.objects.none()

        # Data Preparation
        data = []
        for lead in leads:
            data.append({
                'Name': lead.name,
                'Call': lead.call,
                'Status': lead.status,
                'staff Name': lead.assigned_to.name if lead.assigned_to else 'N/A',
                'Message': lead.message,
                'Date': localtime(lead.updated_date).strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        df = pd.DataFrame(data)

        # Response Generation
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")

        if all_interested == "1":
            response['Content-Disposition'] = f'attachment; filename=interested_{start_str}_to_{end_str}.xlsx'
        else:
            if staff_instance:
                response['Content-Disposition'] = f'attachment; filename={staff_instance.name}_{lead_status}_{start_str}_to_{end_str}.xlsx'
            else:
                response['Content-Disposition'] = f'attachment; filename=export_{lead_status}_{start_str}_to_{end_str}.xlsx'

        with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Leads')

        return response



# API: TEAM LEADER LEADS REPORT (BY STATUS)

class TeamLeadSuperAdminLeadsReportAPIView(APIView):
    """
    API to retrieve a status-wise report of leads belonging to a specific Team Leader.
    This view is accessible by Superusers .
    """

    permission_classes = [IsAuthenticated , CustomIsSuperuser]
    pagination_class = StandardResultsSetPagination 

    def get(self, request, id, tag, format=None):
        paginator = self.pagination_class()

        base_queryset = LeadUser.objects.filter(team_leader=id)

        
        allowed_tags = ["Intrested", "Not Interested", "Other Location", "Lost", "Visit"]

        if tag in allowed_tags:
            staff_leads = base_queryset.filter(status=tag)
        else:
            staff_leads = base_queryset

        staff_leads = staff_leads.order_by('-updated_date')

        page = paginator.paginate_queryset(staff_leads, request, view=self)

        if page is not None:
            serializer = ApiLeadUserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ApiLeadUserSerializer(staff_leads, many=True)
        return Response(serializer.data)
    

# API: ADD SELL PLOT (FREELANCER) VIEW

class AddSellPlotAPIView(APIView):
    """
    API for endpoint 'add_sell_freelancer' function .
    GET: give tha staff and admin list t fill the form .
    POST: make new sell plot record .
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser]

    def get(self, request, id, format=None):
        
        admins = Admin.objects.all()
        
        admin_serializer = DashboardAdminSerializer(admins, many=True)
        
        response_data = {
            'admins': admin_serializer.data,
            'staffs': [] 
        }
        
        if request.user.is_team_leader:
            staffs = Staff.objects.filter(team_leader__email=request.user.email)
            staff_serializer = ApiStaffSerializer(staffs, many=True)
            response_data['staffs'] = staff_serializer.data
            
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request, id, format=None):
       
        
        serializer = SellPlotCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            sell_obj = serializer.save()
            
            output_serializer = SellPlotSerializer(sell_obj)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  




class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000

    
class VisitLeadsAPIView(APIView):
    """
    GET /accounts/api/leads/visit/?tag=<tag>&search=<q>
    - If tag is provided it MUST be one of allowed_tags, otherwise returns 400.
    - If no tag provided, returns full list (or filtered by search).
    """
    permission_classes = [IsAuthenticated]   # change if you want stricter access
    pagination_class = StandardResultsSetPagination

    # allowed tags (lowercase). include common typo if you want
    ALLOWED_TAGS = {"pending_follow", "today_follow", "tomorrow_follow"}

    def get(self, request, format=None):
        # get and normalize tag/search
        tag = (request.query_params.get("tag") or "").strip().lower()
        search_query = (request.query_params.get("search") or "").strip()

        # If tag provided, validate it
        if tag:
            if tag not in self.ALLOWED_TAGS:
                return Response({
                    "error": "Invalid tag provided.",
                    "provided_tag": tag,
                    "allowed_tags": sorted(list(self.ALLOWED_TAGS))
                }, status=status.HTTP_400_BAD_REQUEST)

            # normalize synonyms (map tommorrow typo to canonical)
            if tag in ("tommorrow_follow", "tomorrow_follow"):
                tag = "tomorrow_follow"

        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        STATUS_INTERESTED = "Intrested"

        queryset = LeadUser.objects.filter(status=STATUS_INTERESTED)

        # Search handling (search should be allowed even without tag)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(call__icontains=search_query) |
                Q(team_leader__name__icontains=search_query)
            ).order_by("-updated_date")
        else:
            # tag-based filtering only when tag provided
            if tag == "pending_follow":
                queryset = queryset.filter(follow_up_date__isnull=False).order_by("-updated_date")
            elif tag == "today_follow":
                queryset = queryset.filter(follow_up_date=today).order_by("-updated_date")
            elif tag == "tomorrow_follow":
                queryset = queryset.filter(follow_up_date=tomorrow).order_by("-updated_date")
            else:
                # no tag -> return all (ordered)
                queryset = queryset.order_by("-updated_date")

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = ApiLeadUserSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)



# API: PROJECT (LIST & CREATE)

class ProjectListCreateAPIView(APIView):
    """
    API endpoint which handles both 'project_list' and 'project_add' .
    GET: give list of all projects.
    POST: make new project (with file upload).
    """
    permission_classes = [IsAuthenticated , CustomIsSuperuser]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, *args, **kwargs):
        """
        return list of all projects.
        """
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        make new project .
        """
        serializer = ProjectSerializer(data=request.data)
        
        if serializer.is_valid():
           
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    



# API: ACTIVITY LOGS (BY ROLE)

from rest_framework.views import APIView

class ActivityLogsAPIView(APIView):
    """
    API endpoint to retrieve activity logs based on the authenticated user's role and hierarchy (paginated).
    """
   
    permission_classes = [IsAuthenticated , CustomIsSuperuser]
    pagination_class = ActivityLogPagination # Custom pagination

    def get(self, request, format=None):
        paginator = self.pagination_class()
        user = request.user
        
        queryset = ActivityLog.objects.none() # Start with an empty queryset

        if user.is_superuser:
            queryset = ActivityLog.objects.all()
        
        elif user.is_admin:
            admin_user = Admin.objects.filter(email=user.email).last()
            if admin_user:
                queryset = ActivityLog.objects.filter(admin=admin_user)
        
        elif user.is_team_leader:
            team_leader_user = Team_Leader.objects.filter(email=user.email).last()
            if team_leader_user:
                queryset = ActivityLog.objects.filter(team_leader=team_leader_user)

        elif user.is_staff_new:
            staff_instance = Staff.objects.filter(email=user.email).last()
            
            # Staff can see logs linked to their user OR their staff profile
            if staff_instance:
                 queryset = ActivityLog.objects.filter(Q(user=user) | Q(staff=staff_instance))
            else:
                queryset = ActivityLog.objects.filter(user=user)
        
        ordered_queryset = queryset.order_by('-created_date')
        
        page = paginator.paginate_queryset(ordered_queryset, request, view=self)
        
        if page is not None:
            serializer = ActivityLogSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ActivityLogSerializer(ordered_queryset, many=True)
        return Response(serializer.data)
    




def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_type(user):
    if user.is_superuser: return "Super User"
    elif user.is_admin: return "Admin User"
    elif user.is_team_leader: return "Team Leader User"
    elif user.is_staff_new: return "Staff User"
    return "User"



@api_view(['POST']) 
@permission_classes([IsAuthenticated , CustomIsSuperuser])
def update_lead_user_api(request, id):
    """
    API endpoint to update lead status, message, and follow-up.
    The lead model updated (LeadUser or Team_LeadData) is determined by the logged-in user's role.
    """
    user = request.user
    
    lead_object = None
    model_type = None
    
    try:
        if user.is_superuser:
            lead_object = get_object_or_404(Team_LeadData, id=id)
            model_type = 'Team_LeadData'
        elif user.is_staff_new:
            lead_object = get_object_or_404(LeadUser, id=id)
            model_type = 'LeadUser'
        elif user.is_team_leader:
            lead_object = get_object_or_404(LeadUser, id=id)
            model_type = 'LeadUser'
        else:
            return Response({"error": "You do not have permission for this lead type."},
                            status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({"error": f"Lead with id={id} not found."}, 
                        status=status.HTTP_404_NOT_FOUND)

    current_status = lead_object.status

    serializer = LeadUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated_data = serializer.validated_data
    new_status = validated_data.get('status')
    message = validated_data.get('message', lead_object.message)
    follow_date = validated_data.get('followDate')
    follow_time = validated_data.get('followTime')

    #  Special Logic: "Not Picked"
    if new_status == "Not Picked" and model_type == 'LeadUser':
        try:
            Team_LeadData.objects.create(
                user=lead_object.user,
                name=lead_object.name,
                call=lead_object.call,
                status="Leads", 
                email=lead_object.email,
            )
            lead_object.delete()
            return Response({'message': 'Success: Lead moved to Team_LeadData'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Failed to move lead: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Normal Update Logic
    lead_object.status = new_status
    lead_object.message = message

    if (user.is_team_leader or user.is_staff_new) and model_type == 'LeadUser':
        if follow_date:
            lead_object.follow_up_date = follow_date
        if follow_time:
            lead_object.follow_up_time = follow_time
            
    lead_object.save()

    try:
        history_leads_obj = lead_object if isinstance(lead_object, LeadUser) else None
        
        Leads_history.objects.create(
            leads=history_leads_obj,
            lead_id=id, 
            status=new_status,
            name=lead_object.name,
            message=message,
        )
    except Exception as e:
        print(f"Failed to create Leads_history: {e}")


    user_type = get_user_type(user)
    tagline = f"Lead status changed from {current_status} to {new_status} by user[Email: {user.email}, {user_type}]"
    tag2 = new_status
    ip = get_client_ip(request)

    if user.is_staff_new:
        admin_instance = Staff.objects.filter(email=user.email).last()
        if admin_instance:
            my_user2 = admin_instance.team_leader
            ActivityLog.objects.create(
                staff=admin_instance,
                team_leader=my_user2,
                description=tagline,
                ip_address=ip,
                email=user.email,
                user_type=user_type,
                activity_type=tag2,
                name=user.name,
            )
            
    return Response({'message': 'Success'}, status=status.HTTP_200_OK)




# API: ADMIN DASHBOARD - TEAM LEADER REPORT

class AdminTeamLeaderReportAPIView(APIView):
    """
    API endpoint exclusively for Admin users to retrieve a report showing all subordinate Team Leaders and aggregated lead counts.
    """
    
    permission_classes = [IsAuthenticated, IsCustomAdminUser]

    def get(self, request, format=None):
        user = request.user
        
        
        try:
            admin_profile = Admin.objects.get(email=user.username) 
        except Admin.DoesNotExist:
            return Response(
                {"error": "Admin profile not found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        team_leaders_list = Team_Leader.objects.filter(admin=admin_profile)

        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        today = timezone.now().date()

        if start_date_str and end_date_str:
            start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
            end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)) - timedelta(seconds=1)
        else:
            start_date = timezone.make_aware(datetime.combine(today, datetime.min.time()))
            end_date = timezone.make_aware(datetime.combine(today, datetime.max.time()))
        
        lead_filter = {'updated_date__range': [start_date, end_date]}
        base_queryset = LeadUser.objects.filter(team_leader__in=team_leaders_list, **lead_filter)
        
        total_leads = base_queryset.filter(status="Leads").count()
        total_interested_leads = base_queryset.filter(status="Intrested").count()
        total_not_interested_leads = base_queryset.filter(status="Not Interested").count()
        total_other_location_leads = base_queryset.filter(status="Other Location").count()
        total_not_picked_leads = base_queryset.filter(status="Not Picked").count()
        total_lost_leads = base_queryset.filter(status="Lost").count()
        total_visits_leads = base_queryset.filter(status="Visit").count()

        setting = Settings.objects.filter().last()

        team_leaders_data = ProductivityTeamLeaderSerializer(team_leaders_list, many=True).data
        setting_data = DashboardSettingsSerializer(setting).data if setting else None

        response_data = {
            'counts': {
                'total_leads': total_leads,
                'total_interested_leads': total_interested_leads,
                'total_not_interested_leads': total_not_interested_leads,
                'total_other_location_leads': total_other_location_leads,
                'total_not_picked_leads': total_not_picked_leads,
                'total_lost_leads': total_lost_leads,
                'total_visits_leads': total_visits_leads,
            },
            'team_leaders_list': team_leaders_data,
            'setting': setting_data,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    



# API: ADMIN - ADD TEAM LEADER

class TeamLeaderAddAPIView(APIView):
    """
    API endpoint for creating a new Team Leader user and managing related data.
    Access is restricted solely to Admin users.
    """
   
    
    permission_classes = [IsAuthenticated, IsCustomAdminUser]
   
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, format=None):
        """
        Returns data for the 'Select Admin' dropdown on the form..
        """
        all_admins = User.objects.filter(is_admin=True)
        serializer = DashboardUserSerializer(all_admins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """
        creates new team leader .
        """
        
        serializer = TeamLeaderCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
      
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class AdminStaffDashboardAPIView(APIView):
    """
    API endpoint for Admin Dashboard -> Staff Users Page.
    GET: Fetches Counts for 7 Cards (Including Earning) and Clean Staff List.
    [FIX]: Removed 'filter_status' from response.
    """
    permission_classes = [IsAuthenticated, IsCustomAdminUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, format=None):
        # Get Admin Profile
        try:
            admin_instance = Admin.objects.get(self_user=request.user)
        except Admin.DoesNotExist:
            return Response({"error": "Admin profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get Team Leaders under this Admin
        team_leaders = Team_Leader.objects.filter(admin=admin_instance)

        # Get Staffs under these Team Leaders
        staffs = Staff.objects.filter(
            team_leader__in=team_leaders,
            #user__user_active=True, 
            user__is_freelancer=False
        ).select_related('team_leader', 'user')

        # --- DATE FILTER LOGIC ---
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        today = timezone.now().date()
        
        date_filter = {}
        create_filter = {}
        sell_filter = {}

        if start_date_str and end_date_str:
            try:
                s_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                if isinstance(end_date_str, str):
                    e_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                else:
                    e_date = end_date_str
                
                start_date = timezone.make_aware(datetime.combine(s_date, datetime.min.time()))
                end_date = timezone.make_aware(e_date + timedelta(days=1)) - timedelta(seconds=1)
                
                date_filter = {'updated_date__range': [start_date, end_date]}
                create_filter = {'created_date__range': [start_date, end_date]}
                sell_filter = {'date__range': [start_date.date(), end_date.date()]}
            except ValueError:
                pass 

        # --- CALCULATE CARDS (Aggregated for Admin) ---
        all_staff_leads = LeadUser.objects.filter(assigned_to__in=staffs)
        
        total_leads = all_staff_leads.filter(status="Leads", **create_filter).count()
        total_visit = all_staff_leads.filter(status="Visit", **date_filter).count()
        total_interested = all_staff_leads.filter(status="Intrested", **date_filter).count()
        total_not_interested = all_staff_leads.filter(status="Not Interested", **date_filter).count()
        total_other_location = all_staff_leads.filter(status="Other Location", **date_filter).count()
        total_not_picked = all_staff_leads.filter(status="Not Picked", **date_filter).count()
       

        # Calculate Total Earning
        sell_qs = Sell_plot.objects.filter(staff__in=staffs)
        if sell_filter:
            sell_qs = sell_qs.filter(**sell_filter)
            
        total_earning_agg = sell_qs.aggregate(total=Sum('earn_amount'))
        total_earning = float(total_earning_agg['total']) if total_earning_agg['total'] else 0.0

        counts_data = {
            'total_leads': total_leads,
            'total_visit': total_visit,
            'interested': total_interested,
            'not_interested': total_not_interested,
            'other_location': total_other_location,
            'not_picked': total_not_picked,
            'total_earning': total_earning,
            
        }

        # --- STAFF LIST DATA ---
        staff_list_data = []
        for staff in staffs:
            s_sell_qs = Sell_plot.objects.filter(staff=staff)
            if sell_filter:
                s_sell_qs = s_sell_qs.filter(**sell_filter)
            
            s_earn_agg = s_sell_qs.aggregate(total=Sum('earn_amount'))
            s_earn = float(s_earn_agg['total']) if s_earn_agg['total'] else 0.0

            s_leads_count = LeadUser.objects.filter(assigned_to=staff, status="Leads").count()

            staff_list_data.append({
                'id': staff.id,
                'user_id': staff.user.id,
                'name': staff.name,
                'team_leader_name': staff.team_leader.name if staff.team_leader else "N/A",
                'mobile': staff.mobile,
                'created_date': staff.created_date,
                'is_active': staff.user.user_active,
                'total_earned': s_earn,
                'leads_count': s_leads_count
            })

        setting = Settings.objects.filter().last()
        
        response_data = {
            "counts": counts_data,
            "staff_list": staff_list_data,
            "setting": DashboardSettingsSerializer(setting).data if setting else None,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)






class AdminStaffAddAPIView(APIView):
    """
    API endpoint exclusively for the Admin user to create a new Staff member.
    The GET method retrieves the list of subordinate Team Leaders for the assignment dropdown.
    """
    
    permission_classes = [IsAuthenticated, IsCustomAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, format=None):
        """
        Returns data for the 'Select Team Leader' dropdown on the form.
        """
        try:
            all_teamleader = Team_Leader.objects.filter(admin__self_user=request.user)
        except FieldError:
            all_teamleader = Team_Leader.objects.filter(admin__user=request.user)
            
        serializer = ProductivityTeamLeaderSerializer(all_teamleader, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """
        create new staff.
        """
        
        serializer = StaffCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            team_leader_id = request.data.get('team_leader')
            try:
                team_leader = Team_Leader.objects.get(id=team_leader_id)
                admin_profile = Admin.objects.get(self_user=request.user) 
                
                if team_leader.admin != admin_profile:
                    return Response(
                        {"error": "You can only assign staff to your own Team Leaders."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Exception as e:
                 return Response({"error": f"Invalid Team Leader: {e}"}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class SuperUserTeamLeaderListAPIView(APIView):
    """
    API endpoint exclusively for the Superuser to retrieve a complete list of all Team Leaders in the database.
    """
   
    
    permission_classes = [IsAuthenticated, CustomIsSuperuser]
    pagination_class = StandardResultsSetPagination 

    def get(self, request, format=None):
        paginator = self.pagination_class()
        
        team_leaders = Team_Leader.objects.all().order_by('id')
        
        page = paginator.paginate_queryset(team_leaders, request, view=self)
        
        if page is not None:
            serializer = ProductivityTeamLeaderSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ProductivityTeamLeaderSerializer(team_leaders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)    
    




# API: SUPERUSER - TEAM LEADER DASHBOARD (CARDS + LIST) 

class SuperUserTeamLeaderDashboardAPIView(APIView):
    """
    API for Superuser's 'Team Leader List' dashboard (add_team_leader_admin_side).
    Provides all card counts (at the top) and the paginated list of Team Leaders.
    """
    permission_classes = [IsAuthenticated, CustomIsSuperuser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, format=None):
        paginator = self.pagination_class()
        
        # ---  Get Team Leader List (Paginated) ---
        team_leaders_qs = Team_Leader.objects.all().order_by('name')
        
        page = paginator.paginate_queryset(team_leaders_qs, request, view=self)
        team_leaders_serializer = ProductivityTeamLeaderSerializer(page, many=True)

        # ---  Calculate All Card Counts ---
        active_staff_count = User.objects.filter(is_staff_new=True, is_user_login=True).count()
        total_staff_count = User.objects.filter(is_staff_new=True).count()
        total_leads = LeadUser.objects.filter(status="Leads").count()
        total_interested = LeadUser.objects.filter(status="Intrested").count()
        total_not_interested = LeadUser.objects.filter(status="Not Interested").count()
        total_other_location = LeadUser.objects.filter(status="Other Location").count()
        total_not_picked = LeadUser.objects.filter(status="Not Picked").count()
        total_lost = LeadUser.objects.filter(status="Lost").count()
        total_visits = LeadUser.objects.filter(status="Visit").count()

        # ---  Calculate Followup Counts ---
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        pending_followups = LeadUser.objects.filter(
            Q(status='Intrested') & Q(follow_up_date__isnull=False)
        ).count()
        today_followups = LeadUser.objects.filter(
            Q(status='Intrested') & Q(follow_up_date=today)
        ).count()
        tomorrow_followups = LeadUser.objects.filter(
            Q(status='Intrested') & Q(follow_up_date=tomorrow)
        ).count()
        
        counts_data = {
            'pending_followups': pending_followups,
            'tomorrow_followups': tomorrow_followups,
            'today_followups': today_followups,
            'total_leads': total_leads,
            'total_visit': total_visits,
            'interested': total_interested,
            'not_interested': total_not_interested,
            'other_location': total_other_location,
            'not_picked': total_not_picked,
            'total_staff': total_staff_count,
            'active_staff': active_staff_count,
            'total_lost': total_lost, 
        }

        paginated_response = paginator.get_paginated_response(team_leaders_serializer.data)
        
        final_data = {
            "counts": counts_data,
            "count": paginated_response.data['count'],
            "next": paginated_response.data['next'],
            "previous": paginated_response.data['previous'],
            "results": paginated_response.data['results']
        }
        
        return Response(final_data, status=status.HTTP_200_OK)
        



# API: SUPERUSER-ONLY - STAFF REPORT DASHBOARD 

class SuperUserStaffReportAPIView(APIView):
    """
    API endpoint exclusively for the Superuser to retrieve a complete list of all staff, aggregated lead counts, and a detailed monthly productivity report for all staff members.
    """
  
    
    permission_classes = [IsAuthenticated, CustomIsSuperuser] 

    def get(self, request, format=None):
        user = request.user
        
        staff_list_qs = Staff.objects.all()
        base_lead_qs = LeadUser.objects.all()
        
        lead_counts = {
            'total_leads': base_lead_qs.filter(status="Leads").count(),
            'total_interested_leads': base_lead_qs.filter(status="Intrested").count(),
            'total_not_interested_leads': base_lead_qs.filter(status="Not Interested").count(),
            'total_other_location_leads': base_lead_qs.filter(status="Other Location").count(),
            'total_not_picked_leads': base_lead_qs.filter(status="Not Picked").count(),
            
            'total_visits_leads': base_lead_qs.filter(status="Visit").count()
        }

        year = int(request.query_params.get('year', datetime.now().year))
        month = int(request.query_params.get('month', datetime.now().month))
        
        days_in_month = monthrange(year, month)[1]
        
        total_salary_all_staff = 0
        productivity_data_all_staff = {} 

        for staff in staff_list_qs:
            salary = float(staff.salary or 0)
            daily_salary = round(salary / days_in_month, 2) if days_in_month > 0 else 0

            leads_data = LeadUser.objects.filter(
                assigned_to=staff,
                updated_date__year=year,
                updated_date__month=month,
                status='Intrested'
            ).values('updated_date__day').annotate(count=Count('id'))

            productivity_data_dict = {day: {'leads': 0, 'salary': 0} for day in range(1, days_in_month + 1)}
            total_salary = 0

            for lead in leads_data:
                day = lead['updated_date__day']
                if day in productivity_data_dict:
                    leads_count = lead['count']
                    productivity_data_dict[day]['leads'] = leads_count

                    if leads_count >= 10:
                        daily_earned_salary = daily_salary
                    else:
                        daily_earned_salary = round((daily_salary / 10) * leads_count, 2)

                    productivity_data_dict[day]['salary'] = daily_earned_salary
                    total_salary += daily_earned_salary

            productivity_data_all_staff[staff.id] = {
                'name': staff.name,
                'productivity_data': productivity_data_dict, 
                'total_salary': round(total_salary, 2)
            }
            total_salary_all_staff += total_salary

        # ---  Calendar Structure ---
        calendar_data = calendar.monthcalendar(year, month)
        weekdays = list(calendar.day_name)
        structured_calendar_data = []
        for week in calendar_data:
            week_data = []
            for i, day in enumerate(week):
                week_data.append({
                    'day': day,
                    'day_name': weekdays[i]
                })
            structured_calendar_data.append(week_data)
        
        # ---  Month List for Dropdown ---
        months_list = [{'id': i, 'name': calendar.month_name[i]} for i in range(1, 13)]

        # ---  Serialize and Respond ---
        staff_list_serializer = ApiStaffSerializer(staff_list_qs, many=True)
        
        total_earning_aggregation = Sell_plot.objects.filter(staff__in=staff_list_qs).aggregate(total_earn=Sum('earn_amount'))
        total_earning = total_earning_aggregation.get('total_earn') or 0
        lead_counts['total_earning'] = total_earning
        
        response_data = {
            'lead_counts': lead_counts,
            'staff_list': staff_list_serializer.data,
            'productivity_report': {
                'total_salary_all_staff': round(total_salary_all_staff, 2),
                'staff_productivity_details': productivity_data_all_staff 
            },
            'calendar_structure': structured_calendar_data,
            'dropdown_data': {
                'months': months_list
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    


class AdminStaffEditAPIView(APIView):
    """
    API endpoint for retrieving and updating a Staff member's profile from the Admin Dashboard.
    Access is restricted solely to the Admin role who manages the Staff member.
    """
    
    permission_classes = [IsAuthenticated, IsCustomAdminUser]
    parser_classes = [MultiPartParser, FormParser] 

    def get_object(self, id):
        
        return get_object_or_404(Staff, id=id)

    def get(self, request, id, format=None):
        """
        GET request: return Staff current details .
        """
        staff = self.get_object(id)
        
        admin_profile = Admin.objects.get(self_user=request.user)
        if staff.team_leader.admin != admin_profile:
             return Response(
                {"error": "You do not have permission to edit this staff member."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = FullStaffSerializer(staff, context={'request': request}) 
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id, format=None):
        """
        PATCH request: update Staff profile.
        """
        staff = self.get_object(id)

        # Security check
        admin_profile = Admin.objects.get(self_user=request.user)
        if staff.team_leader.admin != admin_profile:
             return Response(
                {"error": "You do not have permission to edit this staff member."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = StaffUpdateSerializer(instance=staff, data=request.data, partial=True) 
        
        if serializer.is_valid():
            updated_instance = serializer.save()
            
            read_serializer = StaffProfileSerializer(updated_instance, context={'request': request})
            return Response(read_serializer.data, status=status.HTTP_200_OK) 
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, id, format=None):
       
        return self.patch(request, id, format)
    




# API: ADMIN-ONLY - EDIT TEAM LEADER (GET/UPDATE)

class AdminTeamLeaderEditAPIView(APIView):
    """
    API endpoint for retrieving and updating a Team Leader's profile from the Admin Dashboard.
    Access is restricted solely to the Admin role who manages the Team Leader.
    """
    
    permission_classes = [IsAuthenticated, IsCustomAdminUser]
    parser_classes = [MultiPartParser, FormParser] 
    def get_object(self, id):
        return get_object_or_404(Team_Leader, id=id)

    def get(self, request, id, format=None):
        """
        GET request:return  Team Leader current details .
        """
        team_leader = self.get_object(id)
        
        try:
            admin_profile = Admin.objects.get(self_user=request.user)
        except Admin.DoesNotExist:
            return Response({"error": "Admin profile not found."}, status=status.HTTP_404_NOT_FOUND)
            
        if team_leader.admin != admin_profile:
             return Response(
                {"error": "You do not have permission to edit this Team Leader."},
                status=status.HTTP_403_FORBIDDEN
            )
    

        serializer = ProductivityTeamLeaderSerializer(team_leader) 
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id, format=None):
        """
        PATCH request: update Team Leader profile.
        """
        team_leader = self.get_object(id)

        try:
            admin_profile = Admin.objects.get(self_user=request.user)
        except Admin.DoesNotExist:
            return Response({"error": "Admin profile not found."}, status=status.HTTP_404_NOT_FOUND)
            
        if team_leader.admin != admin_profile:
             return Response(
                {"error": "You do not have permission to edit this Team Leader."},
                status=status.HTTP_403_FORBIDDEN
            )
       
        serializer = TeamLeaderUpdateSerializer(instance=team_leader, data=request.data, partial=True) 
        
        if serializer.is_valid():
            updated_instance = serializer.save()
            
            
            read_serializer = SimpleTeamLeaderSerializer(updated_instance)
            return Response(read_serializer.data, status=status.HTTP_200_OK) 
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, id, format=None):
        
        return self.patch(request, id, format)
    



class AdminStaffIncentiveAPIView(APIView):
    """
    GET: Returns incentive details for a specific staff (month/year filter)
    Accessible only by Admin users.
    """
    permission_classes = [IsAuthenticated, IsCustomAdminUser]

    def get(self, request, staff_id, format=None):
        admin_profile = None

        try:
            staff_instance = get_object_or_404(Staff, id=staff_id)

            # Try to get admin profile
            try:
                admin_profile = Admin.objects.get(self_user=request.user)
            except Admin.DoesNotExist:
                try:
                    admin_profile = Admin.objects.get(email=request.user.email or request.user.username)
                except Admin.DoesNotExist:
                    return Response(
                        {"error": "Admin profile not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

        except Exception as e:
            return Response(
                {"error": f"Staff with ID {staff_id} not found or invalid access."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Security Check
        if not staff_instance.team_leader or staff_instance.team_leader.admin != admin_profile:
            return Response(
                {"error": "You do not have permission to view this staff member's incentives."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Filters
        year = int(request.query_params.get("year", datetime.now().year))
        month = int(request.query_params.get("month", datetime.now().month))
        months_list = [(i, calendar.month_name[i]) for i in range(1, 13)]

        # Staff type safely
        user_type = False
        if hasattr(staff_instance, 'user') and staff_instance.user:
            user_type = staff_instance.user.is_freelancer

        # Slab and sales
        slab = Slab.objects.all()
        sell_property = Sell_plot.objects.filter(
            staff=staff_instance,
            updated_date__year=year,
            updated_date__month=month,
        ).order_by("-created_date")

        total_earn = sell_property.aggregate(total_earn=Sum("earn_amount"))["total_earn"] or 0

        context = {
            "slab": SlabSerializer(slab, many=True).data,
            "sell_property": SellPlotSerializer(sell_property, many=True).data,
            "total_earn": total_earn,
            "year": year,
            "month": month,
            "months_list": months_list,
            "user_type": user_type,
        }
        return Response(context, status=status.HTTP_200_OK)



class AdminStaffProductivityCalendarAPIView(APIView):
    """
    API endpoint: 'staff_productivity_calendar_view' (Admin Dashboard)
    GET: Returns a specific staff's daily earnings calendar.
    Access: Only Admins
    """

    permission_classes = [IsAuthenticated, IsCustomAdminUser]

    def get_staff_object(self, staff_id):
        return get_object_or_404(Staff, id=staff_id)

    def get(self, request, staff_id, format=None):
        admin_profile = None  
        staff_instance = None

        try:
            staff_instance = self.get_staff_object(staff_id)
        except Exception:
            return Response(
                {"error": f"Staff with ID {staff_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Try resolving admin via both fields
        try:
            admin_profile = Admin.objects.get(self_user=request.user)
        except Admin.DoesNotExist:
            try:
                admin_profile = Admin.objects.get(email=request.user.username)
            except Admin.DoesNotExist:
                return Response(
                    {"error": "Admin profile not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        if not admin_profile:
            return Response(
                {"error": "Could not resolve admin profile."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not hasattr(staff_instance, "team_leader") or not staff_instance.team_leader:
            return Response(
                {"error": "This staff member is not assigned to any Team Leader."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if staff_instance.team_leader.admin != admin_profile:
            return Response(
                {"error": "You do not have permission to view this staff's calendar."},
                status=status.HTTP_403_FORBIDDEN,
            )

        months_list = [(i, calendar.month_name[i]) for i in range(1, 13)]
        year = int(request.query_params.get("year", datetime.now().year))
        month = int(request.query_params.get("month", datetime.now().month))

        days_in_month = monthrange(year, month)[1]
        salary_arg = staff_instance.salary or 0
        daily_salary = round(float(salary_arg) / int(days_in_month)) if days_in_month > 0 else 0

        leads_data = (
            LeadUser.objects.filter(
                assigned_to=staff_instance,
                updated_date__year=year,
                updated_date__month=month,
                status="Intrested",
            )
            .values("updated_date__day")
            .annotate(count=Count("id"))
        )

        productivity_data = {day: {"leads": 0, "salary": 0} for day in range(1, days_in_month + 1)}
        total_salary = 0

        for lead in leads_data:
            day = lead["updated_date__day"]
            leads_count = lead["count"]
            productivity_data[day]["leads"] = leads_count

            if leads_count >= 10:
                daily_earned_salary = daily_salary
            else:
                daily_earned_salary = round((daily_salary / 10) * leads_count, 2)

            productivity_data[day]["salary"] = daily_earned_salary
            total_salary += daily_earned_salary

        weekdays = list(calendar.day_name)
        productivity_list = []

        for day in range(1, days_in_month + 1):
            date_obj = datetime(year, month, day).date()
            data = productivity_data.get(day, {"leads": 0, "salary": 0})
            productivity_list.append({
                "day": day,
                "date": date_obj,
                "day_name": weekdays[date_obj.weekday()],
                "leads": data["leads"],
                "salary": data["salary"],
            })

        response_data = {
            "staff": StaffProfileSerializer(staff_instance).data,
            "year": year,
            "month": month,
            "monthly_salary": salary_arg,
            "total_salary": round(total_salary, 2),
            "months_list": months_list,
            "daily_productivity_data": DailyProductivitySerializer(productivity_list, many=True).data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
 
    


# API: ADMIN-ONLY - STAFF PARTICULAR LEADS (BY TAG)
class AdminStaffParticularLeadsAPIView(APIView):
    """
    API endpoint to fetch all leads of a specific staff member (ID) filtered by status (tag).
    Access is strictly limited to the Admin user who manages the Staff member.
    """
    
    permission_classes = [IsAuthenticated, IsCustomAdminUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, id, tag, format=None):
        paginator = self.pagination_class()
        admin_profile = None  # Prevent UnboundLocalError
        staff_instance = None

        try:
            staff_instance = get_object_or_404(Staff, id=id)
        except Exception:
            return Response(
                {"error": f"Staff with ID {id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            admin_profile = Admin.objects.get(self_user=request.user)
        except Admin.DoesNotExist:
            try:
                admin_profile = Admin.objects.get(email=request.user.username)
            except Admin.DoesNotExist:
                return Response(
                    {"error": "Admin profile not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        if not admin_profile:
            return Response(
                {"error": "Could not determine admin profile."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not hasattr(staff_instance, "team_leader") or not staff_instance.team_leader:
            return Response(
                {"error": "This staff member is not assigned to any Team Leader."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if staff_instance.team_leader.admin != admin_profile:
            return Response(
                {"error": "You do not have permission to view this staff's leads."},
                status=status.HTTP_403_FORBIDDEN,
            )

        valid_status = [
            "Intrested",
            "Not Interested",
            "Other Location",
            "Lost",
            "Visit",
        ]

        if tag in valid_status:
            staff_leads = LeadUser.objects.filter(
                assigned_to=staff_instance, status=tag
            )
        else:
            staff_leads = LeadUser.objects.filter(assigned_to=staff_instance)

        staff_leads = staff_leads.order_by("-updated_date")
        page = paginator.paginate_queryset(staff_leads, request, view=self)

        serializer = ApiLeadUserSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        response.data["staff_id"] = id
        response.data["tag"] = tag
        response.data["count"] = staff_leads.count()

        return response






class SuperUserUnassignedLeadsAPIView(APIView):
    """
    API for Superuser's 'Leads' page (def lead function).
    Provides a paginated list of all unassigned leads (Team_LeadData).
    """
    permission_classes = [IsAuthenticated, CustomIsSuperuser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, format=None):
        paginator = self.pagination_class()
        
        unassigned_leads_qs = Team_LeadData.objects.filter(
            assigned_to=None, 
            status='Leads'
        ).order_by('-created_date')
        
        page = paginator.paginate_queryset(unassigned_leads_qs, request, view=self)
        
        if page is not None:
            serializer = ApiTeamLeadDataSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ApiTeamLeadDataSerializer(unassigned_leads_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    





# API: SUPERUSER-ONLY - EDIT PROJECT (GET/UPDATE)
class ProjectEditAPIView(APIView):
    """
    API endpoint for retrieving and updating a specific Project record.
    Access is strictly limited to the Superuser role.
    """
    
    permission_classes = [IsAuthenticated, CustomIsSuperuser]
    parser_classes = [MultiPartParser, FormParser] 

    def get_object(self, id):
        
        return get_object_or_404(Project, id=id)

    def get(self, request, id, format=None):
        """
        GET request:return  Project current details.
        """
        project = self.get_object(id)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id, format=None):
        """
        PATCH request: update Project details .
        """
        project = self.get_object(id)
        
        serializer = ProjectSerializer(instance=project, data=request.data, partial=True) 
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK) 
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, id, format=None):
        # POST ko bhi PATCH ki tarah handle karo
        return self.patch(request, id, format)
    






class SuperUserFreelancerLeadsAPIView(APIView):
    """
    API endpoint exclusively for the Superuser to retrieve a list of leads assigned ONLY to Freelancers (Associates), filtered by status tag.
    """
    permission_classes = [IsAuthenticated, CustomIsSuperuser]
    pagination_class = StandardResultsSetPagination 

    def get(self, request, tag, format=None):
        paginator = self.pagination_class()
        
        base_queryset = LeadUser.objects.filter(assigned_to__user__is_freelancer=True)
        queryset = LeadUser.objects.none() 

        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        status_map = {
            'total_lead': 'Leads',
            'visits': 'Visit',
            'interested': 'Intrested',
            'not_interested': 'Not Interested',
            'other_location': 'Other Location',
            'not_picked': 'Not Picked',
            'lost': 'Lost',
            'pending_followups': 'pending', 
            'today_followups': 'today',
            'tomorrow_followups': 'tomorrow'
        }

        if tag not in status_map:
            return Response(
                {"error": f"Invalid tag: {tag}. Valid tags are: {list(status_map.keys())}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        status = status_map[tag]

        if status == 'pending':
            queryset = base_queryset.filter(Q(status='Intrested') & Q(follow_up_date__isnull=False))
        elif status == 'today':
            queryset = base_queryset.filter(Q(status='Intrested') & Q(follow_up_date=today))
        elif status == 'tomorrow':
            queryset = base_queryset.filter(Q(status='Intrested') & Q(follow_up_date=tomorrow))
        else:
            queryset = base_queryset.filter(status=status)

        queryset = queryset.order_by('-updated_date')
        
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = ApiLeadUserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ApiLeadUserSerializer(queryset, many=True)
        return Response(serializer.data)
    




class SuperUserTeamLeaderLeadsAPIView(APIView):
    """
    API endpoint for Superusers to retrieve detailed reports on both Lead status and Staff metrics (Total, Active, Salary).
    The response structure (Leads List vs Staff List) depends entirely on the 'tag' parameter.
    """
    permission_classes = [IsAuthenticated, CustomIsSuperuser]
    pagination_class = StandardResultsSetPagination

    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    @staticmethod
    def _summary():
        total_staff = User.objects.filter(
            Q(is_admin=True) | Q(is_staff_new=True) | Q(is_team_leader=True)
        ).count()

        active_staff = User.objects.filter(
            is_staff_new=True,
            logout_time__isnull=True
        ).count()

        total_earning = 0  
        return {
            "total_staff": total_staff,
            "active_staff": active_staff,
            "total_earning": total_earning,
        }

    def get(self, request, tag, format=None):
        paginator = self.pagination_class()

        staff_leads_qs = LeadUser.objects.none()
        staff_qs = Staff.objects.none()

        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        lead_tags = [
            "total_leads","total_visit","interested","not_interested",
            "other_location","not_picked","lost",
            "pending_followups","today_followups","tomorrow_followups"
        ]

        staff_tags = ["staff_total", "staff_active", "staff_salary"]

        if tag in lead_tags:

            if tag == "total_leads":
                staff_leads_qs = LeadUser.objects.filter(status="Leads")

            elif tag == "total_visit":
                staff_leads_qs = LeadUser.objects.filter(status="Visit")

            elif tag == "interested":
                staff_leads_qs = LeadUser.objects.filter(status="Intrested")

            elif tag == "not_interested":
                staff_leads_qs = LeadUser.objects.filter(status="Not Interested")

            elif tag == "other_location":
                staff_leads_qs = LeadUser.objects.filter(status="Other Location")

            elif tag == "not_picked":
                staff_leads_qs = LeadUser.objects.filter(status="Not Picked")

            elif tag == "lost":
                staff_leads_qs = LeadUser.objects.filter(status="Lost")

            elif tag == "pending_followups":
                staff_leads_qs = LeadUser.objects.filter(
                    status="Intrested",
                    follow_up_date__isnull=False
                )

            elif tag == "today_followups":
                staff_leads_qs = LeadUser.objects.filter(
                    status="Intrested",
                    follow_up_date=today
                )

            elif tag == "tomorrow_followups":
                staff_leads_qs = LeadUser.objects.filter(
                    status="Intrested",
                    follow_up_date=tomorrow
                )

            # Serialize
            ordered_qs = staff_leads_qs.order_by("-updated_date")
            serializer = ApiLeadUserSerializer(ordered_qs, many=True)
            page = paginator.paginate_queryset(serializer.data, request, view=self)

            if page is not None:
                return paginator.get_paginated_response(page)

            return Response({"results": serializer.data})

        elif tag in staff_tags:

            # STAFF TOTAL
            if tag == "staff_total":
                total_staff = Staff.objects.count()
                staff_qs = Staff.objects.all().order_by("-updated_date")
                summary = {"total_staff": total_staff}

            # STAFF ACTIVE
            elif tag == "staff_active":
                active_staff = Staff.objects.filter(
                    user__logout_time__isnull=True
                ).count()
                staff_qs = Staff.objects.filter(
                    user__logout_time__isnull=True
                ).order_by("-updated_date")
                summary = {"active_staff": active_staff}

            # STAFF SALARY / TOTAL EARNING
            elif tag == "staff_salary":
                total_earning = Staff.objects.annotate(
                    salary_int=Cast("salary", IntegerField())
                ).aggregate(total=Sum("salary_int"))["total"] or 0

                staff_qs = Staff.objects.exclude(
                    salary__isnull=True
                ).exclude(
                    salary=""
                ).order_by("-updated_date")

                summary = {"total_earning": total_earning}

            # Serialize staff
            serializer = ApiStaffSerializer(staff_qs, many=True)
            page = paginator.paginate_queryset(serializer.data, request, view=self)

            if page is not None:
                paginated = paginator.get_paginated_response(page)
                paginated.data.update(summary)
                return paginated

            return Response({"results": serializer.data, **summary})

        else:
            return Response(
                {
                    "error": f"Invalid tag: {tag}. Valid tags: {lead_tags + staff_tags}"
                },
                status=400
            )
        # return Response(staff_serializer.data, status=status.HTTP_200_OK)
    



# API: STAFF-ONLY - LEADS DASHBOARD (CARDS + LIST) 

class StaffDashboardAPIView(APIView):
    """
    Staff-only Leads Dashboard (cards + paginated list).
    Filters both leads list and card counts by provided start_date/end_date.
    Accepts dates in 'YYYY-MM-DD' or 'DD-MM-YYYY'.
    """
    permission_classes = [IsAuthenticated, IsCustomStaffUser]
    pagination_class = StandardResultsSetPagination

    def _parse_date_safe(self, s):
        if not s:
            return None
        s = s.strip()
        for fmt in ('%Y-%m-%d', '%d-%m-%Y'):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return None

    def get(self, request, format=None):
        paginator = self.pagination_class()

        try:
            staff = Staff.objects.get(email=request.user.email)
        except Staff.DoesNotExist:
            return Response({"error": "Staff profile not found."}, status=status.HTTP_404_NOT_FOUND)

        raw_params = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in request.query_params.items()}
        start_date_str = raw_params.get('start_date')
        end_date_str = raw_params.get('end_date')

        parsed_start = self._parse_date_safe(start_date_str)
        parsed_end = self._parse_date_safe(end_date_str)

        tz = timezone.get_current_timezone()
        today = timezone.localdate()

        if parsed_start and parsed_end:
            start_dt = timezone.make_aware(datetime.combine(parsed_start, datetime.min.time()), tz)
            
            end_dt = timezone.make_aware(datetime.combine(parsed_end, datetime.max.time()), tz)
        else:
            start_date = today - timedelta(days=6)  # last 7 days including today
            start_dt = timezone.make_aware(datetime.combine(start_date, datetime.min.time()), tz)
            end_dt = timezone.make_aware(datetime.combine(today, datetime.max.time()), tz)
        
        date_q = Q(updated_date__range=(start_dt, end_dt)) | Q(created_date__range=(start_dt, end_dt))

       
        leads_qs = LeadUser.objects.filter(status="Leads", assigned_to=staff).filter(date_q).select_related('project')

        # Paginate leads
        page = paginator.paginate_queryset(leads_qs, request, view=self)
        leads_serializer = ApiLeadUserSerializer(page, many=True)

        interested_count = LeadUser.objects.filter(status="Intrested", assigned_to=staff).filter(date_q).count()
        not_interested_count = LeadUser.objects.filter(status="Not Interested", assigned_to=staff).filter(date_q).count()
        other_location_count = LeadUser.objects.filter(status="Other Location", assigned_to=staff).filter(date_q).count()
        not_picked_count = LeadUser.objects.filter(status="Not Picked", assigned_to=staff).filter(date_q).count()
        visits_count = LeadUser.objects.filter(status="Visit", assigned_to=staff).filter(date_q).count()
        total_leads_count = leads_qs.count()

        counts_data = {
            'total_leads': total_leads_count,
            'total_interested_leads': interested_count,
            'total_not_interested_leads': not_interested_count,
            'total_other_location_leads': other_location_count,
            'total_not_picked_leads': not_picked_count,
            'total_visits_leads': visits_count,
        }

        whatsapp_marketing = Marketing.objects.filter(source="whatsapp", user=request.user).last()
        projects = Project.objects.all()
        setting = Settings.objects.filter().last()

        paginated_response = paginator.get_paginated_response(leads_serializer.data)
        results = paginated_response.data.get('results', [])

        staff_ids = [r.get('assigned_to', {}).get('id') for r in results if r.get('assigned_to')]
        staff_ids = list(set([sid for sid in staff_ids if sid]))

        projects_qs = Project.objects.filter(staff__id__in=staff_ids).order_by('-updated_date')
        projects_by_staff = {}
        for p in projects_qs:
            if getattr(p, 'staff', None) and getattr(p.staff, 'id', None):
                sid = p.staff.id
                projects_by_staff.setdefault(sid, []).append(p)

        for idx, lead in enumerate(results):
            assigned = lead.get('assigned_to')
            if assigned and assigned.get('id'):
                sid = assigned.get('id')
                proj_list = projects_by_staff.get(sid, [])
                results[idx]['projects'] = ProjectSerializer(proj_list, many=True).data
            else:
                results[idx]['projects'] = []

        final_data = {
            "counts": counts_data,
            "whatsapp_marketing": MarketingSerializer(whatsapp_marketing).data if whatsapp_marketing else None,
            "projects": ProjectSerializer(projects, many=True).data,
            "setting": DashboardSettingsSerializer(setting).data if setting else None,
            "count": paginated_response.data.get('count'),
            "next": paginated_response.data.get('next'),
            "previous": paginated_response.data.get('previous'),
            "results": results
        }

        return Response(final_data, status=status.HTTP_200_OK)



class StaffAddSelfLeadAPIView(APIView):
    """
    API endpoint for Staff members to manually add a new lead into the system.
    The created lead is automatically assigned to the Staff member creating it.
    """
   
    
    permission_classes = [IsAuthenticated, IsCustomStaffUser]
   
    parser_classes = [MultiPartParser, FormParser] 

    def post(self, request, format=None):
        """
        create new lead.
        """
        serializer = StaffLeadCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            lead = serializer.save()
            
            response_serializer = ApiLeadUserSerializer(lead)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





# API: STAFF-ONLY - UPDATE LEAD (CHANGE STATUS)

class StaffUpdateLeadAPIView(APIView):
    """
    API endpoint for Staff to update lead status, message, and follow-up.
    This is a new, separate API only for Staff (is_staff_new=True).
    """
    permission_classes = [IsAuthenticated, IsCustomStaffUser]

    def post(self, request, id, format=None):
        try:
            staff_profile = Staff.objects.get(email=request.user.email)
        except Staff.DoesNotExist:
            return Response(
                {"error": "Staff profile not found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            lead_object = get_object_or_404(LeadUser, id=id)
        except Exception:
            return Response({"error": f"Lead with id={id} not found."}, 
                            status=status.HTTP_404_NOT_FOUND)

        if lead_object.assigned_to != staff_profile:
            return Response(
                {"error": "You do not have permission to update this lead."},
                status=status.HTTP_403_FORBIDDEN
            )

        current_status = lead_object.status

        serializer = LeadUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        new_status = validated_data.get('status')
        message = validated_data.get('message', lead_object.message)
        follow_date = validated_data.get('followDate')
        follow_time = validated_data.get('followTime')

        if new_status == "Not Picked":
            try:
                Team_LeadData.objects.create(
                    user=lead_object.user,
                    name=lead_object.name,
                    call=lead_object.call,
                    status="Leads", 
                    email=lead_object.email,
                    team_leader=staff_profile.team_leader
                )
                lead_object.delete()
                return Response({'message': 'Success: Lead moved back to Team Leader pool.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': f'Failed to move lead: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        lead_object.status = new_status
        lead_object.message = message
        if follow_date:
            lead_object.follow_up_date = follow_date
        if follow_time:
            lead_object.follow_up_time = follow_time
            
        lead_object.save()

        try:
            Leads_history.objects.create(
                leads=lead_object,
                lead_id=id, 
                status=new_status,
                name=lead_object.name,
                message=message,
            )
        except Exception as e:
            print(f"Failed to create Leads_history: {e}")

        user_type = get_user_type(request.user)
        tagline = f"Lead status changed from {current_status} to {new_status} by user[Email: {request.user.email}, {user_type}]"
        tag2 = new_status
        ip = get_client_ip(request)

        ActivityLog.objects.create(
            staff=staff_profile,
            team_leader=staff_profile.team_leader,
            description=tagline,
            ip_address=ip,
            email=request.user.email,
            user_type=user_type,
            activity_type=tag2,
            name=request.user.name,
        )
            
        response_serializer = ApiLeadUserSerializer(lead_object)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    

class UpdateLeadProjectAPIView(APIView):
    """
    API endpoint for Staff members to update the specific project linked to an assigned lead.
    """
    permission_classes = [IsAuthenticated, IsCustomStaffUser]

    def post(self, request, format=None):
        lead_id = request.data.get('lead_id')
        project_id = request.data.get('project_id')

        if not lead_id or project_id is None:
            return Response({"error": "lead_id aur project_id dono zaroori hain."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            staff = Staff.objects.get(email=request.user.email)
        except Staff.DoesNotExist:
            return Response({"error": "Staff profile not found."}, status=status.HTTP_404_NOT_FOUND)

        lead = get_object_or_404(LeadUser, id=lead_id)
        if lead.assigned_to != staff:
            return Response({"error": "Aap is lead ko edit nahi kar sakte (Not assigned to you)."}, status=status.HTTP_403_FORBIDDEN)

        project = get_object_or_404(Project, id=project_id)
        lead.project = project
        lead.save()

        serializer = ApiLeadUserSerializer(lead)
        return Response(serializer.data, status=status.HTTP_200_OK)



# API: STAFF-ONLY - INTERESTED LEADS (BY TAG) 

class StaffInterestedLeadsAPIView(APIView):
    """
    API endpoint for 'lost_leads' function (Staff Dashboard).
    GET: Fetches a Staff's "Interested" leads, filtered by a tag 
         (e.g., pending_follow, today_follow, tommorrow_follow).
    ONLY STAFF (is_staff_new=True) can access this.
    """
    
    permission_classes = [IsAuthenticated, IsCustomStaffUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, tag, format=None):
        paginator = self.pagination_class()
        user = request.user
        
        # Get the Staff profile
        try:
            staff = Staff.objects.get(email=user.email)
        except Staff.DoesNotExist:
            return Response({"error": "Staff profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get dates for filtering
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        # Base queryset: Only interested leads for this staff
        base_queryset = LeadUser.objects.filter(assigned_to=staff, status='Intrested')
        
        queryset = LeadUser.objects.none() 
        
        if tag == 'pending_follow':
            queryset = base_queryset.filter(follow_up_date__isnull=False)
        
        elif tag == 'today_follow':
            queryset = base_queryset.filter(follow_up_date=today)
        
        elif tag == 'tomorrow_follow': 
            queryset = base_queryset.filter(follow_up_date=tomorrow)
        
        elif tag == 'interested': # Default 'Interested' tag
             queryset = base_queryset.filter(follow_up_time__isnull=True)
             
        else:
            valid_tags = ['pending_follow', 'today_follow', 'tomorrow_follow', 'interested']
            return Response(
                {"error": f"Invalid tag for this view: {tag}. Valid tags are: {valid_tags}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Order and Paginate
        queryset = queryset.order_by('-updated_date')
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        if page is not None:
            serializer = ApiLeadUserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Fallback if pagination fails
        serializer = ApiLeadUserSerializer(queryset, many=True)
        return Response(serializer.data)
    

# API: STAFF-ONLY - NOT INTERESTED LEADS

class StaffNotInterestedLeadsAPIView(APIView):
    """
    API endpoint for 'customer' function (Staff Dashboard).
    GET: Fetches all of a Staff's "Not Interested" leads.
    ONLY STAFF (is_staff_new=True) can access this.
    """
    
    permission_classes = [IsAuthenticated, IsCustomStaffUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, format=None):
        paginator = self.pagination_class()
        user = request.user
        
        # Get the Staff profile
        try:
            staff = Staff.objects.get(email=user.email)
        except Staff.DoesNotExist:
            return Response({"error": "Staff profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get "Not Interested" leads for this staff
        # (This is the 'else' block logic from your 'customer' function)
        leads_qs = LeadUser.objects.filter(
            status="Not Interested", 
            assigned_to=staff
        ).order_by("-updated_date")

        # Paginate and Serialize
        page = paginator.paginate_queryset(leads_qs, request, view=self)
        
        if page is not None:
            serializer = ApiLeadUserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Fallback if pagination fails
        serializer = ApiLeadUserSerializer(leads_qs, many=True)
        return Response(serializer.data)
    




# API: STAFF-ONLY - GET LEAD HISTORY

class StaffLeadHistoryAPIView(APIView):
    """
    API endpoint for 'LeadHistory' function (Staff Dashboard).
    GET: Fetches the status update history for a single lead (id).
    ONLY STAFF (is_staff_new=True) can access this, and only for their own leads.
    """
    
    permission_classes = [IsAuthenticated, IsCustomStaffUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, id, format=None):
        paginator = self.pagination_class()
        user = request.user
        
        # Get the Staff profile
        try:
            staff = Staff.objects.get(email=user.email)
        except Staff.DoesNotExist:
            return Response({"error": "Staff profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get the Lead and verify it belongs to this Staff
        try:
            lead = get_object_or_404(LeadUser, id=id)
            if lead.assigned_to != staff:
                return Response(
                    {"error": "You do not have permission to view this lead's history."},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Exception:
            return Response({"error": "Lead not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get Lead History (using 'lead_id' from views.py logic)
        # Note: Your view uses lead_id=id, which might mean the LeadUser ID
        history_qs = Leads_history.objects.filter(lead_id=id).order_by('-updated_date')

        # 4. Paginate and Serialize
        page = paginator.paginate_queryset(history_qs, request, view=self)
        
        if page is not None:
            serializer = LeadsHistorySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = LeadsHistorySerializer(history_qs, many=True)
        return Response(serializer.data)
    



# API: STAFF-ONLY - OTHER LOCATION LEADS

class StaffOtherLocationLeadsAPIView(APIView):
    """
    API endpoint for 'maybe' function (Staff Dashboard).
    GET: Fetches all of a Staff's "Other Location" leads.
    ONLY STAFF (is_staff_new=True) can access this.
    """
    
    permission_classes = [IsAuthenticated, IsCustomStaffUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, format=None):
        paginator = self.pagination_class()
        user = request.user
        
        # Get the Staff profile
        try:
            staff = Staff.objects.get(email=user.email)
        except Staff.DoesNotExist:
            return Response({"error": "Staff profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get "Other Location" leads for this staff
        # (This is the 'else' block logic from your 'maybe' function)
        leads_qs = LeadUser.objects.filter(
            status="Other Location", 
            assigned_to=staff
        ).order_by("-updated_date")

        # Paginate and Serialize
        page = paginator.paginate_queryset(leads_qs, request, view=self)
        
        if page is not None:
            serializer = ApiLeadUserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Fallback if pagination fails
        serializer = ApiLeadUserSerializer(leads_qs, many=True)
        return Response(serializer.data)
    


class StaffNotPickedLeadsAPIView(APIView):
    """
    API endpoint for 'not_picked' function (Staff Dashboard).
    GET: Fetches all of a Staff's "Not Picked" leads.
    ONLY STAFF (is_staff_new=True) can access this.
    """
    
    permission_classes = [IsAuthenticated, IsCustomStaffUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, format=None):
        paginator = self.pagination_class()
        user = request.user
        
        # Get the Staff profile
        try:
            staff = Staff.objects.get(email=user.email)
        except Staff.DoesNotExist:
            return Response({"error": "Staff profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get "Not Picked" leads for this staff
        # (This is the 'else' block logic from your 'not_picked' function)
        leads_qs = LeadUser.objects.filter(
            status="Not Picked", 
            assigned_to=staff
        ).order_by("-updated_date")

        #Paginate and Serialize
        page = paginator.paginate_queryset(leads_qs, request, view=self)
        
        if page is not None:
            serializer = ApiLeadUserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Fallback if pagination fails
        serializer = ApiLeadUserSerializer(leads_qs, many=True)
        return Response(serializer.data)



# API: STAFF-ONLY - LOST LEADS

class StaffLostLeadsAPIView(APIView):
    """
    API endpoint for 'lost' function (Staff Dashboard).
    GET: Fetches all of a Staff's "Lost" leads.
    ONLY STAFF (is_staff_new=True) can access this.
    """
    
    permission_classes = [IsAuthenticated, IsCustomStaffUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, format=None):
        paginator = self.pagination_class()
        user = request.user
        
        # Get the Staff profile
        try:
            staff = Staff.objects.get(email=user.email)
        except Staff.DoesNotExist:
            return Response({"error": "Staff profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get "Lost" leads for this staff
        # (This is the 'else' block logic from your 'lost' function)
        leads_qs = LeadUser.objects.filter(
            status="Lost", 
            assigned_to=staff
        ).order_by("-updated_date")

        # Paginate and Serialize
        page = paginator.paginate_queryset(leads_qs, request, view=self)
        
        if page is not None:
            serializer = ApiLeadUserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Fallback if pagination fails
        serializer = ApiLeadUserSerializer(leads_qs, many=True)
        return Response(serializer.data)
    


# API: STAFF-ONLY - VISIT LEADS

class StaffVisitLeadsAPIView(APIView):
    """
    API endpoint for 'visit_lead_staff_side' function (Staff Dashboard).
    GET: Fetches all of a Staff's "Visit" leads.
    ONLY STAFF (is_staff_new=True) can access this.
    """
    
    permission_classes = [IsAuthenticated, IsCustomStaffUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, format=None):
        paginator = self.pagination_class()
        user = request.user
        
        # Get the Staff profile
        try:
            staff = Staff.objects.get(email=user.email)
        except Staff.DoesNotExist:
            return Response({"error": "Staff profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get "Visit" leads for this staff
        # (This is the logic from your 'visit_lead_staff_side' function)
        leads_qs = LeadUser.objects.filter(
            status="Visit", 
            assigned_to=staff
        ).order_by("-updated_date")

        # Paginate and Serialize
        page = paginator.paginate_queryset(leads_qs, request, view=self)
        
        if page is not None:
            serializer = ApiLeadUserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Fallback if pagination fails
        serializer = ApiLeadUserSerializer(leads_qs, many=True)
        return Response(serializer.data)



# API: STAFF-ONLY - ACTIVITY LOGS (TIME SHEET)

class StaffActivityLogAPIView(APIView):
    """
    API endpoint for 'activitylogs' function (Staff Dashboard "Time Sheet").
    GET: Fetches all of a Staff's activity logs (paginated).
    ONLY STAFF (is_staff_new=True) can access this.
    """
    
    permission_classes = [IsAuthenticated, IsCustomStaffUser]
    pagination_class = ActivityLogPagination

    def get(self, request, format=None):
        paginator = self.pagination_class()
        user = request.user
        
        # Get the Staff profile
        try:
            staff_instance = Staff.objects.get(email=user.email)
        except Staff.DoesNotExist:
            # Fallback agar staff profile nahi bana hai, toh sirf user se filter karo
            staff_instance = None

        # Get Logs (Aapke 'activitylogs' function ka Staff logic)
        if staff_instance:
            logs_qs = ActivityLog.objects.filter(
                Q(user=user) | Q(staff=staff_instance)
            ).order_by('-created_date')
        else:
            logs_qs = ActivityLog.objects.filter(user=user).order_by('-created_date')

        # Paginate and Serialize
        page = paginator.paginate_queryset(logs_qs, request, view=self)
        
        if page is not None:
            serializer = ActivityLogSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Fallback if pagination fails
        serializer = ActivityLogSerializer(logs_qs, many=True)
        return Response(serializer.data)  




# API: STAFF-ONLY - PRODUCTIVITY CALENDAR (EARN) 

class StaffProductivityCalendarAPIView(APIView):
    """
    API endpoint for 'staff_productivity_calendar_view' function (Staff Dashboard).
    GET: Fetches a Staff's productivity (Leads + Earned Salary) for a given month/year.
    ONLY STAFF (is_staff_new=True) can access this.
    """
    
    permission_classes = [IsAuthenticated, IsCustomStaffUser]

    def get(self, request, staff_id, format=None):
        

        try:
            requested_user_id = int(staff_id)
        except ValueError:
            return Response({"error": "Invalid User ID format in URL."}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.id != requested_user_id:
            return Response(
                {"error": "You can only view your own calendar."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            staff = Staff.objects.get(user__id=requested_user_id) 
        except Staff.DoesNotExist:
            return Response({"error": "Staff profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get Filters
        months_list = [(i, calendar.month_name[i]) for i in range(1, 13)]
        year = int(request.query_params.get('year', datetime.now().year))
        month = int(request.query_params.get('month', datetime.now().month))

        # Daily Salary Calculation Logic
        days_in_month = monthrange(year, month)[1]
        salary_arg = staff.salary or 0
        
        try:
            salary_float = float(salary_arg)
        except ValueError:
            salary_float = 0.0
            
        daily_salary = round(salary_float / days_in_month) if days_in_month > 0 else 0

        leads_data = LeadUser.objects.filter(
            assigned_to=staff,
            updated_date__year=year,
            updated_date__month=month,
            status='Intrested'
        ).values('updated_date__day').annotate(count=Count('id'))

        productivity_data = {day: {'leads': 0, 'salary': 0} for day in range(1, days_in_month + 1)}
        total_salary = 0 # This is the total EARNED salary

        for lead in leads_data:
            day = lead['updated_date__day']
            leads_count = lead['count']
            productivity_data[day]['leads'] = leads_count

            if leads_count >= 10:
                daily_earned_salary = daily_salary
            else:
                daily_earned_salary = round((daily_salary / 10) * leads_count, 2)

            productivity_data[day]['salary'] = daily_earned_salary
            total_salary += daily_earned_salary

        # Structure Data for Calendar
        weekdays = list(calendar.day_name)
        productivity_list = []
        for day in range(1, days_in_month + 1):
            date_obj = datetime(year, month, day).date()
            day_data = productivity_data.get(day, {'leads': 0, 'salary': 0})
            
            productivity_list.append({
                'day': day,
                'date': date_obj,
                'day_name': weekdays[date_obj.weekday()],
                'leads': day_data['leads'],
                'salary': day_data['salary']
            })

        # Serialize and Respond
        response_data = {
            'staff_details': StaffProfileSerializer(staff).data,
            'year': year,
            'month': month,
            'monthly_salary': salary_arg, 
            'earn_salary': round(total_salary, 2), 
            'months_list': months_list,
            'daily_productivity_data': DailyProductivitySerializer(productivity_list, many=True).data,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    


# API: STAFF-ONLY - INCENTIVE DETAILS 
class StaffIncentiveAPIView(APIView):
    """
    API endpoint for 'incentive_slap_staff' function (Staff Dashboard).
    GET: Fetches the logged-in Staff's incentive details (Month/Year filter).
    """
    
    permission_classes = [IsAuthenticated, IsCustomStaffUser]

    def get(self, request, format=None):
        user = request.user
        
        # Get Staff Profile (from token)
        try:
            staff_instance = Staff.objects.get(email=user.email)
        except Staff.DoesNotExist:
            return Response({"error": "Staff profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get Filters
        months_list = [(i, calendar.month_name[i]) for i in range(1, 13)]
        year = int(request.query_params.get('year', datetime.now().year))
        month = int(request.query_params.get('month', datetime.now().month))

        # Get User Type
        user_type = user.is_freelancer # This is True if Freelancer, False if Staff

        # Get Slab Data
        slab_qs = Slab.objects.all()
        
        slab_data = SlabSerializer(slab_qs, many=True).data
        
        if not user_type:
            for slab_item in slab_data:
                try:
                    original_amount = int(slab_item.get('amount', 0))
                    slab_item['amount'] = str(original_amount - 100) 
                except (ValueError, TypeError, AttributeError):
                    pass 

        sell_property_qs = Sell_plot.objects.filter(
            staff__email=user.email, 
            updated_date__year=year,
            updated_date__month=month
        ).order_by('-created_date')

        total_earn_amount = sell_property_qs.aggregate(total_earn=Sum('earn_amount'))
        total_earn = total_earn_amount.get('total_earn') or 0

        # Serialize and Respond
        context = {
            'slab': slab_data, 
            'sell_property': SellPlotSerializer(sell_property_qs, many=True).data,
            'total_earn': total_earn,
            'year': year,
            'month': month,
            'months_list': months_list,
            'user_type': user_type,
        }
        return Response(context, status=status.HTTP_200_OK)
    



# API: STAFF-ONLY - VIEW/UPDATE PROFILE

class StaffProfileViewAPIView(APIView):
    """
    API endpoint for 'staff_view_profile' function (Staff Dashboard).
    GET: Fetches the logged-in Staff's profile.
    PATCH: Updates the logged-in Staff's profile.
    ONLY STAFF (is_staff_new=True) can access this.
    """
    
    permission_classes = [IsAuthenticated, IsCustomStaffUser]
    parser_classes = [MultiPartParser, FormParser] # For profile_image

    def get_staff_object(self, request):
        # Helper to get staff from the logged-in user
        try:
            # The view function uses email, so we will too
            return Staff.objects.get(email=request.user.email)
        except Staff.DoesNotExist:
            raise Http404
    
    def get(self, request, format=None):
        """
        GET request: Fetches the staff's own profile.
        """
        try:
            staff = self.get_staff_object(request)
        except Http404:
            return Response({"error": "Staff profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Use 'FullStaffSerializer' to show all details, including nested User
        serializer = StaffOnlyProfileSerializer(staff)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, format=None):
        """
        PATCH request: Updates the staff's own profile.
        """
        try:
            staff = self.get_staff_object(request)
        except Http404:
            return Response({"error": "Staff profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Use the 'StaffUpdateSerializer' which handles Staff + User update
        serializer = StaffUpdateSerializer(instance=staff, data=request.data, partial=True) 
        
        if serializer.is_valid():
            updated_instance = serializer.save()
            
            # Return the full, updated profile
            read_serializer = StaffOnlyProfileSerializer(updated_instance)
            return Response(read_serializer.data, status=status.HTTP_200_OK) 
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        # Allow POST to work just like PATCH
        return self.patch(request, format)
    


# API: SUPERUSER-ONLY - VIEW/UPDATE PROFILE & SETTINGS

class SuperUserProfileAPIView(APIView):
    """
    API endpoint for Superuser 'view_profile' function.
    GET: Fetches Superuser profile and System Settings (Logo).
    PATCH: Updates Profile (Name, Email, Image) or Settings (Logo).
    ONLY SUPERUSER can access this.
    """
    permission_classes = [IsAuthenticated, CustomIsSuperuser]
    parser_classes = [MultiPartParser, FormParser] # To handle image/logo uploads

    def get(self, request, format=None):
        # 1. Serialize User Data
        user_serializer = SuperUserProfileSerializer(request.user)
        
        # 2. Serialize Settings Data (Logo)
        setting = Settings.objects.last()
        setting_data = DashboardSettingsSerializer(setting).data if setting else None
        
        return Response({
            'admin': user_serializer.data,
            'setting': setting_data
        }, status=status.HTTP_200_OK)

    def patch(self, request, format=None):
        user = request.user
        data = request.data
        
        # ---  Handle Logo Update (if 'tag' is logo or 'logo' file is present) ---
        if data.get('tag') == 'logo' or 'logo' in request.FILES:
            logo = request.FILES.get('logo')
            if logo:
                setting = Settings.objects.last()
                if setting:
                    setting.logo = logo
                    setting.save()
                else:
                    # Create new settings if not exists
                    setting = Settings.objects.create(logo=logo)
                
                return Response({
                    "message": "Logo updated successfully",
                    "setting": DashboardSettingsSerializer(setting).data
                }, status=status.HTTP_200_OK)

        # --- Handle Profile Update ---
        
        # Check for Email Duplication
        new_email = data.get('email')
        if new_email and new_email != user.email:
            if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                return Response({"error": "Email Already Exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update User fields
        serializer = SuperUserProfileSerializer(instance=user, data=data, partial=True)
        
        if serializer.is_valid():
            updated_user = serializer.save()
            
            # Sync username with email (as per your view logic)
            if new_email:
                updated_user.username = new_email
                updated_user.save()
                
            return Response({
                "message": "Profile updated successfully",
                "admin": SuperUserProfileSerializer(updated_user).data
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        # Handle POST requests as PATCH
        return self.patch(request, format)
    


class TeamLeaderStaffDashboardAPIView(APIView):
    """
    Team Leader -> Staff Dashboard (full replacement)
    - Filters lead counts by date range (updated_date OR created_date).
    - Filters staff_list by user.date_joined when start_date & end_date provided.
    - Use all_staff for lead counts (so counts remain for whole team).
    """
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]
    pagination_class = StandardResultsSetPagination

    def _parse_date_safe(self, s):
        """Accepts 'YYYY-MM-DD' or 'DD-MM-YYYY' (returns date or None)."""
        if not s:
            return None
        s = s.strip()
        for fmt in ('%Y-%m-%d', '%d-%m-%Y'):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return None

    def get(self, request, format=None):
        #  Team leader instance
        try:
            team_leader_instance = Team_Leader.objects.get(user=request.user)
        except Team_Leader.DoesNotExist:
            return Response({"error": "Team Leader profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Build staff querysets
        all_staff_qs = Staff.objects.filter(team_leader=team_leader_instance)
        associate_staff_count = all_staff_qs.filter(user__is_freelancer=True).count()

        # Read & parse query params (trim keys/values to avoid accidental spaces)
        raw_params = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in request.query_params.items()}
        start_date_str = raw_params.get('start_date')
        end_date_str = raw_params.get('end_date')

        parsed_start = self._parse_date_safe(start_date_str)
        parsed_end = self._parse_date_safe(end_date_str)

        tz = timezone.get_current_timezone()
        today = timezone.localdate()

        if parsed_start and parsed_end:
            start_dt = timezone.make_aware(datetime.combine(parsed_start, datetime.min.time()), tz)
            end_dt = timezone.make_aware(datetime.combine(parsed_end, datetime.max.time()), tz)
        else:
            # fallback to today's full day (previous behaviour if params missing/invalid)
            start_dt = timezone.make_aware(datetime.combine(today, datetime.min.time()), tz)
            end_dt = timezone.make_aware(datetime.combine(today, datetime.max.time()), tz)

        # date Q: check updated_date OR created_date in range
        date_q = Q(updated_date__range=(start_dt, end_dt)) | Q(created_date__range=(start_dt, end_dt))

        # Choose staff_list source (filtered by date_joined when params provided)
        if parsed_start and parsed_end:
            # Filter staff by user.date_joined between start_dt and end_dt
            staff_list_qs = all_staff_qs.filter(user__date_joined__range=(start_dt, end_dt))
        else:
            staff_list_qs = all_staff_qs

        # Build staff_list (user_logs) from staff_list_qs (so UI sees filtered staff)
        user_logs = []
        logged_in_count = 0
        logged_out_count = 0
        now = timezone.now()

        for staff in staff_list_qs:
            last_log = UserActivityLog.objects.filter(user=staff.user).order_by('-login_time').first()
            status_log = 'No data'
            duration = 'No data'

            if last_log:
                if last_log.logout_time:
                    status_log = 'Inactive'
                    duration_seconds = (last_log.logout_time - last_log.login_time).total_seconds()
                    logged_out_count += 1
                else:
                    status_log = 'Active'
                    duration_seconds = (now - last_log.login_time).total_seconds()
                    logged_in_count += 1
                duration = str(timedelta(seconds=int(duration_seconds)))
            else:
                logged_out_count += 1

            user_logs.append({
                'id': staff.id,
                'username': staff.name,
                'email': staff.user.email,
                'mobile': staff.mobile,
                'created_date': staff.user.date_joined,
                'status': status_log,
                'duration': duration,
                'is_freelancer': staff.user.is_freelancer,
                'user_active': staff.user.user_active,
            })

        total_staff = staff_list_qs.count()

        # Card counts (lead counts) - use all_staff_qs so cards reflect whole team
        total_leads = 0
        total_interested_leads = 0
        total_not_interested_leads = 0
        other_location_leads = 0
        not_picked_leads = 0
        lost_leads = 0
        visits_leads = 0

        for staff in all_staff_qs:
            staff_leads_qs = LeadUser.objects.filter(assigned_to=staff).filter(date_q)

            total_leads += staff_leads_qs.filter(status="Leads").count()
            total_interested_leads += staff_leads_qs.filter(status="Intrested").count()
            total_not_interested_leads += staff_leads_qs.filter(status="Not Interested").count()
            other_location_leads += staff_leads_qs.filter(status="Other Location").count()
            not_picked_leads += staff_leads_qs.filter(status="Not Picked").count()
            lost_leads += staff_leads_qs.filter(status="Lost").count()
            visits_leads += staff_leads_qs.filter(status="Visit").count()

        # Team_LeadData unassigned uploads (apply same date filter)
        leads2_qs = Team_LeadData.objects.filter(assigned_to=None, team_leader=team_leader_instance)
        total_upload_leads = leads2_qs.count()
        leads2_filtered = leads2_qs.filter(date_q)

        total_leads += leads2_filtered.filter(status="Leads").count()
        total_interested_leads += leads2_filtered.filter(status="Intrested").count()
        total_not_interested_leads += leads2_filtered.filter(status="Not Interested").count()
        other_location_leads += leads2_filtered.filter(status="Other Location").count()
        not_picked_leads += leads2_filtered.filter(status="Not Picked").count()
        lost_leads += leads2_filtered.filter(status="Lost").count()
        visits_leads += leads2_filtered.filter(status="Visit").count()

        counts_data = {
            'total_staff': total_staff,
            'associate_staff': associate_staff_count,
            'logged_in_count': logged_in_count,
            'logged_out_count': logged_out_count,
            'total_upload_leads': total_upload_leads,
            'total_leads': total_leads,
            'total_interested_leads': total_interested_leads,
            'total_not_interested_leads': total_not_interested_leads,
            'other_location_leads': other_location_leads,
            'not_picked_leads': not_picked_leads,
            'lost_leads': lost_leads,
            'visits_leads': visits_leads,
        }

        
        setting = Settings.objects.filter().last()

        response_data = {
            "counts": counts_data,
            "staff_list": user_logs,
            "setting": DashboardSettingsSerializer(setting).data if setting else None,
        }

        return Response(response_data, status=status.HTTP_200_OK)



# API: TEAM LEADER - ADD NEW STAFF (POST ONLY)

class TeamLeaderAddStaffAPIView(APIView):
    """
    API for Team Leader to add a new Staff member under them.
    ONLY TEAM LEADER (is_team_leader=True) can access this.
    """
    
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]
    parser_classes = [MultiPartParser, FormParser] 

    def post(self, request, format=None):
        serializer = TeamLeaderAddStaffSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            staff = serializer.save()
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            
            tagline = f"staff : {staff.name} created by user[Email : {request.user.email}, Team leader User]"
            tag2 = f"staff : {staff.name} created"

            team_leader = Team_Leader.objects.get(user=request.user)
            
            ActivityLog.objects.create(
                admin=team_leader.admin, 
                description=tagline,
                ip_address=ip,
                email=request.user.email,
                user_type="Team leader User",
                activity_type=tag2,
                name=request.user.name,
            )
            

            return Response({"message": "Staff Created Successfully", "id": staff.id}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class TeamLeaderStaffEditAPIView(APIView):
    """
    API endpoint for Team Leaders to retrieve and update the profile of their subordinate Staff members.
    Access is strictly controlled to the logged-in Team Leader's hierarchy.
    """
   
    
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]
    parser_classes = [MultiPartParser, FormParser]

    def get_staff_object(self, request, id):
        try:
            tl_instance = Team_Leader.objects.get(user=request.user)
        except Team_Leader.DoesNotExist:
            return None, Response({"error": "Team Leader profile not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            staff = Staff.objects.get(id=id)
        except Staff.DoesNotExist:
            return None, Response({"error": "Staff not found."}, status=status.HTTP_404_NOT_FOUND)

        if staff.team_leader != tl_instance:
            return None, Response({"error": "You do not have permission to edit this staff."}, status=status.HTTP_403_FORBIDDEN)

        return staff, None

    def get(self, request, id, format=None):
        staff, error_response = self.get_staff_object(request, id)
        if error_response:
            return error_response
        
        serializer = StaffOnlyProfileSerializer(staff)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id, format=None):
        staff, error_response = self.get_staff_object(request, id)
        if error_response:
            return error_response

        serializer = StaffUpdateSerializer(instance=staff, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_staff = serializer.save()
            
            response_serializer = StaffOnlyProfileSerializer(updated_staff)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# API: TEAM LEADER - VIEW STAFF CALENDAR

class TeamLeaderStaffCalendarAPIView(APIView):
    """
    API endpoint for Team Leaders to retrieve the detailed monthly productivity calendar for a subordinate Staff member.
    """
   
    
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]

    def get(self, request, staff_id, format=None):
        
        try:
            team_leader_instance = Team_Leader.objects.get(user=request.user)
        except Team_Leader.DoesNotExist:
            return Response({"error": "Team Leader profile not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            staff = Staff.objects.get(id=staff_id)
            if staff.team_leader != team_leader_instance:
                 return Response({"error": "You do not have permission to view this staff's calendar."}, status=status.HTTP_403_FORBIDDEN)
        except Staff.DoesNotExist:
            return Response({"error": "Staff not found."}, status=status.HTTP_404_NOT_FOUND)

        current_date = datetime.now()
        try:
            year = int(request.query_params.get('year', current_date.year))
            month = int(request.query_params.get('month', current_date.month))
        except ValueError:
            year = current_date.year
            month = current_date.month
            
        months_list = [(i, calendar.month_name[i]) for i in range(1, 13)]

        days_in_month = monthrange(year, month)[1]
        salary_arg = staff.salary
        
        if not salary_arg:
            salary_float = 0.0
        else:
            try:
                salary_float = float(salary_arg)
            except ValueError:
                salary_float = 0.0
            
        daily_salary = round(salary_float / days_in_month) if days_in_month > 0 else 0

        leads_data = LeadUser.objects.filter(
            assigned_to=staff,
            updated_date__year=year,
            updated_date__month=month,
            status='Intrested'
        ).values('updated_date__day').annotate(count=Count('id'))

        leads_map = {item['updated_date__day']: item['count'] for item in leads_data}
        total_earned_salary = 0
        weekdays = list(calendar.day_name)
        calendar_list = []

        for day in range(1, days_in_month + 1):
            date_obj = datetime(year, month, day).date()
            leads_count = leads_map.get(day, 0)
            
            if leads_count >= 10:
                daily_earn = daily_salary
            else:
                daily_earn = round((daily_salary / 10) * leads_count, 2)

            total_earned_salary += daily_earn
            
            calendar_list.append({
                'day': day,
                'date': date_obj,
                'day_name': weekdays[date_obj.weekday()],
                'leads': leads_count,
                'salary': daily_earn
            })

        response_data = {
            "staff_details": StaffProfileSerializer(staff).data,
            "year": year,
            "month": month,
            "months_list": months_list,
            "monthly_salary": salary_float,
            "earn_salary": round(total_earned_salary, 2),
            "calendar_data": DailyProductivitySerializer(calendar_list, many=True).data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    



class AutoAssignLeadsAPIView(APIView):
    """
    API endpoint for a Staff user to automatically assign a batch of leads if their current lead pool is empty.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user_email = request.user.email
        request_user = Staff.objects.filter(email=user_email).last()

        if not request_user:
            return Response({"error": "Staff user not found"}, status=status.HTTP_404_NOT_FOUND)

        team_leader = request_user.team_leader

        current_total_assign_leads = LeadUser.objects.filter(
            assigned_to=request_user, 
            status='Leads'
        ).count()

        if current_total_assign_leads != 0:
            return Response({"error": "You already have leads."}, status=status.HTTP_400_BAD_REQUEST)

        team_leader_total_leads = Team_LeadData.objects.filter(
            assigned_to=None,
            status='Leads'
        )

        leads_count = 0

        for lead in team_leader_total_leads:
            if leads_count >= 100:
                break

            if LeadUser.objects.filter(call=lead.call).exists():
                continue

            LeadUser.objects.create(
                name=lead.name,
                email=lead.email,
                call=lead.call,
                send=False,
                status=lead.status,
                assigned_to=request_user,
                team_leader=team_leader,
                user=lead.user,
            )

            lead.delete()
            leads_count += 1

        return Response(
            {"message": "Auto leads assigned successfully.", "assigned_leads": leads_count},
            status=status.HTTP_200_OK
        )
    


# API: TEAM LEADER - VIEW STAFF INCENTIVE

class TeamLeaderStaffIncentiveAPIView(APIView):
    """
    API endpoint for Team Leaders to retrieve the detailed sales incentive report for a subordinate Staff member.
    """
    
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]

    def get(self, request, staff_id, format=None):
        
        try:
            tl_instance = Team_Leader.objects.get(user=request.user)
        except Team_Leader.DoesNotExist:
            return Response({"error": "Team Leader profile not found."}, status=status.HTTP_404_NOT_FOUND)

        
        try:
            staff = Staff.objects.get(id=staff_id)
            
            if staff.team_leader != tl_instance:
                return Response({"error": "You do not have permission to view this staff's incentives."}, status=status.HTTP_403_FORBIDDEN)
        except Staff.DoesNotExist:
            return Response({"error": "Staff not found."}, status=status.HTTP_404_NOT_FOUND)

        months_list = [(i, calendar.month_name[i]) for i in range(1, 13)]
        year = int(request.query_params.get('year', datetime.now().year))
        month = int(request.query_params.get('month', datetime.now().month))

        user_type = staff.user.is_freelancer

        slab_qs = Slab.objects.all()
        slab_data = SlabSerializer(slab_qs, many=True).data
        
        if not user_type:
            for slab_item in slab_data:
                try:
                    original_amount = int(slab_item.get('amount', 0))
                    slab_item['amount'] = str(original_amount - 100) 
                except (ValueError, TypeError):
                    pass

        sell_property_qs = Sell_plot.objects.filter(
            staff=staff, 
            updated_date__year=year,
            updated_date__month=month,
        ).order_by('-created_date')

        total_earn_amount = sell_property_qs.aggregate(total_earn=Sum('earn_amount'))
        total_earn = total_earn_amount.get('total_earn') or 0

        response_data = {
            'slab': slab_data,
            'sell_property': SellPlotSerializer(sell_property_qs, many=True).data,
            'total_earn': total_earn,
            'year': year,
            'month': month,
            'months_list': months_list,
            'user_type': user_type, 
            'staff_name': staff.name
        }
        
        return Response(response_data, status=status.HTTP_200_OK)





# API: TEAM LEADER - VIEW STAFF LEADS (LIST)

class TeamLeaderStaffLeadsListAPIView(APIView):
    """
    API endpoint for Team Leaders to retrieve a paginated list of leads assigned to a subordinate Staff member, filtered by status.
    """
   
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, staff_id, tag, format=None):
       
        try:
            tl_instance = Team_Leader.objects.get(user=request.user)
            staff = Staff.objects.get(id=staff_id)
            if staff.team_leader != tl_instance:
                 return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        except (Team_Leader.DoesNotExist, Staff.DoesNotExist):
            return Response({"error": "Invalid Team Leader or Staff."}, status=status.HTTP_404_NOT_FOUND)

        base_qs = LeadUser.objects.filter(assigned_to=staff)
        
        if tag == "Intrested":
            leads = base_qs.filter(status='Intrested')
        elif tag == "Not Interested":
            leads = base_qs.filter(status='Not Interested')
        elif tag == "Other Location":
            leads = base_qs.filter(status='Other Location')
        elif tag == "Lost":
            leads = base_qs.filter(status='Lost')
        elif tag == "Visit":
            leads = base_qs.filter(status='Visit')
        else:
            leads = base_qs 

        leads = leads.order_by('-updated_date')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(leads, request, view=self)
        if page is not None:
            serializer = ApiLeadUserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ApiLeadUserSerializer(leads, many=True)
        return Response(serializer.data)



class TeamLeaderExportLeadsAPIView(APIView):
    """
    API endpoint for Team Leaders to export leads data to an Excel file (.xlsx).
    Filtering can be done for specific Staff status or for all 'Intrested' leads in the Team Leader's hierarchy.
    """
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]

    def post(self, request, format=None):
        try:
            staff_id = request.data.get('staff_id')
            status_val = request.data.get('status')
            start_date_str = request.data.get('start_date')
            end_date_str = request.data.get('end_date')
            all_interested = request.data.get('all_interested')

            tl_instance = Team_Leader.objects.get(user=request.user)

            if all_interested == "1":
                base_qs = LeadUser.objects.filter(team_leader=tl_instance, status="Intrested")
                staff_name = "All_Staff"
            else:
                staff = Staff.objects.get(id=staff_id)
                if staff.team_leader != tl_instance:
                    return Response({"error": "Permission denied."}, status=403)

                base_qs = LeadUser.objects.filter(assigned_to=staff, status=status_val)
                staff_name = staff.name

            tz = get_current_timezone()
            start_date = make_aware(datetime.strptime(start_date_str, "%Y-%m-%d"), tz)
            end_date = make_aware(
                datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1), 
                tz
            )

            leads = base_qs.filter(updated_date__range=[start_date, end_date])

            if not leads.exists():
                return Response({"message": "No data found for export."}, status=404)

            data = [{
                'Name': l.name,
                'Call': l.call,
                'Status': l.status,
                'Staff Name': l.assigned_to.name if l.assigned_to else "N/A",
                'Message': l.message,
                'Date': l.updated_date.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
            } for l in leads]

            df = pd.DataFrame(data)

            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            filename_status = "Intrested" if all_interested == "1" else status_val
            response['Content-Disposition'] = (
                f'attachment; filename={staff_name}_{filename_status}_{start_date_str}_to_{end_date_str}.xlsx'
            )

            with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Leads')

            return response

        except Exception as e:
            return Response({
                "error": "Failed to export leads.",
                "details": str(e)
            }, status=500)
        




class TeamLeadLeadsReportAPIView(APIView):
    """
    API endpoint that serves as the main dashboard and leads report for a Team Leader.
    It returns aggregated staff statistics and a paginated list of leads filtered by status tag.
    """
  
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, tag, format=None):
        try:
            team_lead = Team_Leader.objects.get(user=request.user)
        except Team_Leader.DoesNotExist:
            return Response({"error": "Team Leader profile not found."}, status=status.HTTP_404_NOT_FOUND)

        staff_members = Staff.objects.filter(team_leader=team_lead)

        total_staff = staff_members.count()
        associate_staff = staff_members.filter(user__is_freelancer=True).count()
        
        logged_in_count = 0
        logged_out_count = 0
        
        for staff in staff_members:
            last_log = UserActivityLog.objects.filter(user=staff.user).order_by('-login_time').first()
            if last_log:
                if last_log.logout_time:
                    logged_out_count += 1
                else:
                    logged_in_count += 1
            else:
                 logged_out_count += 1
        
        total_upload_leads = Team_LeadData.objects.filter(assigned_to=None, team_leader=team_lead).count()

        counts_data = {
            'total_staff': total_staff,
            'login_staff': logged_in_count,
            'logout_staff': logged_out_count,
            'associate_staff': associate_staff,
            'total_upload_leads': total_upload_leads
        }
  
        status_map = {
            'total_leads_tag': 'Leads',
            'total_interested_tag': 'Intrested',
            'total_not_interested_tag': 'Not Interested',
            'total_other_location_tag': 'Other Location',
            'total_not_picked_tag': 'Not Picked',
            'total_lost_tag': 'Lost',
            'total_visit_tag': 'Visit'
        }
        
        staff_leads_qs = LeadUser.objects.none()
        tl_leads_qs = Team_LeadData.objects.none()

        if tag == 'total_upload_lead_tag':
            tl_leads_qs = Team_LeadData.objects.filter(
                assigned_to=None,
                team_leader=team_lead,
                status='Leads' 
            )


        elif tag in status_map:
            status_val = status_map[tag]
          
            staff_leads_qs = LeadUser.objects.filter(
                assigned_to__in=staff_members, 
                status=status_val
            )
            
            tl_leads_qs = Team_LeadData.objects.filter(
                assigned_to=None, 
                team_leader=team_lead, 
                status=status_val
            )
            
        else:
           
            valid_tags = ['total_upload_lead_tag'] + list(status_map.keys())
            return Response({
                "error": f"Invalid tag: '{tag}'",
                "valid_tags_are": valid_tags
            }, status=status.HTTP_400_BAD_REQUEST)

        staff_leads_qs = staff_leads_qs.order_by('-updated_date')
        tl_leads_qs = tl_leads_qs.order_by('-created_date')

        staff_data = ApiLeadUserSerializer(staff_leads_qs, many=True).data
        tl_data = ApiTeamLeadDataSerializer(tl_leads_qs, many=True).data

        for item in staff_data: item['source'] = 'Staff Lead'
        for item in tl_data: item['source'] = 'Team Lead Data'

        combined_data = staff_data + tl_data

        page = int(request.query_params.get('page', 1))
        page_size = 10
        start = (page - 1) * page_size
        end = start + page_size
        total_count = len(combined_data)
        paginated_results = combined_data[start:end]
        
        has_next = end < total_count
        has_previous = start > 0

        return Response({
            'counts': counts_data,
            'count': total_count,
            'page': page,
            'next': f"?page={page+1}" if has_next else None,
            'previous': f"?page={page-1}" if has_previous else None,
            'results': paginated_results
        }, status=status.HTTP_200_OK)
    


class TeamLeaderStaffProductivityReportAPIView(APIView):
    """
    API endpoint to retrieve the productivity report and lead activity summary for all subordinate Staff members of a Team Leader.
    """
  
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]

    def get(self, request, format=None):
        
        try:
            team_leader_instance = Team_Leader.objects.get(user=request.user)
        except Team_Leader.DoesNotExist:
            return Response({"error": "Team Leader profile not found."}, status=status.HTTP_404_NOT_FOUND)

        date_filter = request.query_params.get('date')
        end_date_str = request.query_params.get('endDate') 
        
        today = timezone.now().date()
        start_date = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end_date = timezone.make_aware(datetime.combine(today, datetime.max.time()))

        if date_filter and end_date_str:
            try:
                s_date = datetime.strptime(date_filter, '%Y-%m-%d')
               
                if isinstance(end_date_str, str):
                    e_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                else:
                    e_date = end_date_str
                
                start_date = timezone.make_aware(datetime.combine(s_date, datetime.min.time()))
                end_date = timezone.make_aware(e_date + timedelta(days=1)) - timedelta(seconds=1)
                
            except ValueError:
                pass 

        update_filter = {'updated_date__range': [start_date, end_date]}
        
        create_filter = {'created_date__range': [start_date, end_date]}

        staffs = Staff.objects.filter(
            team_leader=team_leader_instance, 
            user__user_active=True, 
            user__is_freelancer=False
        )
        
        staff_data = []
        
        total_all_leads = 0
        total_all_interested = 0
        total_all_not_interested = 0
        total_all_other_location = 0
        total_all_not_picked = 0
        total_all_lost = 0
        total_all_visit = 0
        total_all_calls = 0

        for staff in staffs:
           
            leads_activity = LeadUser.objects.filter(assigned_to=staff, **update_filter).aggregate(
                interested=Count('id', filter=Q(status='Intrested')),
                not_interested=Count('id', filter=Q(status='Not Interested')),
                other_location=Count('id', filter=Q(status='Other Location')),
                not_picked=Count('id', filter=Q(status='Not Picked')),
                lost=Count('id', filter=Q(status='Lost')),
                visit=Count('id', filter=Q(status='Visit'))
            )
            
            leads_created = LeadUser.objects.filter(assigned_to=staff, **create_filter).aggregate(
                total_leads=Count('id')
            )

            total = leads_created['total_leads']
            interested = leads_activity['interested']
            not_interested = leads_activity['not_interested']
            other_location = leads_activity['other_location']
            not_picked = leads_activity['not_picked']
            lost = leads_activity['lost']
            visit = leads_activity['visit']
            
            total_calls = interested + not_interested + other_location + not_picked + lost + visit

            visit_percentage = (visit / total * 100) if total > 0 else 0
            interested_percentage = (interested / total * 100) if total > 0 else 0

            staff_data.append({
                'id': staff.id,
                'name': staff.name,
                'total_leads': total,
                'interested': interested,
                'not_interested': not_interested,
                'other_location': other_location,
                'not_picked': not_picked,
                'lost': lost,
                'visit': visit,
                'visit_percentage': round(visit_percentage, 2),
                'interested_percentage': round(interested_percentage, 2),
                'total_calls': total_calls,
            })

            total_all_leads += total
            total_all_interested += interested
            total_all_not_interested += not_interested
            total_all_other_location += other_location
            total_all_not_picked += not_picked
            total_all_lost += lost
            total_all_visit += visit
            total_all_calls += total_calls

        
        total_visit_percentage = (total_all_visit / total_all_leads * 100) if total_all_leads > 0 else 0
        total_interested_percentage = (total_all_interested / total_all_leads * 100) if total_all_leads > 0 else 0

        
        response_data = {
            'staff_data': staff_data, 
            
            'total_all_leads': total_all_leads,
            'total_all_interested': total_all_interested,
            'total_all_not_interested': total_all_not_interested,
            'total_all_other_location': total_all_other_location,
            'total_all_not_picked': total_all_not_picked,
            'total_all_lost': total_all_lost,
            'total_all_visit': total_all_visit,
            'total_all_calls': total_all_calls,
            
            'total_visit_percentage': round(total_visit_percentage, 2),
            'total_interested_percentage': round(total_interested_percentage, 2),
            'total_staff_count': staffs.count(),
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    



class TeamLeaderFreelancerProductivityAPIView(APIView):
    """
    API endpoint for Team Leaders to retrieve the aggregated lead productivity and conversion metrics specifically for their subordinate Freelancer staff members.
    """
 
    permission_classes = []  

    def get(self, request, *args, **kwargs):
        
        if not getattr(request.user, "is_team_leader", False):
            return Response({"detail": "Permission denied. Only Team Leader can access."},
                            status=status.HTTP_403_FORBIDDEN)

        date_filter = request.GET.get('date', None)
        end_date = request.GET.get('endDate', None)
        teamleader_id = request.GET.get('teamleader_id', None)
        admin_id = request.GET.get('admin_id', None)

       
        try:
            team_leader_instance = Team_Leader.objects.filter(user=request.user).last()
        except Exception:
            team_leader_instance = None

        if not team_leader_instance:
            return Response({"detail": "Team leader profile not found."}, status=status.HTTP_400_BAD_REQUEST)

        
        staffs = Staff.objects.filter(team_leader=team_leader_instance, user__user_active=True, user__is_freelancer=True)

       
        if admin_id:
            try:
                admins_int = int(admin_id)
                staffs = staffs.filter(team_leader__admin=admins_int)
            except Exception:
                pass
        if teamleader_id:
            try:
                tid = int(teamleader_id)
                staffs = staffs.filter(team_leader=tid)
            except Exception:
                pass

        staff_data = []
        total_all_leads = total_all_interested = total_all_not_interested = 0
        total_all_other_location = total_all_not_picked = total_all_lost = 0
        total_all_visit = total_all_calls = 0
        total_staff_count = staffs.count()
        total_calls = 0

        for staff in staffs:
            
            if date_filter and end_date:
               
                try:
                    start_dt = datetime.strptime(date_filter, '%Y-%m-%d')
                    start_dt = timezone.make_aware(start_dt)
                except Exception:
                    return Response({"error": "Invalid start date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                except Exception:
                    return Response({"error": "Invalid end date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

                end_dt = end_dt + timedelta(days=1) - timedelta(seconds=1)
                if timezone.is_naive(end_dt):
                    end_dt = timezone.make_aware(end_dt)

                lead_filter = {'updated_date__range': [start_dt, end_dt]}
                lead_filter1 = {'created_date__range': [start_dt, end_dt]}

                leads_by_date = LeadUser.objects.filter(assigned_to=staff, **lead_filter).aggregate(
                    interested=Count('id', filter=Q(status='Intrested')),
                    not_interested=Count('id', filter=Q(status='Not Interested')),
                    other_location=Count('id', filter=Q(status='Other Location')),
                    not_picked=Count('id', filter=Q(status='Not Picked')),
                    lost=Count('id', filter=Q(status='Lost')),
                    visit=Count('id', filter=Q(status='Visit'))
                )
                leads_by_date1 = LeadUser.objects.filter(assigned_to=staff, **lead_filter1).aggregate(total_leads=Count('id'))

            elif date_filter:
               
                try:
                    _ = datetime.strptime(date_filter, '%Y-%m-%d')
                except Exception:
                    return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

                leads_by_date = LeadUser.objects.filter(
                    assigned_to=staff,
                    updated_date__date=date_filter
                ).aggregate(
                    interested=Count('id', filter=Q(status='Intrested')),
                    not_interested=Count('id', filter=Q(status='Not Interested')),
                    other_location=Count('id', filter=Q(status='Other Location')),
                    not_picked=Count('id', filter=Q(status='Not Picked')),
                    lost=Count('id', filter=Q(status='Lost')),
                    visit=Count('id', filter=Q(status='Visit'))
                )
                leads_by_date1 = LeadUser.objects.filter(assigned_to=staff, created_date__date=date_filter).aggregate(total_leads=Count('id'))

            else:
                leads_by_date = LeadUser.objects.filter(assigned_to=staff).aggregate(
                    total_leads=Count('id'),
                    interested=Count('id', filter=Q(status='Intrested')),
                    not_interested=Count('id', filter=Q(status='Not Interested')),
                    other_location=Count('id', filter=Q(status='Other Location')),
                    not_picked=Count('id', filter=Q(status='Not Picked')),
                    lost=Count('id', filter=Q(status='Lost')),
                    visit=Count('id', filter=Q(status='Visit'))
                )
                leads_by_date1 = {'total_leads': leads_by_date.get('total_leads', 0)}

           
            total_leads = int(leads_by_date1.get('total_leads') or 0)
            interested = int(leads_by_date.get('interested') or 0)
            not_interested = int(leads_by_date.get('not_interested') or 0)
            other_location = int(leads_by_date.get('other_location') or 0)
            not_picked = int(leads_by_date.get('not_picked') or 0)
            lost = int(leads_by_date.get('lost') or 0)
            visit = int(leads_by_date.get('visit') or 0)

            total_calls_for_staff = interested + not_interested + other_location + not_picked + lost + visit
            visit_percentage = (visit / total_leads * 100) if total_leads > 0 else 0
            interested_percentage = (interested / total_leads * 100) if total_leads > 0 else 0

            staff_data.append({
                'id': staff.id,
                'name': staff.name,
                'total_leads': total_leads,
                'interested': interested,
                'not_interested': not_interested,
                'other_location': other_location,
                'not_picked': not_picked,
                'lost': lost,
                'visit': visit,
                'visit_percentage': round(visit_percentage, 2),
                'interested_percentage': round(interested_percentage, 2),
                'total_calls': total_calls_for_staff,
            })

            
            total_all_leads += total_leads
            total_all_interested += interested
            total_all_not_interested += not_interested
            total_all_other_location += other_location
            total_all_not_picked += not_picked
            total_all_lost += lost
            total_all_visit += visit
            total_all_calls += total_calls_for_staff
            total_calls = total_calls_for_staff

        total_visit_percentage = (total_all_visit / total_all_leads * 100) if total_all_leads > 0 else 0
        total_interested_percentage = (total_all_interested / total_all_leads * 100) if total_all_leads > 0 else 0

        resp = {
            'staff_data': staff_data,
            'total_calls': total_calls,
            'total_all_leads': total_all_leads,
            'total_all_interested': total_all_interested,
            'total_all_not_interested': total_all_not_interested,
            'total_all_other_location': total_all_other_location,
            'total_all_not_picked': total_all_not_picked,
            'total_all_lost': total_all_lost,
            'total_all_visit': total_all_visit,
            'total_all_calls': total_all_calls,
            'total_visit_percentage': round(total_visit_percentage, 2),
            'total_interested_percentage': round(total_interested_percentage, 2),
            'total_staff_count': total_staff_count,
        }

        return Response(resp, status=status.HTTP_200_OK)
    


class LeadsDashboardAPIView(APIView):
    """
    API endpoint that serves as the main dashboard for the Team Leader, providing aggregated lead counts and a list of recent leads.
    """
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]

    def get(self, request, format=None):
        user = request.user

       
        try:
            team_leader = Team_Leader.objects.get(user=user)
        except Team_Leader.DoesNotExist:
            return Response({"detail": "Team leader profile not found."}, status=status.HTTP_404_NOT_FOUND)

        
        qs = LeadUser.objects.filter(team_leader=team_leader).order_by('-id')

       
        page_size = 10
        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(1)  # always return first page to frontend (or change logic as needed)

       
        serializer = LeadForDashboardSerializer(page_obj.object_list, many=True, context={'request': request})
        serialized = serializer.data

        items = []
        
        for idx, lead_data in enumerate(serialized, start=1):
            phone = lead_data.get('mobile') or lead_data.get('phone') or ""
            whatsapp_flag = bool(phone)  
            items.append({
                'sn': idx,
                'id': lead_data.get('id'),
                'name': lead_data.get('name'),
                'phone': phone,
                'whatsapp': whatsapp_flag,
                'status': lead_data.get('status'),
                #'assigned_to': lead_data.get('assigned_to'),
                #'possible_statuses': ["Leads", "Intrested", "Not Interested", "Other Location", "Not Picked", "Lost", "Customer", "Maybe"],
            })

        staff_qs = Staff.objects.filter(team_leader=team_leader)
        staff_list = [{'id': s.id, 'name': s.name} for s in staff_qs]

       
        aggregates = {
            'total_upload_leads': LeadUser.objects.filter(team_leader=team_leader, assigned_to__isnull=True).count(),
            'total_leads': LeadUser.objects.filter(team_leader=team_leader, status="Leads").count(),
            'total_interested_leads': LeadUser.objects.filter(team_leader=team_leader, status="Intrested").count(),
            'total_lost_leads': LeadUser.objects.filter(team_leader=team_leader, status="Lost").count(),
        }

        response = {
            'staff_name': items,
            'staff_list': staff_list,
            'aggregates': aggregates,
            'dashboard_image': '/mnt/data/06177923-6185-42b4-848d-92bccd262b6e.png',  # local path -> dev will convert to URL
        }

        return Response(response, status=status.HTTP_200_OK)





class AddLeadAPI(APIView):
    """
    API endpoint for a Team Leader to manually create and add a new lead into the system.
    The created lead is automatically linked to the managing Team Leader.
    """

    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]

    def post(self, request, format=None):
       
        serializer = LeadCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        
        try:
            team_lead = Team_Leader.objects.get(user=request.user)
        except Team_Leader.DoesNotExist:
            
            team_lead = Team_Leader.objects.filter(email=request.user.username).first()
            if not team_lead:
                return Response({'detail': 'Team leader profile not found.'}, status=status.HTTP_400_BAD_REQUEST)

       
        validated = serializer.validated_data
        mobile = validated.pop('mobile', '') or ''
       
        lead = LeadUser.objects.create(
            user = request.user,
            team_leader = team_lead,
            name = validated.get('name', ''),
            email = validated.get('email', ''),
            call = mobile,
            message = validated.get('message', ''),
            status = validated.get('status', '')
        )

       
        return Response({
            'id': lead.id,
            'name': lead.name,
            'email': lead.email,
            'status': lead.status,
            'call': lead.call,
            'message': lead.message,
        }, status=status.HTTP_201_CREATED)



class TeamCustomerAPIView(APIView):
    """
    API endpoint for the Team Leader to retrieve a paginated list of 'Intrested' leads, filtered by follow-up status or search query.
    """
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]

    def get(self, request, tag=None, format=None):
      
        VALID_TAGS = ['pending_follow', 'today_follow', 'tommorrow_follow','interested']

       
        tag_q = request.query_params.get('tag')
        if tag_q:
            tag = tag_q.strip()

        
        if not tag:
            return Response({
                "detail": "Tag is required. Valid tags: " + ", ".join(VALID_TAGS),
                "valid_tags": VALID_TAGS
            }, status=400)

        
        if tag not in VALID_TAGS:
            return Response({
                "detail": f"Invalid tag '{tag}'. Valid tags: " + ", ".join(VALID_TAGS),
                "valid_tags": VALID_TAGS
            }, status=400)
        
        

        
        user = request.user
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        search_query = request.query_params.get('search', '').strip()

        
        try:
            team_leader = Team_Leader.objects.filter(user=user).last() or Team_Leader.objects.filter(email=user.email).last()
        except Exception:
            team_leader = None

        qs = LeadUser.objects.none()

       
        if search_query:
            qs = LeadUser.objects.filter(
                Q(name__icontains=search_query) | Q(call__icontains=search_query) | Q(team_leader__name__icontains=search_query),
                status='Intrested'
            ).order_by('-updated_date')
        else:
            
            if tag == 'pending_follow':
                qs = LeadUser.objects.filter(status='Intrested', follow_up_date__isnull=False).order_by('-updated_date')
            elif tag == 'today_follow':
                qs = LeadUser.objects.filter(status='Intrested', follow_up_date=today).order_by('-updated_date')
            elif tag == 'tommorrow_follow':
                qs = LeadUser.objects.filter(status='Intrested', follow_up_date=tomorrow).order_by('-updated_date')
            elif tag == 'interested':
                qs = LeadUser.objects.filter(status='Intrested').order_by('-updated_date')

        if team_leader:
            qs = qs.filter(team_leader=team_leader)

        page_size = 50
        paginator = Paginator(qs, page_size)
        page_number = request.query_params.get('page', 1)
        page_obj = paginator.get_page(page_number)

        serializer = ApiLeadUserSerializer(page_obj.object_list, many=True, context={'request': request})
        leads_data = serializer.data

        total_pages = paginator.num_pages
        current_page = page_obj.number

        if total_pages <= 7:
            page_range = list(range(1, total_pages + 1))
        else:
            pr = list(range(1, 4))
            start = max(3, current_page - 2)
            end = min(current_page + 1, total_pages - 2)
            pr.extend(list(range(start, end + 1)))
            pr.extend(list(range(total_pages - 2, total_pages + 1)))
            page_range = sorted(set(pr))

        response = {
            'leads': leads_data,
            'total_items': paginator.count,
            'page': current_page,
            'total_pages': total_pages,
            'page_range': page_range,
            'interested_leads_count': qs.count(),
            'reference_image': '/mnt/data/c2dc665d-9d54-40ab-a57d-08f450e93be3.png',
            'valid_tags': VALID_TAGS
        }
        return Response(response, status=200)




# API: TEAM LEADER-ONLY - UPDATE LEAD STATUS

class TeamLeaderUpdateLeadAPIView(APIView):
    """
    API endpoint for Team Leaders to update the status, follow-up, and details of a lead.
    Enforces strict hierarchy control, ensuring the lead belongs to the Team Leader's team before updating.
    """
   
    
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]

    def patch(self, request, id, format=None):
        
        try:
            tl_instance = Team_Leader.objects.get(user=request.user)
        except Team_Leader.DoesNotExist:
            return Response({"error": "Team Leader profile not found."}, status=status.HTTP_404_NOT_FOUND)

       
        try:
            lead_user = LeadUser.objects.get(id=id)
            
            is_authorized = False
            
            if lead_user.assigned_to and lead_user.assigned_to.team_leader == tl_instance:
                is_authorized = True
            elif lead_user.team_leader == tl_instance:
                is_authorized = True
                
            if not is_authorized:
                 return Response({"error": "You do not have permission to update this lead."}, status=status.HTTP_403_FORBIDDEN)

        except LeadUser.DoesNotExist:
            return Response({"error": "Lead not found."}, status=status.HTTP_404_NOT_FOUND)

        current_status = lead_user.status

        
        serializer = LeadUpdateSerializer(instance=lead_user, data=request.data, partial=True)
        
        if serializer.is_valid():
            status_val = serializer.validated_data.get('status')
            message = serializer.validated_data.get('message', lead_user.message)
            follow_date = serializer.validated_data.get('followDate')
            follow_time = serializer.validated_data.get('followTime')

           
            if status_val == "Not Picked":
                try:
                    Team_LeadData.objects.create(
                        user=lead_user.user,
                        name=lead_user.name,
                        call=lead_user.call,
                        status="Leads", 
                        email=lead_user.email,
                        team_leader=tl_instance 
                    )
                    lead_user.delete() 
                    return Response({'message': 'Lead moved back to Team Leader pool (Not Picked)'}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'error': f'Failed to move lead: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

           
            lead_user.status = status_val
            lead_user.message = message
            
            if follow_date:
                lead_user.follow_up_date = follow_date
            if follow_time:
                lead_user.follow_up_time = follow_time
            
            lead_user.save()

            
            try:
                Leads_history.objects.create(
                    leads=lead_user,
                    lead_id=id,
                    status=status_val,
                    name=lead_user.name,
                    message=message
                )
            except Exception:
                pass 

            
            try:
                ip = get_client_ip(request)
                user_type = get_user_type(request.user)
                tagline = f"Lead status changed from {current_status} to {status_val} by user[Email: {request.user.email}, {user_type}]"
                
                ActivityLog.objects.create(
                    team_leader=tl_instance,
                    description=tagline,
                    ip_address=ip,
                    email=request.user.email,
                    user_type=user_type,
                    activity_type=status_val,
                    name=request.user.name,
                )
            except Exception:
                pass

            return Response({'message': 'Lead updated successfully', 'data': ApiLeadUserSerializer(lead_user).data}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, id, format=None):
       
        return self.patch(request, id, format)
    





class TeamLeaderLeadHistoryAPIView(APIView):
    """
    API endpoint for Team Leaders to retrieve the full history of status changes for a specific lead.
    Enforces hierarchy check to ensure the lead belongs to the Team Leader's team.
    """
   
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, id, format=None):
       
        try:
            tl_instance = Team_Leader.objects.get(user=request.user)
        except Team_Leader.DoesNotExist:
            return Response({"error": "Team Leader profile not found."}, status=status.HTTP_404_NOT_FOUND)

       
        try:
            lead = LeadUser.objects.get(id=id)
            is_authorized = False
            
           
            if lead.assigned_to and lead.assigned_to.team_leader == tl_instance:
                is_authorized = True
            
            elif lead.team_leader == tl_instance:
                is_authorized = True
                
            if not is_authorized:
                return Response({"error": "Permission denied. This lead does not belong to your team."}, status=status.HTTP_403_FORBIDDEN)

        except LeadUser.DoesNotExist:
           
            return Response({"error": "Lead not found."}, status=status.HTTP_404_NOT_FOUND)

      
        history_qs = Leads_history.objects.filter(lead_id=id).order_by('-updated_date')

    
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(history_qs, request, view=self)
        
        if page is not None:
            serializer = LeadsHistorySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = LeadsHistorySerializer(history_qs, many=True)
        return Response(serializer.data)
    




class ActivityLogsRoleAPIView(APIView):
    """
    API endpoint to retrieve paginated activity logs with access and filtering determined by the authenticated user's role.
    """
   
    permission_classes = [IsAuthenticated , IsCustomTeamLeaderUser]

    def get(self, request, format=None):
        user = request.user

        
        if getattr(user, 'is_superuser', False):
            qs = ActivityLog.objects.all().order_by('-created_date')
        elif getattr(user, 'is_admin', False):
           
            admin_profile = Admin.objects.filter(email=user.email).last()
            if not admin_profile:
                return Response({"detail": "Admin profile not found for this user."}, status=status.HTTP_404_NOT_FOUND)
            qs = ActivityLog.objects.filter(admin=admin_profile).order_by('-created_date')
        elif getattr(user, 'is_team_leader', False):
            team_leader_profile = Team_Leader.objects.filter(email=user.email).last() or Team_Leader.objects.filter(user=user).last()
            if not team_leader_profile:
                return Response({"detail": "Team leader profile not found for this user."}, status=status.HTTP_404_NOT_FOUND)
            qs = ActivityLog.objects.filter(team_leader=team_leader_profile).order_by('-created_date')
        elif getattr(user, 'is_staff_new', False):
            staff_profile = Staff.objects.filter(email=user.email).last()
            
            if staff_profile:
                qs = ActivityLog.objects.filter(Q(user=user) | Q(staff=staff_profile)).order_by('-created_date')
            else:
               
                qs = ActivityLog.objects.filter(user=user).order_by('-created_date')
        else:
            
            return Response({"detail": "You do not have permission to view activity logs."}, status=status.HTTP_403_FORBIDDEN)

        
        q = request.query_params.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(description__icontains=q) |
                Q(email__icontains=q) |
                Q(name__icontains=q) |
                Q(activity_type__icontains=q)
            )

       
        try:
            page_size = int(request.query_params.get('page_size', 100))
            if page_size <= 0:
                page_size = 100
        except Exception:
            page_size = 100

        paginator = Paginator(qs, page_size)
        page_number = request.query_params.get('page', 1)
        page_obj = paginator.get_page(page_number)

        serializer = ActivityLogSerializer(page_obj.object_list, many=True, context={'request': request})
        logs_data = serializer.data

        total_pages = paginator.num_pages
        current_page = page_obj.number

        
        if total_pages <= 7:
            page_range = list(range(1, total_pages + 1))
        else:
            pr = list(range(1, 4))
            start = max(3, current_page - 2)
            end = min(current_page + 1, total_pages - 2)
            pr.extend(list(range(start, end + 1)))
            pr.extend(list(range(total_pages - 2, total_pages + 1)))
            page_range = sorted(set(pr))

        response = {
            'logs': logs_data,
            'page': current_page,
            'page_size': page_size,
            'total_items': paginator.count,
            'total_pages': total_pages,
            'page_range': page_range,
            
            'reference_image': '/mnt/data/c2dc665d-9d54-40ab-a57d-08f450e93be3.png'
        }
        return Response(response, status=status.HTTP_200_OK)




class VisitTeamLeaderAPIView(APIView):
    """
    
    Response:
    {
      "items": [...],
      "total_items": 123,
      "page": 1,
      "page_size": 50,
      "total_pages": 3,
      "page_range": [1,2,3],
      "reference_image": "/mnt/data/c2dc665d-9d54-40ab-a57d-08f450e93be3.png"
    }
    """
    permission_classes = [IsAuthenticated , IsCustomTeamLeaderUser]

    def get(self, request, format=None):
        user = request.user
        page_size = 50

        items = []
        total_count = 0
        serializer_class = None

        if getattr(user, 'is_superuser', False):
            qs = LeadUser.objects.filter(status='Visit').order_by('-updated_date')
            serializer_class = ApiLeadUserSerializer

        elif getattr(user, 'is_team_leader', False):
            team_leader = Team_Leader.objects.filter(email=user.email).last() or Team_Leader.objects.filter(user=user).last()
            if not team_leader:
                return Response({"detail": "Team leader profile not found."}, status=status.HTTP_404_NOT_FOUND)
            qs = LeadUser.objects.filter(team_leader=team_leader, status='Visit').order_by('-updated_date')
            serializer_class = ApiLeadUserSerializer

        # others -> Team_LeadData for that team_leader
        else:
            team_leader = Team_Leader.objects.filter(email=user.email).last() or Team_Leader.objects.filter(user=user).last()
            # if no team_leader found, return empty but 200 (original view used team_leader variable; keep safe)
            if not team_leader:
                qs = Team_LeadData.objects.none()
            else:
                qs = Team_LeadData.objects.filter(team_leader=team_leader, status='Visit').order_by('-created_date')
            serializer_class = ApiTeamLeadDataSerializer

        # Optional: support search param ?search=...
        q = request.query_params.get('search', '').strip()
        if q:
            # apply search for both LeadUser and Team_LeadData where fields exist
            if serializer_class == ApiLeadUserSerializer:
                qs = qs.filter(Q(name__icontains=q) | Q(call__icontains=q) | Q(email__icontains=q))
            else:
                qs = qs.filter(Q(name__icontains=q) | Q(call__icontains=q) | Q(email__icontains=q))

        # Pagination
        paginator = Paginator(qs, page_size)
        page_number = request.query_params.get('page', 1)
        page_obj = paginator.get_page(page_number)

        serializer = serializer_class(page_obj.object_list, many=True, context={'request': request})
        items = serializer.data
        total_count = paginator.count
        total_pages = paginator.num_pages
        current_page = page_obj.number

        # page_range minimal numeric (no '...' strings)
        if total_pages <= 7:
            page_range = list(range(1, total_pages + 1))
        else:
            pr = list(range(1, 4))
            start = max(3, current_page - 2)
            end = min(current_page + 1, total_pages - 2)
            pr.extend(list(range(start, end + 1)))
            pr.extend(list(range(total_pages - 2, total_pages + 1)))
            page_range = sorted(set(pr))

        response = {
            'items': items,
            'total_items': total_count,
            'page': current_page,
            'page_size': page_size,
            'total_pages': total_pages,
            'page_range': page_range,
            'reference_image': '/mnt/data/c2dc665d-9d54-40ab-a57d-08f450e93be3.png'
        }
        return Response(response, status=status.HTTP_200_OK)
    


class TeamLeaderExportDashboardLeadsAPIView(APIView):
    """
    API endpoint for Team Leaders to export filtered leads data (dashboard view) to an Excel file.
    Filtering is conditional based on follow-up tags or date range for 'Intrested' leads.
    """
  
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]

    def post(self, request, format=None):
        # Get Params
        tag = request.data.get('tag') # E.g., 'today_followups', 'Intrested'
        staff_id = request.data.get('staff_id')
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        
        # Verify Team Leader
        try:
            tl_instance = Team_Leader.objects.get(user=request.user)
        except Team_Leader.DoesNotExist:
            return Response({"error": "Team Leader profile not found."}, status=status.HTTP_404_NOT_FOUND)

        if staff_id:
            try:
                staff = Staff.objects.get(id=staff_id)
                if staff.team_leader != tl_instance:
                    return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
                # Staff Leads
                base_qs = LeadUser.objects.filter(assigned_to=staff)
            except Staff.DoesNotExist:
                 return Response({"error": "Staff not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # All Leads under TL (Assigned to any staff OR unassigned)
            staff_members = Staff.objects.filter(team_leader=tl_instance)
            base_qs = LeadUser.objects.filter(
                Q(assigned_to__in=staff_members) | Q(team_leader=tl_instance, assigned_to=None)
            )

        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        
        if tag == 'today_followups':
            # Logic: Status Interested + FollowUp Date is TODAY
            leads = base_qs.filter(status='Intrested', follow_up_date=today)
            filename_tag = "Today_FollowUps"
            
        elif tag == 'tomorrow_followups':
            # Logic: Status Interested + FollowUp Date is TOMORROW
            leads = base_qs.filter(status='Intrested', follow_up_date=tomorrow)
            filename_tag = "Tomorrow_FollowUps"

        elif tag == 'pending_followups':
            # Logic: Status Interested + FollowUp Date exists (Pending)
            leads = base_qs.filter(status='Intrested', follow_up_date__isnull=False)
            filename_tag = "Pending_FollowUps"

        elif tag == 'Intrested':
            # Logic: Status Interested + User selected Date Range (Created/Updated)
            try:
                if start_date_str and end_date_str:
                    s_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    e_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    
                    start = timezone.make_aware(datetime.combine(s_date, datetime.min.time()))
                    end = timezone.make_aware(datetime.combine(e_date, datetime.max.time()))
                    
                    # Filter by updated_date
                    leads = base_qs.filter(status='Intrested', updated_date__range=[start, end])
                else:
                    # Default: All Interested
                    leads = base_qs.filter(status='Intrested')
            except ValueError:
                 return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)
            
            filename_tag = "Interested_Leads"

        else:
             return Response({"error": "Invalid tag provided."}, status=status.HTTP_400_BAD_REQUEST)

        # ---  GENERATE EXCEL ---
        data = []
        for lead in leads:
            assigned_name = lead.assigned_to.name if lead.assigned_to else "Unassigned"
            
            data.append({
                'Name': lead.name,
                'Call': lead.call,
                'Status': lead.status,
                'Staff Name': assigned_name,
                'Follow Up Date': lead.follow_up_date,
                'Follow Up Time': lead.follow_up_time,
                'Message': lead.message,
                'Date Added': localtime(lead.created_date).strftime('%Y-%m-%d'),
            })

        if not data:
             return Response({"message": "No data found for export."}, status=status.HTTP_404_NOT_FOUND)

        df = pd.DataFrame(data)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={filename_tag}_{today}.xlsx'

        with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Leads')

        return response
    



# API: TEAM LEADER - VIEW/UPDATE PROFILE

class TeamLeaderProfileViewAPIView(APIView):
    """
    API endpoint for 'team_view_profile' (Team Leader Dashboard).
    GET: Fetches logged-in Team Leader's profile.
    PATCH: Updates logged-in Team Leader's profile.
    ONLY TEAM LEADER can access this.
    """
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser]
    parser_classes = [MultiPartParser, FormParser]

    def get_tl_object(self, request):
        try:
            return Team_Leader.objects.get(user=request.user)
        except Team_Leader.DoesNotExist:
            return None

    def get(self, request, format=None):
        tl_instance = self.get_tl_object(request)
        if not tl_instance:
            return Response({"error": "Team Leader profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TeamLeaderProfileSerializer(tl_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, format=None):
        tl_instance = self.get_tl_object(request)
        if not tl_instance:
            return Response({"error": "Team Leader profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Use existing update serializer which handles User + TL model update
        serializer = TeamLeaderUpdateSerializer(instance=tl_instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_instance = serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "data": TeamLeaderProfileSerializer(updated_instance).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request, format=None):
        return self.patch(request, format)
    










# # ==========================================================
# # API: SUPERUSER-ONLY - VIEW/UPDATE PROFILE & SETTINGS
# # ==========================================================
# class SuperUserProfileAPIView(APIView):
#     """
#     API endpoint for Superuser 'view_profile' function.
#     GET: Fetches Superuser profile and System Settings (Logo).
#     PATCH: Updates Profile (Name, Email, Image) or Settings (Logo).
#     ONLY SUPERUSER can access this.
#     """
#     permission_classes = [IsAuthenticated, CustomIsSuperuser]
#     parser_classes = [MultiPartParser, FormParser] # Image/File upload ke liye

#     def get(self, request, format=None):
#         # 1. Serialize User Data
#         user_serializer = SuperUserProfileSerializer(request.user)
        
#         # 2. Serialize Settings Data (Logo)
#         setting = Settings.objects.last()
#         setting_data = DashboardSettingsSerializer(setting).data if setting else None
        
#         return Response({
#             'admin': user_serializer.data,
#             'setting': setting_data
#         }, status=status.HTTP_200_OK)

#     def patch(self, request, format=None):
#         user = request.user
#         data = request.data.copy() # Copy data to make it mutable
        
#         # --- 1. Handle Logo Update (if 'tag' is logo or 'logo' file is present) ---
#         if data.get('tag') == 'logo' or 'logo' in request.FILES:
#             logo = request.FILES.get('logo')
#             if logo:
#                 setting = Settings.objects.last()
#                 if setting:
#                     setting.logo = logo
#                     setting.save()
#                 else:
#                     # Create new settings if not exists
#                     setting = Settings.objects.create(logo=logo)
                
#                 return Response({
#                     "message": "Logo updated successfully",
#                     "setting": DashboardSettingsSerializer(setting).data
#                 }, status=status.HTTP_200_OK)
#             else:
#                  return Response({"error": "Logo file not provided."}, status=status.HTTP_400_BAD_REQUEST)

#         # --- 2. Handle Profile Update ---
        
#         # Check for Email Duplication
#         new_email = data.get('email')
#         if new_email and new_email != user.email:
#             if User.objects.filter(email=new_email).exclude(id=user.id).exists():
#                 return Response({"error": "Email Already Exists"}, status=status.HTTP_400_BAD_REQUEST)
        
#         # Update User fields
#         serializer = SuperUserProfileSerializer(instance=user, data=data, partial=True)
        
#         if serializer.is_valid():
#             updated_user = serializer.save()
            
#             # Sync username with email (as per your view logic)
#             if new_email:
#                 updated_user.username = new_email
#                 updated_user.save()
                
#             return Response({
#                 "message": "Profile updated successfully",
#                 "admin": SuperUserProfileSerializer(updated_user).data
#             }, status=status.HTTP_200_OK)
            
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def post(self, request, format=None):
#         # Allow POST to work just like PATCH
#         return self.patch(request, format)
    






# API: ADMIN - STAFF LEADS LIST (BY STATUS TAG)

class AdminnStaffLeadsAPIView(APIView):
    """
    API endpoint exclusively for the Admin role to retrieve a paginated list of leads filtered by status.
    Access is restricted to leads managed by the Admin's subordinate Team Leaders.
    """
    
    permission_classes = [IsAuthenticated, IsCustomAdminUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, tag, format=None):
        paginator = self.pagination_class()
        
        try:
            admin_instance = Admin.objects.get(self_user=request.user)
        except Admin.DoesNotExist:
            return Response({"error": "Admin profile not found."}, status=status.HTTP_404_NOT_FOUND)

        team_leaders = Team_Leader.objects.filter(admin=admin_instance)

        
        base_qs = LeadUser.objects.filter(team_leader__in=team_leaders).order_by('-updated_date')

        if tag == 'total_lead':
            leads = base_qs.filter(status="Leads")
        elif tag == 'visits':
            leads = base_qs.filter(status="Visit")
        elif tag == 'interested':
            leads = base_qs.filter(status="Intrested") # Note spelling 'Intrested' from models
        elif tag == 'not_interested':
            leads = base_qs.filter(status="Not Interested")
        elif tag == 'other_location':
            leads = base_qs.filter(status="Other Location")
        elif tag == 'not_picked':
            leads = base_qs.filter(status="Not Picked")
        elif tag == 'Total_earning': # Adding this just in case, though not in your 'if' block context list
            leads = base_qs.filter(status="Total_earning")
        else:
            return Response(
                {"error": f"Invalid tag: {tag}. Valid tags are: total_lead, visits, interested, not_interested, other_location, not_picked, Total_earning"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 5. Paginate and Serialize
        page = paginator.paginate_queryset(leads, request, view=self)
        
        if page is not None:
            serializer = ApiLeadUserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ApiLeadUserSerializer(leads, many=True)
        return Response(serializer.data)




# API: ADMIN - VIEW/UPDATE PROFILE

class AdminProfileViewAPIView(APIView):
    """
    API endpoint for the authenticated Admin user to view and update their own profile details.
    """
   
    permission_classes = [IsAuthenticated, IsCustomAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def get_admin_object(self, request):
        try:
            # Using email as per your view logic, but self_user is safer if linked correctly
            return Admin.objects.get(email=request.user.email)
        except Admin.DoesNotExist:
            return None

    def get(self, request, format=None):
        admin_instance = self.get_admin_object(request)
        if not admin_instance:
            return Response({"error": "Admin profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AdminProfileSerializer(admin_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, format=None):
        admin_instance = self.get_admin_object(request)
        if not admin_instance:
            return Response({"error": "Admin profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Use existing update serializer which handles User + Admin model update
        serializer = AdminUpdateSerializer(instance=admin_instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_instance = serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "data": AdminProfileSerializer(updated_instance).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request, format=None):
        return self.patch(request, format)
    



def user_has_field(field_name):
    """Return True if User model has a DB field named `field_name` (not a property)."""
    try:
        User._meta.get_field(field_name)
        return True
    except Exception:
        return False
    

class AdminToggleStatusAPIView(APIView):
    """
    API endpoint for the Admin role to toggle the active status (user_active field) of a subordinate user (Team Leader or Staff).
    """
    permission_classes = [IsAuthenticated, IsCustomAdminUser]

    def post(self, request, user_id):
        if not request.user or not request.user.is_authenticated:
            return Response({"error": "Authentication required. Provide valid token/session."}, status=401)

        admin_obj = None
        possible_fields = ["user", "self_user", "admin_user"]  # adjust if your model uses different name
        for field in possible_fields:
            lookup = {f"{field}": request.user}
            try:
                admin_obj = Admin.objects.get(**lookup)
                break
            except Admin.DoesNotExist:
                continue

        if not admin_obj:
            return Response({
                "error": "Admin profile not found for the authenticated user.",
                "hint": "Check Admin model relation field (user/self_user/admin_user) and that the logged-in user is an admin.",
                "request_user_id": getattr(request.user, "id", None),
                "request_user_username": getattr(request.user, "username", None)
            }, status=404)

        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Target user not found."}, status=404)

        # Authorization: is target under this admin?
        is_authorized = Team_Leader.objects.filter(user=target_user, admin=admin_obj).exists() \
                        or Staff.objects.filter(user=target_user, team_leader__admin=admin_obj).exists()

        if not is_authorized:
            return Response({"error": "Permission denied. This user is not under your administration."}, status=403)

        # Toggle and save
        target_user.user_active = not target_user.user_active
        target_user.save()

        return Response({
            "message": f"User is now {'Active' if target_user.user_active else 'Inactive'}",
            "user_id": target_user.id,
            "user_active": target_user.user_active
        }, status=200)



# API: ADMIN-ONLY - ACTIVITY LOGS (TIME SHEET)

class AdminActivityLogAPIView(APIView):
   
    """
    API endpoint to retrieve the activity logs generated exclusively by the authenticated Admin user.
    """
    permission_classes = [IsAuthenticated, IsCustomAdminUser]
    pagination_class = ActivityLogPagination # Using your custom pagination

    def get(self, request, format=None):
        # Get Admin Profile
        try:
            # 'self_user' is the User instance linked to Admin
            admin_user = Admin.objects.get(self_user=request.user)
        except Admin.DoesNotExist:
            # Fallback: Try getting by email if self_user logic fails (as per your view logic backup)
            try:
                admin_user = Admin.objects.filter(email=request.user.email).last()
                if not admin_user:
                    return Response({"error": "Admin profile not found."}, status=status.HTTP_404_NOT_FOUND)
            except:
                return Response({"error": "Admin profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get Logs for this Admin
        # Logic from your view: logs = ActivityLog.objects.filter(admin=admin_user).order_by('-created_date')
        logs_qs = ActivityLog.objects.filter(admin=admin_user).order_by('-created_date')

        # Paginate & Serialize
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(logs_qs, request, view=self)
        
        if page is not None:
            serializer = ActivityLogSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Fallback if pagination fails
        serializer = ActivityLogSerializer(logs_qs, many=True)
        return Response(serializer.data)
    







# API: FREELANCER PRODUCTIVITY REPORT (ALL ROLES)

class FreelancerProductivityReportAPIView(APIView):
    """
    API endpoint to retrieve the productivity report and lead activity summary for Freelancer (Associate) staff members.
    The data scope is determined by the logged-in user's role and hierarchy (Superuser, Admin, or Team Leader).
    """
   
    permission_classes = [IsAuthenticated , IsCustomAdminUser ]

    def get(self, request, format=None):
        # Get Query Params
        date_filter = request.query_params.get('date')
        end_date_str = request.query_params.get('endDate')
        teamleader_id = request.query_params.get('teamleader_id')
        admin_id = request.query_params.get('admin_id')
        
        # Determine Staffs (Freelancers) based on User Role
        staffs = Staff.objects.none()
        
        if request.user.is_superuser:
            staffs = Staff.objects.filter(user__user_active=True, user__is_freelancer=True)
            if admin_id:
                staffs = staffs.filter(team_leader__admin=admin_id)
            if teamleader_id:
                staffs = staffs.filter(team_leader=teamleader_id)

        elif request.user.is_admin:
            try:
                admin_user = Admin.objects.get(self_user=request.user)
                staffs = Staff.objects.filter(
                    team_leader__admin=admin_user, 
                    user__user_active=True, 
                    user__is_freelancer=True
                )
                if teamleader_id:
                    staffs = staffs.filter(team_leader=teamleader_id)
            except Admin.DoesNotExist:
                pass

        elif request.user.is_team_leader:
            try:
                team_leader = Team_Leader.objects.get(user=request.user)
                staffs = Staff.objects.filter(
                    team_leader=team_leader, 
                    user__user_active=True, 
                    user__is_freelancer=True
                )
            except Team_Leader.DoesNotExist:
                pass

        #Date Filter Logic
        today = timezone.now().date()
        start_date = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end_date = timezone.make_aware(datetime.combine(today, datetime.max.time()))
        
        if date_filter:
            try:
                s_date = datetime.strptime(date_filter, '%Y-%m-%d')
                start_date = timezone.make_aware(datetime.combine(s_date, datetime.min.time()))
                
                if end_date_str:
                    e_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    end_date = timezone.make_aware(datetime.combine(e_date, datetime.max.time()))
                else:
                    # If no end date, assume single day filter (start to end of that day)
                    end_date = timezone.make_aware(datetime.combine(s_date, datetime.max.time()))
            except ValueError:
                pass

        # Filters
        # Updated date for status changes
        activity_filter = {'updated_date__range': [start_date, end_date]}
        # Created date for new leads
        creation_filter = {'created_date__range': [start_date, end_date]}

        staff_data = []
        total_all_leads = 0
        total_all_interested = 0
        total_all_not_interested = 0
        total_all_other_location = 0
        total_all_not_picked = 0
        total_all_lost = 0
        total_all_visit = 0
        total_all_calls = 0

        for staff in staffs:
            # Calculate Leads for this Staff
            staff_leads = LeadUser.objects.filter(assigned_to=staff)
            
            # Counts
            total = staff_leads.filter(status="Leads", **creation_filter).count()
            interested = staff_leads.filter(status="Intrested", **activity_filter).count()
            not_interested = staff_leads.filter(status="Not Interested", **activity_filter).count()
            other_location = staff_leads.filter(status="Other Location", **activity_filter).count()
            not_picked = staff_leads.filter(status="Not Picked", **activity_filter).count()
            lost = staff_leads.filter(status="Lost", **activity_filter).count()
            visit = staff_leads.filter(status="Visit", **activity_filter).count()

            total_calls = interested + not_interested + other_location + not_picked + lost + visit

            # Percentages
            visit_percentage = (visit / total * 100) if total > 0 else 0
            interested_percentage = (interested / total * 100) if total > 0 else 0

            staff_data.append({
                'id': staff.id,
                'name': staff.name,
                'total_leads': total,
                'interested': interested,
                'not_interested': not_interested,
                'other_location': other_location,
                'not_picked': not_picked,
                'lost': lost,
                'visit': visit,
                'visit_percentage': round(visit_percentage, 2),
                'interested_percentage': round(interested_percentage, 2),
                'total_calls': total_calls,
            })

            total_all_leads += total
            total_all_interested += interested
            total_all_not_interested += not_interested
            total_all_other_location += other_location
            total_all_not_picked += not_picked
            total_all_lost += lost
            total_all_visit += visit
            total_all_calls += total_calls

        # Grand Total Percentages
        total_visit_percentage = (total_all_visit / total_all_leads * 100) if total_all_leads > 0 else 0
        total_interested_percentage = (total_all_interested / total_all_leads * 100) if total_all_leads > 0 else 0

        # Final Response
        response_data = {
            "counts": {
                'total_all_leads': total_all_leads,
                'total_all_interested': total_all_interested,
                'total_all_not_interested': total_all_not_interested,
                'total_all_other_location': total_all_other_location,
                'total_all_not_picked': total_all_not_picked,
                'total_all_lost': total_all_lost,
                'total_all_visit': total_all_visit,
                'total_all_calls': total_all_calls,
                'total_visit_percentage': round(total_visit_percentage, 2),
                'total_interested_percentage': round(total_interested_percentage, 2),
                'total_staff_count': staffs.count(),
            },
            "staff_data": staff_data,
            "filter_dates": {
                "start": str(start_date.date()),
                "end": str(end_date.date())
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    




# API: ADMIN-ONLY - STAFF PRODUCTIVITY REPORT (CARDS + LIST)
class AdminProductivityReportAPIView(APIView):
    """
    API endpoint for the Admin Dashboard to retrieve the consolidated staff productivity report and aggregated lead counts.
    The scope is limited to the Admin's subordinate Team Leaders and Staff (non-freelancer).
    """
   
    permission_classes = [IsAuthenticated, IsCustomAdminUser]

    def get(self, request, format=None):
        try:
            admin_instance = Admin.objects.get(self_user=request.user)
        except Admin.DoesNotExist:
            return Response({"error": "Admin profile not found."}, status=status.HTTP_404_NOT_FOUND)

        teamleader_id = request.query_params.get('teamleader_id')
        date_filter = request.query_params.get('date')
        end_date_str = request.query_params.get('endDate')

        today = timezone.now().date()
        start_date = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end_date = timezone.make_aware(datetime.combine(today, datetime.max.time()))
        filter_status = "Today (Default)"

        if date_filter and end_date_str:
            try:
                s_date = datetime.strptime(date_filter, '%Y-%m-%d')
                if isinstance(end_date_str, str):
                    e_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                else:
                    e_date = end_date_str
                
                start_date = timezone.make_aware(datetime.combine(s_date, datetime.min.time()))
                end_date = timezone.make_aware(e_date + timedelta(days=1)) - timedelta(seconds=1)
                filter_status = f"Custom: {start_date.date()} to {end_date.date()}"
            except ValueError:
                pass 

        update_filter = {'updated_date__range': [start_date, end_date]}
        create_filter = {'created_date__range': [start_date, end_date]}
        sell_filter = {'created_date__range': [start_date, end_date]} 

        staffs = Staff.objects.filter(
            team_leader__admin=admin_instance,
            user__user_active=True, 
            user__is_freelancer=False
        )

        # Optional: Filter by specific Team Leader
        if teamleader_id:
            staffs = staffs.filter(team_leader_id=teamleader_id)
        
        staff_data = []
        
        # Aggregates Initialization
        total_all_leads = 0
        total_all_interested = 0
        total_all_not_interested = 0
        total_all_other_location = 0
        total_all_not_picked = 0
        total_all_lost = 0
        total_all_visit = 0
        total_all_earning = 0.0

        for staff in staffs:
            # ---  Leads Calculation (LeadUser) ---
            staff_leads = LeadUser.objects.filter(assigned_to=staff)
            
            total = staff_leads.filter(status="Leads", **create_filter).count()
            visit = staff_leads.filter(status="Visit", **update_filter).count()
            interested = staff_leads.filter(status="Intrested", **update_filter).count()
            not_interested = staff_leads.filter(status="Not Interested", **update_filter).count()
            other_location = staff_leads.filter(status="Other Location", **update_filter).count()
            not_picked = staff_leads.filter(status="Not Picked", **update_filter).count()
            lost = staff_leads.filter(status="Lost", **update_filter).count()

            # ---  Earning Calculation (Sell_plot) ---
            earning_agg = Sell_plot.objects.filter(staff=staff, **sell_filter).aggregate(total=Sum('earn_amount'))
            total_earned_amount = earning_agg['total'] if earning_agg['total'] else 0.0

            staff_data.append({
                'id': staff.id,
                'name': staff.name,
                'team_leader': staff.team_leader.name if staff.team_leader else "N/A",
                'mobile': staff.mobile,
                'created_date': staff.created_date,
                'user_active': staff.user.user_active,
                
                'total_leads': total,
                'visit': visit,
                'interested': interested,
                'not_interested': not_interested,
                'other_location': other_location,
                'not_picked': not_picked,
                'lost': lost,
                'earn': total_earned_amount
            })

            total_all_leads += total
            total_all_visit += visit
            total_all_interested += interested
            total_all_not_interested += not_interested
            total_all_other_location += other_location
            total_all_not_picked += not_picked
            total_all_lost += lost
            try:
                total_all_earning += float(total_earned_amount)
            except ValueError:
                pass

        # Final Response Construction
        counts_data = {
            'total_leads': total_all_leads,
            'total_visit': total_all_visit,
            'interested': total_all_interested,
            'not_interested': total_all_not_interested,
            'other_location': total_all_other_location,
            'not_picked': total_all_not_picked,
            'lost_leads': total_all_lost,
            'total_earning': total_all_earning
        }

        setting = Settings.objects.filter().last()
        
        response_data = {
            'filter_status': filter_status,
            'counts': counts_data,      # Cards Data
            'staff_list': staff_data,   # Table Data
            'setting': DashboardSettingsSerializer(setting).data if setting else None,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)




# API: TEAM LEADER PRODUCTIVITY REPORT (FOR ADMIN/SUPERUSER)

class TeamLeaderProductivityViewAPIView(APIView):
    """
    API endpoint to retrieve the consolidated productivity report and lead activity summary aggregated by Team Leader.
    The report scope is restricted based on the logged-in user (Superuser sees all; Admin sees their reporting TLs).
    """
   
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Get Query Params
        date_filter = request.query_params.get('date')
        end_date_str = request.query_params.get('endDate')
        admin_id = request.query_params.get('admin_id')
        
        # Determine Team Leaders based on User Role
        team_leaders = Team_Leader.objects.none()
        
        if request.user.is_superuser:
            team_leaders = Team_Leader.objects.filter(user__user_active=True)
            if admin_id:
                team_leaders = team_leaders.filter(admin=admin_id)
        
        elif request.user.is_admin:
            try:
                
                team_leaders = Team_Leader.objects.filter(
                    admin__self_user=request.user, 
                    user__user_active=True
                )
                if admin_id:
                     # If admin tries to filter by another admin ID (should not happen for regular admin, but logic is there)
                     team_leaders = team_leaders.filter(admin=admin_id)
            except Exception:
                pass
        
        # If user is neither superuser nor admin, return empty or error
        elif not (request.user.is_superuser or request.user.is_admin):
             return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        # Date Filter Logic
        today = timezone.now().date()
        start_date = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end_date = timezone.make_aware(datetime.combine(today, datetime.max.time()))
        
        if date_filter:
            try:
                s_date = datetime.strptime(date_filter, '%Y-%m-%d')
                start_date = timezone.make_aware(datetime.combine(s_date, datetime.min.time()))
                
                if end_date_str:
                    e_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    end_date = timezone.make_aware(datetime.combine(e_date, datetime.max.time()))
                else:
                    end_date = timezone.make_aware(datetime.combine(s_date, datetime.max.time()))
            except ValueError:
                pass

        activity_filter = {'updated_date__range': [start_date, end_date]}
        creation_filter = {'created_date__range': [start_date, end_date]}

        # Aggregation Variables
        staff_data = [] # Actually team leader data list
        total_all_leads = 0
        total_all_interested = 0
        total_all_not_interested = 0
        total_all_other_location = 0
        total_all_not_picked = 0
        total_all_lost = 0
        total_all_visit = 0
        total_all_calls = 0

        for tl in team_leaders:
            # Initialize counters for this Team Leader
            tl_leads = 0
            tl_interested = 0
            tl_not_interested = 0
            tl_other_location = 0
            tl_not_picked = 0
            tl_lost = 0
            tl_visit = 0
            
            # Get Staff associated with this Team Leader
            staff_members = Staff.objects.filter(team_leader=tl)

            # Aggregate data from all staff under this TL
            for staff in staff_members:
                staff_leads = LeadUser.objects.filter(assigned_to=staff)
                
                tl_leads += staff_leads.filter(**creation_filter).count()
                tl_interested += staff_leads.filter(status="Intrested", **activity_filter).count()
                tl_not_interested += staff_leads.filter(status="Not Interested", **activity_filter).count()
                tl_other_location += staff_leads.filter(status="Other Location", **activity_filter).count()
                tl_not_picked += staff_leads.filter(status="Not Picked", **activity_filter).count()
                tl_lost += staff_leads.filter(status="Lost", **activity_filter).count()
                tl_visit += staff_leads.filter(status="Visit", **activity_filter).count()

            
            tl_total_calls = tl_interested + tl_not_interested + tl_other_location + tl_not_picked + tl_lost + tl_visit

            visit_percentage = (tl_visit / tl_leads * 100) if tl_leads > 0 else 0
            interested_percentage = (tl_interested / tl_leads * 100) if tl_leads > 0 else 0

            staff_data.append({
                'id': tl.id,
                'name': tl.name,
                'total_leads': tl_leads,
                'interested': tl_interested,
                'not_interested': tl_not_interested,
                'other_location': tl_other_location,
                'not_picked': tl_not_picked,
                'lost': tl_lost,
                'visit': tl_visit,
                'visit_percentage': round(visit_percentage, 2),
                'interested_percentage': round(interested_percentage, 2),
                'total_calls': tl_total_calls,
            })

            total_all_leads += tl_leads
            total_all_interested += tl_interested
            total_all_not_interested += tl_not_interested
            total_all_other_location += tl_other_location
            total_all_not_picked += tl_not_picked
            total_all_lost += tl_lost
            total_all_visit += tl_visit
            total_all_calls += tl_total_calls

        total_visit_percentage = (total_all_visit / total_all_leads * 100) if total_all_leads > 0 else 0
        total_interested_percentage = (total_all_interested / total_all_leads * 100) if total_all_leads > 0 else 0

        response_data = {
            "counts": {
                'total_all_leads': total_all_leads,
                'total_all_interested': total_all_interested,
                'total_all_not_interested': total_all_not_interested,
                'total_all_other_location': total_all_other_location,
                'total_all_not_picked': total_all_not_picked,
                'total_all_lost': total_all_lost,
                'total_all_visit': total_all_visit,
                'total_all_calls': total_all_calls,
                'total_visit_percentage': round(total_visit_percentage, 2),
                'total_interested_percentage': round(total_interested_percentage, 2),
                'total_team_leaders_count': team_leaders.count(),
            },
            "team_leader_data": staff_data, # Rename to clear confusion
            "filter_dates": {
                "start": str(start_date.date()),
                "end": str(end_date.date())
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


# API: ADMIN-ONLY - TOTAL LEADS (SELF/DIRECT)

class AdminTotalLeadsAPIView(APIView):
    """
    API endpoint for the Admin role to retrieve a paginated list of leads with status 'Leads' that are directly associated with the Admin user.
    """
 
    
    permission_classes = [IsAuthenticated, IsCustomAdminUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, format=None):
        paginator = self.pagination_class()
        
        
        leads_qs = LeadUser.objects.filter(
            status="Leads", 
            user=request.user
        ).order_by('-updated_date') # Default ordering

        # Paginate & Serialize
        page = paginator.paginate_queryset(leads_qs, request, view=self)
        
        if page is not None:
            serializer = ApiLeadUserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ApiLeadUserSerializer(leads_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



class AddSellFreelancerV2APIView(APIView):
    """
    API endpoint for a Team Leader to create a new sales record (SellPlot) for a subordinate Staff/Freelancer member.
    The Team Leader must manage the designated Staff member.
    """
   
    permission_classes = [IsAuthenticated, IsCustomTeamLeaderUser ]

    def post(self, request, id, format=None):
        """
        POST payload (JSON) example:
        {
          "project_name": "Project X",
          "project_location": "Site A",
          "description": "Sold plot",
          "size_in_gaj": "10",
          "plot_no": "P-123",
          "date": "2025-11-21",
          "staff_id": 21    
        }
        """
        # verify team leader profile exists
        team_leader = Team_Leader.objects.filter(email=request.user.email).last()
        if not team_leader:
            return Response({"detail": "Team leader profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Pass context so serializer can access request + view kwargs (id)
        serializer = SellPlotCreateSerializer(data=request.data, context={"request": request, "view": self})
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Additional ownership check: ensure staff belongs to this team leader
        # Get staff id used by serializer: prefer URL id unless it's 0
        used_staff_id = id if int(id) != 0 else request.data.get("staff_id")
        try:
            used_staff_id = int(used_staff_id)
        except Exception:
            return Response({"detail": "staff_id must be provided (integer) when url id is 0."}, status=status.HTTP_400_BAD_REQUEST)

        staff_instance = Staff.objects.filter(id=used_staff_id).last()
        if not staff_instance:
            return Response({"detail": f"Staff not found with id {used_staff_id}."}, status=status.HTTP_404_NOT_FOUND)

        if staff_instance.team_leader is None or staff_instance.team_leader.id != team_leader.id:
            return Response({"detail": "You can only create sell records for staff belonging to your own team."}, status=status.HTTP_403_FORBIDDEN)

        # create and return
        try:
            sell = serializer.save()
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        out = SellPlotSerializer(sell)
        return Response({"message": "Sell created", "sell": out.data}, status=status.HTTP_201_CREATED)
    




class AddLeadBySelfAPIView(APIView):
    """
    API endpoint that allows Staff, Team Leaders, Admins, and Superusers to manually create and submit a new lead. 
    The lead's assignment and hierarchy fields are automatically determined based on the creator's role.
    """
    
    permission_classes = [IsAuthenticated , IsCustomAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = LeadCreateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        # Determine context (staff/team leader/admin)
        try:
            if getattr(user, "is_staff_new", False):
                # Staff creates: must have Staff profile
                staff_instance = Staff.objects.filter(email=user.email).last()
                if not staff_instance:
                    return Response({'error': 'Staff profile not found for this user.'}, status=status.HTTP_400_BAD_REQUEST)

                # Create lead with assigned_to = staff_instance and team_leader from staff
                lead = serializer.save(
                    user=user,
                    team_leader=staff_instance.team_leader,
                    assigned_to=staff_instance
                )

            elif getattr(user, "is_team_leader", False):
                team_leader_instance = Team_Leader.objects.filter(email=user.email).last()
                if not team_leader_instance:
                    return Response({'error': 'Team Leader profile not found for this user.'}, status=status.HTTP_400_BAD_REQUEST)

                lead = serializer.save(
                    user=user,
                    team_leader=team_leader_instance
                )

            elif getattr(user, "is_admin", False) or getattr(user, "is_superuser", False):
                # Admin / superuser: create lead with user=request.user (no assigned_to)
                lead = serializer.save(user=user)

            else:
                # Other roles: deny or handle as needed
                return Response({'error': 'You do not have permission to create a lead via this endpoint.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        out = ApiLeadUserSerializer(lead, context={'request': request})
        return Response({'message': 'Lead created', 'data': out.data}, status=status.HTTP_201_CREATED)




# API: ADMIN-ONLY - LEAD HISTORY

class AdminLeadHistoryAPIView(APIView):
    """
    API endpoint for the Admin role to retrieve the full history of status changes for a specific lead.
    Access is restricted to leads that belong to the Admin's hierarchical network (subordinate Team Leaders and Staff).
    """
  
    permission_classes = [IsAuthenticated, IsCustomAdminUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, id, format=None):
        
        try:
            admin_profile = Admin.objects.get(self_user=request.user)
        except Admin.DoesNotExist:
            return Response({"error": "Admin profile not found."}, status=status.HTTP_404_NOT_FOUND)

        
        try:
            lead = LeadUser.objects.get(id=id)
            is_authorized = False
            
            # Case A: Lead is assigned to a Staff -> Staff ke TL -> TL ka Admin
            if lead.assigned_to and lead.assigned_to.team_leader and lead.assigned_to.team_leader.admin == admin_profile:
                is_authorized = True
                
            # Case B: Lead is assigned directly to a Team Leader -> TL ka Admin
            elif lead.team_leader and lead.team_leader.admin == admin_profile:
                is_authorized = True
                
            if not is_authorized:
                return Response({"error": "Permission denied. This lead does not belong to your network."}, status=status.HTTP_403_FORBIDDEN)

        except LeadUser.DoesNotExist:
            return Response({"error": "Lead not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get History
        history_qs = Leads_history.objects.filter(lead_id=id).order_by('-updated_date')

        # Paginate & Serialize
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(history_qs, request, view=self)
        
        if page is not None:
            serializer = LeadsHistorySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = LeadsHistorySerializer(history_qs, many=True)
        return Response(serializer.data)
    





class AdminLostLeadsAPIView(APIView):
    """
    API endpoint for the Admin role to retrieve a paginated list of 'Intrested' leads, filtered by follow-up date status.
    The list is restricted to leads within the Admin's hierarchical network (subordinate Team Leaders).
    """
    
    permission_classes = [IsAuthenticated, IsCustomAdminUser  ]

    def get(self, request, format=None):
        # ensure admin
        user = request.user
        admin_instance = Admin.objects.filter(self_user=user).last()
        if not admin_instance:
            return Response({"detail": "Admin profile not found for this user."}, status=status.HTTP_403_FORBIDDEN)

        tag = request.query_params.get('tag', '').strip()
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        qs = LeadUser.objects.filter(status="Intrested", team_leader__admin=admin_instance)

        if tag == 'pending_follow':
            qs = qs.filter(Q(follow_up_date__isnull=False)).order_by('-updated_date')
        elif tag == 'today_follow':
            qs = qs.filter(Q(follow_up_date=today)).order_by('-updated_date')
        elif tag == 'tommorrow_follow' or tag == 'tomorrow_follow':
            # allow both spellings just in case
            qs = qs.filter(Q(follow_up_date=tomorrow)).order_by('-updated_date')
        elif tag == '':
            # no tag provided: default listing (you can decide ordering)
            qs = qs.order_by('-updated_date')
        else:
            # invalid tag -> return 400 with allowed tags
            allowed = ['pending_follow', 'today_follow', 'tommorrow_follow']
            return Response({
                "detail": f"Invalid tag '{tag}'. Allowed tags: {allowed} or omit tag to get default list."
            }, status=status.HTTP_400_BAD_REQUEST)

        # pagination: reuse DRF's PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 50
        result_page = paginator.paginate_queryset(qs, request)

        serializer = ApiLeadUserSerializer(result_page, many=True, context={"request": request})
        return paginator.get_paginated_response({"leads": serializer.data})
    



class ChangeLeadStatusAPIView(APIView):
    """
    API endpoint for an Admin user to update the status, message, and follow-up details of any specific lead ID.
    """
   
    permission_classes = [IsAuthenticated, IsOnlyAdminUser]

    def post(self, request, lead_id=None):
        # Fetch lead (404 if not found)
        lead = get_object_or_404(LeadUser, id=lead_id)

        # Validate input
        serializer = LeadUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data

        # Apply updates
        status_val = data.get('status')
        message = data.get('message', None)
        follow_date = data.get('followDate', None)
        follow_time = data.get('followTime', None)

        if status_val is not None:
            lead.status = status_val
        if message is not None:
            lead.message = message
        if follow_date is not None:
            lead.follow_up_date = follow_date
        if follow_time is not None:
            lead.follow_up_time = follow_time

        lead.save()

        # Create ActivityLog (optional) - link to Admin profile if exists
        user = request.user
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        user_type = "Admin User"
        admin_instance = Admin.objects.filter(self_user=user).last()
        tagline = f"Lead({lead.name}) status changed to {lead.status} by admin [{user.email}]"
        ActivityLog.objects.create(
            admin=admin_instance,
            description=tagline,
            ip_address=ip,
            email=user.email,
            user_type=user_type,
            activity_type=f"Lead status changed to {lead.status}",
            name=user.name or user.username
        )

        out = {
            "id": lead.id,
            "name": lead.name,
            "status": lead.status,
            "message": lead.message,
            "follow_up_date": lead.follow_up_date,
            "follow_up_time": lead.follow_up_time,
        }
        return Response({"message": "Lead updated", "data": out}, status=status.HTTP_200_OK)






class AdminNotInterestedLeadsAPIView(APIView):
    """
    API endpoint for the Admin role to retrieve a complete list of leads marked as 'Not Interested' within their hierarchical network.
    """
   
    permission_classes = [IsAuthenticated, IsCustomAdminUser ]

    def get(self, request, format=None):
        # find admin profile for current user
        admin_profile = Admin.objects.filter(self_user=request.user).last()
        if not admin_profile:
            return Response({"detail": "Admin profile not found for this user."}, status=status.HTTP_404_NOT_FOUND)

        # queryset: leads where team_leader.admin == admin_profile and status == "Not Interested"
        leads_qs = LeadUser.objects.filter(status="Not Interested", team_leader__admin=admin_profile).order_by('-updated_date')

        serializer = ApiLeadUserSerializer(leads_qs, many=True, context={'request': request})
        return Response({"users_lead_lost": serializer.data}, status=status.HTTP_200_OK)  







class MaybeLeadsAPIView(APIView):
    """
    API endpoint for the Admin role to retrieve a complete list of leads marked with the status 'Other Location' (often treated as 'Maybe' leads).
    """
    
    permission_classes = [IsAuthenticated , IsCustomAdminUser ]

    def get(self, request, *args, **kwargs):
        user = request.user

        # Enforce admin-only access
        if not getattr(user, "is_admin", False):
            return Response(
                {"detail": "You do not have permission to access this resource."},
                status=status.HTTP_403_FORBIDDEN
            )

        # find admin profile related to this user
        admin_instance = Admin.objects.filter(self_user=user).last()
        if not admin_instance:
            return Response(
                {"detail": "Admin profile not found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        # fetch leads with status "Other Location" that belong to this admin
        leads_qs = LeadUser.objects.filter(status="Other Location", team_leader__admin=admin_instance).order_by('-updated_date')

        serializer = ApiLeadUserSerializer(leads_qs, many=True, context={'request': request})
        return Response({"leads": serializer.data}, status=status.HTTP_200_OK)
    




# Not Picked (Admin only)
class NotPickedAPIView(APIView):
    """
    API endpoint for the Admin role to retrieve a complete list of leads marked with the status 'Not Picked'.
    """
    permission_classes = [IsAuthenticated , IsCustomAdminUser ]

    def get(self, request):
        admin_instance = Admin.objects.filter(self_user=request.user).last()
        if not admin_instance:
            return Response({"detail": "Admin profile not found."}, status=status.HTTP_404_NOT_FOUND)
        leads = LeadUser.objects.filter(status="Not Picked", team_leader__admin=admin_instance).order_by('-updated_date')
        serializer = ApiLeadUserSerializer(leads, many=True)
        return Response({"leads": serializer.data}, status=status.HTTP_200_OK)




# lost (Lost) admin-only API (POST)
class LostAdminAPIView(APIView):
    """
    API endpoint for the Admin role to retrieve a complete list of leads marked with the status 'Lost'.
    """
    permission_classes = [IsAuthenticated, IsCustomAdminUser]

    def get(self, request):
        admin_obj = Admin.objects.filter(self_user=request.user).last()
        if not admin_obj:
            return Response({'error': 'Admin profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        qs = LeadUser.objects.filter(status="Lost", team_leader__admin=admin_obj).order_by('-updated_date')
        serializer = ApiLeadUserSerializer(qs, many=True)
        return Response({'lead_lost': serializer.data}, status=status.HTTP_200_OK)
    



class AdminExportStaffLeadsAPIView(APIView):
    """
    API endpoint for the Admin role to export filtered leads data to an Excel file (.xlsx).
    The export scope is restricted to the Admin's managed hierarchy (subordinate Team Leaders/Staff).
    """
  
    permission_classes = [IsAuthenticated, IsCustomAdminUser]

    def post(self, request, format=None):
        staff_id = request.data.get('staff_id')
        status_val = request.data.get('status')
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        all_interested = request.data.get('all_interested')

        try:
          
            admin_profile = Admin.objects.get(self_user=request.user)
            
            if str(all_interested) == "1":
                team_leaders = Team_Leader.objects.filter(admin=admin_profile)
                base_qs = LeadUser.objects.filter(team_leader__in=team_leaders, status="Intrested")
                staff_name = "All_Staff"
            else:
                if not staff_id:
                     return Response({"error": "Staff ID is required."}, status=status.HTTP_400_BAD_REQUEST)
                     
                staff = Staff.objects.get(id=staff_id)
                
              
                if not staff.team_leader:
                    return Response({
                        "error": "Permission denied.",
                        "reason": f"Staff '{staff.name}' (ID: {staff.id}) has NO Team Leader assigned."
                    }, status=status.HTTP_403_FORBIDDEN)

                
                if staff.team_leader.admin != admin_profile:
                    return Response({
                        "error": "Permission denied.",
                        "reason": f"Staff '{staff.name}' belongs to Admin '{staff.team_leader.admin.name}', but you are '{admin_profile.name}'."
                    }, status=status.HTTP_403_FORBIDDEN)
               
                
                base_qs = LeadUser.objects.filter(assigned_to=staff, status=status_val)
                staff_name = staff.name

        except (Admin.DoesNotExist, Staff.DoesNotExist) as e:
            return Response({"error": f"Invalid Data or Profile not found. Detail: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        
        try:
            s_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            e_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            start_date = timezone.make_aware(datetime.combine(s_date, datetime.min.time()))
            end_date = timezone.make_aware(datetime.combine(e_date, datetime.max.time()))
        except (ValueError, TypeError):
             return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)

        leads = base_qs.filter(updated_date__range=[start_date, end_date])

        data = []
        for lead in leads:
            assigned_name = lead.assigned_to.name if lead.assigned_to else "Unassigned"
            data.append({
                'Name': lead.name, 'Call': lead.call, 'Status': lead.status,
                'Staff Name': assigned_name, 'Message': lead.message,
                'Date': localtime(lead.updated_date).strftime('%Y-%m-%d %H:%M:%S'),
            })

        if not data:
             return Response({"message": "No data found for export."}, status=status.HTTP_404_NOT_FOUND)

        df = pd.DataFrame(data)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename_status = "Intrested" if str(all_interested) == "1" else status_val
        response['Content-Disposition'] = f'attachment; filename={staff_name}_{filename_status}_{s_date.strftime("%Y%m%d")}.xlsx'
        with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Leads')
        return response




class UniversalNotificationAPIView(APIView):
    """
    API endpoint to retrieve recent activity logs/notifications for the authenticated user.
    The scope of notifications is determined dynamically by the user's role (Superuser, Admin, Team Leader, or Staff).
    """
   
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        notifications = ActivityLog.objects.none() # Default empty

        # SUPERUSER 
        if user.is_superuser:
            notifications = ActivityLog.objects.all().order_by('-created_date')[:50]

        # ADMIN 
        elif user.is_admin:
            try:
                
                admin_profile = Admin.objects.get(self_user=user)
                
                notifications = ActivityLog.objects.filter(admin=admin_profile).order_by('-created_date')[:50]
            except Admin.DoesNotExist:
                pass

        # TEAM LEADER 
        elif user.is_team_leader:
            try:
                
                tl_profile = Team_Leader.objects.get(user=user)
               
                notifications = ActivityLog.objects.filter(team_leader=tl_profile).order_by('-created_date')[:50]
            except Team_Leader.DoesNotExist:
                pass

        # STAFF 
        elif user.is_staff_new:
            
            notifications = ActivityLog.objects.filter(email=user.email).order_by('-created_date')[:50]

        # --- Response ---
        if notifications.exists():
            serializer = NotificationSerializer(notifications, many=True)
            return Response({
                "count": notifications.count(),
                "notifications": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "count": 0,
                "message": "No new notifications.",
                "notifications": []
            }, status=status.HTTP_200_OK)
    
    
class TodayInterestedCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = localtime(now()).date()

        interested_leads = LeadUser.objects.none()  # default empty queryset

        # SUPERUSER
        if request.user.is_superuser:
            interested_leads = LeadUser.objects.filter(
                status='Intrested',
                follow_up_date=today
            )

        # TEAM LEADER
        elif getattr(request.user, "is_team_leader", False):
            interested_leads = LeadUser.objects.filter(
                team_leader__user=request.user,
                status='Intrested',
                follow_up_date=today
            )

        # ADMIN
        elif getattr(request.user, "is_admin", False):
            interested_leads = LeadUser.objects.filter(
                team_leader__admin__self_user=request.user,
                status='Intrested',
                follow_up_date=today
            )

        # STAFF
        elif getattr(request.user, "is_staff_new", False):
            interested_leads = LeadUser.objects.filter(
                assigned_to__user=request.user,
                status='Intrested',
                follow_up_date=today
            )

        # Prepare payload
        leads_data = list(interested_leads.values('name', 'follow_up_time'))

        data = {
            "count": interested_leads.count(),
            "leads": leads_data
        }

        return Response(data)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def department_members(request):
    user = request.user

    # ---------------------------
    # STAFF VIEW
    # ---------------------------
    if user.role == "staff":
        staff = Staff.objects.filter(user=user).first()
        if not staff or not staff.team_leader:
            return Response(
                {"members": []},
                status=status.HTTP_200_OK
            )

        team_leader = staff.team_leader

    # ---------------------------
    # TEAM LEADER VIEW
    # ---------------------------
    elif user.role == "team_leader":
        team_leader = Team_Leader.objects.filter(user=user).first()
        if not team_leader:
            return Response(
                {"members": []},
                status=status.HTTP_200_OK
            )

    # ---------------------------
    # ADMIN / SUPER USER
    # ---------------------------
    else:
        return Response(
            {"members": []},
            status=status.HTTP_200_OK
        )

    members = Staff.objects.filter(team_leader=team_leader).select_related("user")

    present = 0
    result = []

    for member in members:
        status_today = today_attendance_status(member.user)
        if status_today in ["Present", "Checked In"]:
            present += 1

        result.append({
            "name": member.name or member.user.username,
            "status": status_today,
            "profile_image": (
                member.user.profile_image.url
                if member.user.profile_image else None
            )
        })

    department = member.user.profile.department if member.user.profile else None

    return Response({
        "department": department,
        "summary": {
            "present": present,
            "total": members.count()
        },
        "members": result
    })

def today_attendance_status(user):
    today = timezone.localtime(timezone.now()).date()

    att = Attendance.objects.filter(user=user, date=today).first()

    if not att:
        return "Yet to check-in"

    if att.check_in and att.check_out:
        return "Present"

    if att.check_in and not att.check_out:
        return "Checked In"

    return "Yet to check-in"


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporting_to(request):
    user = request.user

    # ---------------------------
    # STAFF USER
    # ---------------------------
    if user.role == "staff":
        staff = Staff.objects.filter(user=user).first()
        if not staff or not staff.team_leader:
            return Response(
                {"reporting_to": None},
                status=status.HTTP_200_OK
            )

        leader = staff.team_leader
        leader_user = leader.user

        return Response({
            "reporting_to": {
                "name": leader.name or leader_user.username,
                "designation": "Team Leader",
                "status": today_attendance_status(leader_user),
                "profile_image": (
                    leader_user.profile_image.url
                    if leader_user.profile_image else None
                )
            }
        })

    # ---------------------------
    # TEAM LEADER / ADMIN
    # ---------------------------
    return Response(
        {"reporting_to": None},
        status=status.HTTP_200_OK
    )



def can_view_profile(request_user, target_user):
    # Superuser / Admin → full access
    if request_user.is_superuser or request_user.role == "admin":
        return True

    # Staff → only self
    if request_user.role == "staff":
        return request_user == target_user

    # Team leader → self + own staff
    if request_user.role == "team_leader":
        return Staff.objects.filter(
            user=target_user,
            team_leader__user=request_user
        ).exists() or request_user == target_user

    return False

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile_overview(request, staff_id):
    # -------------------------------------------------
    # 1. Staff → User → Profile
    # -------------------------------------------------
    staff = get_object_or_404(Staff, staff_id=staff_id)
    user = staff.user
    profile = user.profile

    # -------------------------------------------------
    # 2. LEAVE CALCULATION
    # -------------------------------------------------
    YEAR = date.today().year

    TOTAL_SICK = 12
    TOTAL_CASUAL = 12

    sick_used = Leave.objects.filter(
        user=user,
        leave_type="Sick",
        status="Approved",
        start_date__year=YEAR
    ).count()

    casual_used = Leave.objects.filter(
        user=user,
        leave_type="Casual",
        status="Approved",
        start_date__year=YEAR
    ).count()

    total_used = sick_used + casual_used

    # -------------------------------------------------
    # 3. RESPONSE
    # -------------------------------------------------
    return Response({
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "profile_image": user.profile_image.url if user.profile_image else None
        },

        "contact_info": {
            "full_name": profile.full_name,
            "email": user.email,   # ✅ Always from User
            "phone": profile.phone,
            "department": profile.department,
            "designation": profile.designation,
            "join_date": profile.join_date,
            "reports_to": profile.reports_to,
            "address": profile.address
        },

        "skills_education": {
            "education": profile.education,
            "skills": profile.skill_list()
        },

        # ✅ NEW BLOCK
        "leave_status": {
            "sick": {
                "used": sick_used,
                "total": TOTAL_SICK
            },
            "casual": {
                "used": casual_used,
                "total": TOTAL_CASUAL
            },
            "total": {
                "used": total_used,
                "total": TOTAL_SICK + TOTAL_CASUAL
            }
        }
    })



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def profile_update(request):
    """
    Update contact info / skills / education
    for the LOGGED-IN USER only
    """
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    # -------------------------
    # Allowed fields only
    # -------------------------
    allowed_fields = [
        "full_name",
        "phone",
        "address",
        "education",
        "skills",
    ]

    for field in allowed_fields:
        if field in request.data:
            value = request.data.get(field)

            # skills may come as list from frontend
            if field == "skills" and isinstance(value, list):
                value = ", ".join(value)

            setattr(profile, field, value)

    profile.save()

    return Response(
        {"message": "Profile updated successfully"},
        status=status.HTTP_200_OK
    )


class IsSuperuserOrAdminOrTeamLeader(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and (
                request.user.is_superuser or
                getattr(request.user, "is_admin", False) or
                getattr(request.user, "is_team_leader", False)
            )
        )

class AddFreelancerAPIView(APIView):
    """
    API to add Freelancer or IT Staff.
    Access:
    - Superuser → selects admin → auto team leader
    - Admin → selects team leader
    - Team Leader → auto assigned
    """
    permission_classes = [IsSuperuserOrAdminOrTeamLeader]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        serializer = AddFreelancerSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            staff_instance = serializer.save()

            # -------- Activity Log --------
            try:
                if request.user.is_superuser:
                    user_type = "Super User"
                elif getattr(request.user, "is_admin", False):
                    user_type = "Admin User"
                else:
                    user_type = "Team Leader"

                ip = request.META.get(
                    'HTTP_X_FORWARDED_FOR',
                    request.META.get('REMOTE_ADDR')
                )

                admin_log = None
                if getattr(request.user, "is_admin", False):
                    admin_log = Admin.objects.filter(
                        self_user=request.user
                    ).last()

                ActivityLog.objects.create(
                    admin=admin_log,
                    user=request.user if request.user.is_superuser else None,
                    description=f"New Freelancer/Staff ({staff_instance.name}) added by {user_type}",
                    ip_address=ip,
                    email=request.user.email,
                    user_type=user_type,
                    activity_type="Freelancer Created",
                    name=request.user.name
                )
            except Exception:
                pass

            return Response(
                {
                    "message": "Profile created successfully. Please wait for review.",
                    "data": StaffProfileSerializer(staff_instance).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
