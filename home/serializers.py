from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import *
from django.contrib.auth import get_user_model
from .models import Admin
# Yeh line file ke sabse upar add karo
from django.db import IntegrityError
from .models import Project

class UserSerializer(serializers.ModelSerializer):
    """ user serializer """

    token_detail = serializers.SerializerMethodField("get_token_detail")
    class Meta:
        model = User 
        fields = ('id', 'username', 'name', 'email', 'mobile', 'profile_image','is_superuser', 'is_admin', 'is_team_leader', 'is_staff_new', 'is_freelancer', 'role', 'login_time', 'logout_time', 'token_detail',)
        extra_kwargs = {
            'token_detail': {'read_only': True}
        }
        
    def get_token_detail(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key

    def get_user(self, request):
        user = request
        return user
    
class StaffAssignedSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadUser
        fields = ('id', 'user', 'team_leader', 'assigned_to', 'name', 'email', 'call', 'status', 'message', 'created_date', 'updated_date', )

class LeadUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadUser
        fields = '__all__'

class MarketingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketing
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class LeadsHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Leads_history
        fields = '__all__'

class TeamLeadDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team_LeadData
        fields = '__all__'

class StaffProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Staff
        fields = [

            'id' ,'user_id', 'name', 'email', 'mobile', 'address', 'city', 'pincode', 'state',
            'dob', 'pancard', 'aadharCard', 'marksheet', 'degree', 'account_number',
            'upi_id', 'bank_name', 'ifsc_code', 'salary', 'achived_slab',
            'referral_code', 'join_referral', 'created_date', 'updated_date'
        ]
        read_only_fields = ['referral_code', 'created_date', 'updated_date']

class MarketingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketing
        fields = ['id', 'user', 'source', 'message', 'media_file', 'url']
        read_only_fields = ['id', 'user']

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'

class SellPlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sell_plot
        fields = [
            'id', 'admin', 'team_leader', 'staff', 'project_name', 
            'project_location', 'description', 'size_in_gaj', 
            'plot_no', 'earn_amount', 'slab', 'slab_amount', 
            'date', 'created_date', 'updated_date'
        ]


class ProductivityDataSerializer(serializers.Serializer):
    day = serializers.IntegerField()
    day_name = serializers.CharField()
    leads = serializers.IntegerField()
    salary = serializers.FloatField()

class StructuredCalendarDataSerializer(serializers.Serializer):
    day = serializers.IntegerField()
    day_name = serializers.CharField()

class AdminSerializer(serializers.ModelSerializer):
  
    user = UserSerializer(read_only=True)

    class Meta:
        model = Admin
        fields = ['id', 'user'] 




# ==========================================================
# NAYE SUPER-USER DASHBOARD KE LIYE NAYE SERIALIZERS
# ==========================================================

class DashboardUserSerializer(serializers.ModelSerializer):
   
    profile_image = serializers.FileField(use_url=True, allow_null=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'mobile', 'profile_image', 
            'is_admin', 'is_team_leader', 'is_staff_new' , 'created_date', 
            'user_active'   
        ]

class DashboardAdminSerializer(serializers.ModelSerializer):
    
    user = DashboardUserSerializer(read_only=True, source='self_user')

    class Meta:
        model = Admin
       
        fields = [
            'id','user_id' , 'user', 'admin_id', 'name', 'email', 'mobile', 
            'address', 'city', 'pincode', 'state', 'dob', 'pancard', 
            'aadharCard', 'account_number', 'upi_id', 'bank_name', 
            'ifsc_code', 'salary', 'achived_slab' , 'created_date'
        ]

class DashboardSettingsSerializer(serializers.ModelSerializer):
    
    logo = serializers.FileField(use_url=True)

    class Meta:
        model = Settings
        fields = ['id', 'logo']





# ==========================================================
# ADMIN SIDE LEADS RECORD KE LIYE NAYE SERIALIZERS
# ==========================================================

class ApiStaffSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Staff
        fields = ['id', 'name', 'staff_id', 'email', 'mobile']


class ApiLeadUserSerializer(serializers.ModelSerializer):
    assigned_to = ApiStaffSerializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(source='project', read_only=True)
    project = ProjectSerializer(read_only=True)
    team_leader = serializers.CharField(source='team_leader.name', read_only=True)
    follow_up_date = serializers.DateField(format="%Y-%m-%d", allow_null=True)
    follow_up_time = serializers.TimeField(format="%H:%M:%S", allow_null=True)

    class Meta:
        model = LeadUser
        fields = [
            'id', 'name', 'email', 'call', 'send', 'status', 'message', 'team_leader',
            'follow_up_date', 'follow_up_time', 'created_date', 'assigned_to',
            'project_id', 'project'
        ]




class ApiTeamLeadDataSerializer(serializers.ModelSerializer):
   
    assigned_to = ApiStaffSerializer(read_only=True)

    class Meta:
        model = Team_LeadData
        fields = [
            'id', 'name', 'email', 'call', 'send', 'status', 'message', 
            'created_date', 'assigned_to'
        ]



# ==========================================================
# ATTENDANCE CALENDAR API SERIALIZER [FINAL FIX]
# ==========================================================

class AttendanceCalendarDaySerializer(serializers.Serializer):
   
    date = serializers.DateField()
    has_task = serializers.BooleanField()
    day_name = serializers.CharField(max_length=10)
    
    status = serializers.CharField(max_length=10) 
    status_color = serializers.CharField(max_length=10)


# STAFF PRODUCTIVITY API SERIALIZERS
class ProductivityTeamLeaderSerializer(serializers.ModelSerializer):
    
    admin_name = serializers.ReadOnlyField(source='admin.name')
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    
    class Meta:
        model = Team_Leader
        depth = 1
     
        fields = [
            'id',
            'user_id', 
            'admin',
            'user',                        
            'admin_name',     
            'name', 
            'email', 
            'mobile', 
            'address', 
            'city', 
            'state', 
            'pincode', 
            'dob', 
            'pancard', 
            'aadharCard', 
            'account_number',
            'upi_id',
            'bank_name',
            'ifsc_code',
            'salary', 
            'achived_slab',
            'profile_image',  
        ]
class StaffProductivityDataSerializer(serializers.Serializer):
    
    id = serializers.IntegerField()
    name = serializers.CharField()
    total_leads = serializers.IntegerField()
    interested = serializers.IntegerField()
    not_interested = serializers.IntegerField()
    other_location = serializers.IntegerField()
    not_picked = serializers.IntegerField()
    lost = serializers.IntegerField()
    visit = serializers.IntegerField()
    visit_percentage = serializers.FloatField()
    interested_percentage = serializers.FloatField()
    total_calls = serializers.IntegerField()



# ==========================================================
# ADMIN ADD API SERIALIZER
# ==========================================================
class AdminCreateSerializer(serializers.ModelSerializer):
    """
    Serializer naya Admin User aur Admin Profile banane ke liye.
    """
    
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    profile_image = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Admin
        
        fields = [
            'name', 'email', 'mobile', 'password', 'profile_image',
            'address', 'city', 'state', 'pincode', 'dob', 'pancard', 
            'aadharCard', 'marksheet', 'degree', 'account_number', 
            'upi_id', 'bank_name', 'ifsc_code', 'salary'
        ]
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate_email(self, value):
      
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email Already Exists")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username (Email) Already Exists")
        return value

    def create(self, validated_data):
        
        creator_user = self.context['request'].user
        
        password = validated_data.pop('password')
        profile_image = validated_data.pop('profile_image', None)
        email = validated_data.get('email')
        name = validated_data.get('name')
        mobile = validated_data.get('mobile')

        try:
            new_user = User.objects.create(
                username=email,
                email=email,
                profile_image=profile_image,
                name=name,
                mobile=mobile,
                is_admin=True  
            )
            new_user.set_password(password)
            new_user.save()
        except IntegrityError as e:
            raise serializers.ValidationError(f"Error creating user: {e}")
        
        try:
           
            admin = Admin.objects.create(
                user=creator_user,      
                self_user=new_user,     
                **validated_data
            )
        except IntegrityError as e:
           
            new_user.delete()
            raise serializers.ValidationError(f"Error creating admin profile: {e}")

        return admin
    

class AdminUpdateSerializer(serializers.ModelSerializer):
    
    profile_image = serializers.FileField(required=False, allow_null=True, write_only=True)
    
    password = serializers.CharField(
        write_only=True, 
        required=False, 
        style={'input_type': 'password'}
    )

    class Meta:
        model = Admin
        fields = [
            'name', 'email', 'mobile', 'address', 'city', 'state', 'pincode', 
            'dob', 'pancard', 'aadharCard', 'marksheet', 'degree', 
            'account_number', 'upi_id', 'bank_name', 'ifsc_code', 'salary',
            'profile_image', 'password' 
        ]
        extra_kwargs = {
            'email': {'required': False}
        }

    def update(self, instance, validated_data):
        
        profile_image = validated_data.pop('profile_image', None)
        password = validated_data.pop('password', None) # Password nikaal liya
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if profile_image:
            instance.profile_image = profile_image
            
        instance.save()
        
        # --- User Table Update & Password Change ---
        user = instance.user
        if user:
            # Basic details sync karo
            user.email = validated_data.get('email', user.email)
            user.username = validated_data.get('email', user.username) # Email hi username hai
            user.name = validated_data.get('name', user.name)
            user.mobile = validated_data.get('mobile', user.mobile)
            
            if profile_image:
                user.profile_image = profile_image
            
            # IMPORTANT: Password Change Logic
            if password:
                user.set_password(password) # Password hash karke save karega
                
            user.save()
            
        return instance
    

# ==========================================================
# STAFF ADD API SERIALIZER [FIXED]
# ==========================================================
class StaffCreateSerializer(serializers.ModelSerializer):
   
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    profile_image = serializers.FileField(required=False, allow_null=True)
    team_leader = serializers.PrimaryKeyRelatedField(queryset=Team_Leader.objects.all(), required=True)

    class Meta:
        model = Staff
        fields = [
            'team_leader', 'name', 'email', 'mobile', 'password', 'profile_image',
            'address', 'city', 'state', 'pincode', 'dob', 'pancard', 
            'aadharCard', 'marksheet', 'degree', 'account_number', 
            'upi_id', 'bank_name', 'ifsc_code', 'salary'
        ]
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email Already Exists")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username (Email) Already Exists")
        return value

    def create(self, validated_data):
        
        password = validated_data.pop('password')
        profile_image = validated_data.pop('profile_image', None)
        email = validated_data.get('email')
        name = validated_data.get('name')
        mobile = validated_data.get('mobile')

        
        try:
            new_user = User.objects.create_user(
                username=email, email=email, password=password,
                profile_image=profile_image, name=name,
                mobile=mobile, is_staff_new=True
            )
        except IntegrityError as e:
            raise serializers.ValidationError(f"Error creating user: {e}")
        
        
        try:
            staff = Staff.objects.create(
                user=new_user,
                **validated_data
            )
            
            
            request = self.context['request']
            user_type = ""
            if request.user.is_superuser: user_type = "Super User"
            elif request.user.is_admin: user_type = "Admin User"
            elif request.user.is_team_leader: user_type = "Team leader User"
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            
            tagline = f"staff : {staff.name} created by user[Email : {request.user.email}, {user_type}]"
            tag2 = f"staff : {staff.name} created"

            if request.user.is_team_leader:
                
                team_leader_instance = Team_Leader.objects.get(user=request.user)
                my_user1 = team_leader_instance.admin
               
                ActivityLog.objects.create(
                    admin=my_user1, description=tagline, ip_address=ip,
                    email=request.user.email, user_type=user_type, activity_type=tag2, name=request.user.name
                )
            elif request.user.is_admin:
                
                admin_instance = Admin.objects.filter(self_user=request.user).last() 
                ActivityLog.objects.create(
                    admin=admin_instance, 
                    description=tagline, 
                    ip_address=ip,
                    email=request.user.email, 
                    user_type=user_type, 
                    activity_type=tag2, 
                    name=request.user.name
                )    
            elif request.user.is_superuser:
                 ActivityLog.objects.create(
                    user=request.user, description=tagline, ip_address=ip,
                    email=request.user.email, user_type=user_type, activity_type=tag2, name=request.user.name
                )
            
        except Exception as e:
            new_user.delete()
            raise serializers.ValidationError(f"Error creating staff profile: {e}")

        return staff
    



# ==========================================================
# TEAM LEADER ADD API SERIALIZER [FINAL FIX]
# ==========================================================
class TeamLeaderCreateSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    profile_image = serializers.FileField(required=False, allow_null=True)
    admin_id = serializers.IntegerField(write_only=True, required=False) 

    # User ke roles
    # on_boarding_manager = serializers.BooleanField(required=False)
    # dsr_manager = serializers.BooleanField(required=False)
    # executive_manager = serializers.BooleanField(required=False)
    # delivery_manager = serializers.BooleanField(required=False)

    class Meta:
        model = Team_Leader
        fields = [
            'name', 'email', 'mobile', 'password', 'profile_image',
            'address', 'city', 'state', 'pincode', 'dob', 'pancard', 
            'aadharCard', 'marksheet', 'degree', 'account_number', 
            'upi_id', 'bank_name', 'ifsc_code', 'salary',
            'admin_id'
        ]
        extra_kwargs = {'email': {'required': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email Already Exists")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username (Email) Already Exists")
        return value

    def create(self, validated_data):
        # 1. Data separation
        password = validated_data.pop('password')
        profile_image = validated_data.pop('profile_image', None)
        admin_id = validated_data.pop('admin_id', None)
        
        # on_boarding_manager = validated_data.pop('on_boarding_manager', False)
        # dsr_manager = validated_data.pop('dsr_manager', False)
        # executive_manager = validated_data.pop('executive_manager', False)
        # delivery_manager = validated_data.pop('delivery_manager', False)
        
        email = validated_data.get('email')
        name = validated_data.get('name')
        mobile = validated_data.get('mobile')
        request = self.context['request']

        
        admin_obj = None
        current_user = request.user
        
        if current_user.is_superuser:
           
            if admin_id:
                try:
                    admin_obj = Admin.objects.get(id=int(admin_id))
                except (Admin.DoesNotExist, ValueError):
                    raise serializers.ValidationError({"admin_id": "Admin profile not found with this ID or ID is invalid."})

        elif current_user.is_admin:
           
            admin_obj = Admin.objects.filter(self_user=current_user).last()
            
        if not admin_obj:
       
            raise serializers.ValidationError({"admin": "Admin profile is required and could not be determined."})

        try:
            new_user = User.objects.create_user(
                username=email, email=email, password=password,
                profile_image=profile_image, name=name, mobile=mobile, 
                is_team_leader=True,
                # on_boarding_manager=on_boarding_manager,
                # dsr_manager=dsr_manager, executive_manager=executive_manager, 
                # delivery_manager=delivery_manager
            )
        except IntegrityError as e:
            raise serializers.ValidationError(f"Error creating user: {e}")
        
        try:
            team_leader = Team_Leader.objects.create(
                admin=admin_obj, 
                user=new_user,
                **validated_data
            )
            
           
            user_type = ""
            if current_user.is_superuser: user_type = "Super User"
            elif current_user.is_admin: user_type = "Admin User"
            
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            tagline = f"Team Lead({name}) created by user[Email : {current_user.email}, {user_type}]"
            tag2 = f"Team Lead({name}) created"
            
            if current_user.is_superuser:
                 ActivityLog.objects.create(
                    user=current_user, description=tagline, ip_address=ip, email=current_user.email,
                    user_type=user_type, activity_type=tag2, name=current_user.name
                )
            elif current_user.is_admin:
                ActivityLog.objects.create(
                    admin=admin_obj, 
                    description=tagline, ip_address=ip, email=current_user.email,
                    user_type=user_type, activity_type=tag2, name=current_user.name
                )
            
        except Exception as e:
            new_user.delete()
            raise serializers.ValidationError({"non_field_errors": f"Error creating team leader profile: {e}"})

        return team_leader
    





# ==========================================================
# TEAM LEADER EDIT/UPDATE API SERIALIZER
# ==========================================================
class TeamLeaderUpdateSerializer(serializers.ModelSerializer):
  
    profile_image = serializers.FileField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Team_Leader
        fields = [
            'name', 'email', 'mobile', 'address', 'city', 'pincode', 'state',
            'dob', 'pancard', 'aadharCard', 'marksheet', 'degree',
            'account_number', 'upi_id', 'bank_name', 'ifsc_code', 'salary',
            'profile_image' 
        ]
        extra_kwargs = {
            'email': {'required': False}, 
            'name': {'required': False}
        }

    def update(self, instance, validated_data):
        
        profile_image = validated_data.pop('profile_image', None)

        team_leader_instance = super().update(instance, validated_data)
        
        user_instance = team_leader_instance.user
        
        if user_instance:
           
            user_instance.email = validated_data.get('email', user_instance.email)
            user_instance.username = validated_data.get('email', user_instance.username) 
            user_instance.name = validated_data.get('name', user_instance.name)
            user_instance.mobile = validated_data.get('mobile', user_instance.mobile)
            
            if profile_image:
                user_instance.profile_image = profile_image
            
            user_instance.save()
        
        return team_leader_instance
    

# ==========================================================
# STAFF EDIT (FREELANCER EDIT) API SERIALIZERS
# ==========================================================

class FullStaffSerializer(serializers.ModelSerializer):
    """
    Staff/Freelancer ki poori profile (GET request ke liye)
    """
    user = DashboardUserSerializer(read_only=True) 
    team_leader = ProductivityTeamLeaderSerializer(read_only=True) 

    class Meta:
        model = Staff
        fields = '__all__' 


class StaffUpdateSerializer(serializers.ModelSerializer):
    
    profile_image = serializers.FileField(required=False, allow_null=True, write_only=True)
    team_leader_id = serializers.IntegerField(write_only=True, required=False)
    
    # Password field add ki hai (write_only)
    password = serializers.CharField(
        write_only=True, 
        required=False, 
        style={'input_type': 'password'}
    )

    class Meta:
        model = Staff
        fields = [
            'name', 'email', 'mobile', 'address', 'city', 'pincode', 'state',
            'dob', 'pancard', 'aadharCard', 'marksheet', 'degree', 
            'account_number', 'upi_id', 'bank_name', 'ifsc_code', 'salary',
            'profile_image', 'team_leader_id', 'password' # <-- Password yahan add kiya
        ]
        extra_kwargs = {
            'email': {'required': False}, 
            'name': {'required': False}
        }

    def update(self, instance, validated_data):
        profile_image = validated_data.pop('profile_image', None)
        team_leader_id = validated_data.pop('team_leader_id', None)
        
        # Password nikaal lo
        password = validated_data.pop('password', None)

        staff_instance = super().update(instance, validated_data)
        
        if team_leader_id:
            try:
                new_team_leader = Team_Leader.objects.get(id=team_leader_id)
                staff_instance.team_leader = new_team_leader
                staff_instance.save()
            except Team_Leader.DoesNotExist:
                pass 
        
        # --- User Model Update Logic ---
        user_instance = staff_instance.user
        if user_instance:
            user_instance.email = validated_data.get('email', user_instance.email)
            user_instance.username = validated_data.get('email', user_instance.username)
            user_instance.name = validated_data.get('name', user_instance.name)
            user_instance.mobile = validated_data.get('mobile', user_instance.mobile)
            
            if profile_image:
                user_instance.profile_image = profile_image
            
            # Agar password bheja hai to update karo
            if password:
                user_instance.set_password(password)
            
            user_instance.save()
        
        return staff_instance
    





# SLAB SERIALIZER

class SlabSerializer(serializers.ModelSerializer):
    """
    Serializer for Slab model data.
    """
    class Meta:
        model = Slab
        fields = '__all__'    



# ==========================================================
# STAFF PRODUCTIVITY CALENDAR SERIALIZER
# ==========================================================

class DailyProductivitySerializer(serializers.Serializer):
   
    day = serializers.IntegerField()
    date = serializers.DateField()
    day_name = serializers.CharField(max_length=10)
    leads = serializers.IntegerField()
    salary = serializers.FloatField()






# ==========================================================
# SERIALIZER: LEAD EXPORT [FIXED VARIABLE NAME]
# ==========================================================
class LeadExportSerializer(serializers.Serializer):
 
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    
    all_interested = serializers.CharField(required=False, allow_blank=True, max_length=10)
    staff_id = serializers.IntegerField(required=False, allow_null=True)
    
   
    lead_status = serializers.CharField(required=False, allow_blank=True, max_length=100) 

    def validate(self, data):
      
        all_interested = data.get('all_interested')
        
        if all_interested != "1":
            if not data.get('staff_id'):
                raise serializers.ValidationError({"staff_id": "This field is required when not exporting 'all_interested'."})
            
            
            if not data.get('lead_status'):
                raise serializers.ValidationError({"lead_status": "This field is required when not exporting 'all_interested'."})
        
        return data
    

# ==========================================================
# NAYA SERIALIZER: SIMPLE TEAM LEADER (SIRF FLAT DATA KE LIYE)
# ==========================================================
class SimpleTeamLeaderSerializer(serializers.ModelSerializer):
    """
    Serializer jo Team Leader ki flat details dikhata hai (bina nested user/admin ke).
    """
    class Meta:
        model = Team_Leader
        
        fields = [
            'id', 'team_leader_id', 'name', 'email', 'mobile', 
            'address', 'city', 'pincode', 'state', 'dob', 'pancard', 
            'aadharCard', 'account_number', 'upi_id', 'bank_name', 
            'ifsc_code', 'salary', 'achived_slab', 'created_date' 
        ]
        read_only_fields = ['created_date']    
    




# ==========================================================
# API: ADD SELL PLOT (FREELANCER) SERIALIZER
# ==========================================================

class SellPlotCreateSerializer(serializers.ModelSerializer):
   
    staff_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Sell_plot
       
        fields = [
            'project_name', 
            'project_location', 
            'description', 
            'size_in_gaj', 
            'plot_no', 
            'date',
            'staff_id',
        ]
        
        extra_kwargs = {
            'date': {'required': True}
        }

    def validate_size_in_gaj(self, value):
       
        try:
            int(value or 0)
        except ValueError:
            raise serializers.ValidationError("Size (Gaj) must be a valid number.")
        
        if int(value or 0) <= 0:
            raise serializers.ValidationError("Size (Gaj) must be greater than 0.")
        
        return value 


    def create(self, validated_data):
      
        view_id = self.context['request'].parser_context['kwargs']['id']
        staff_id_from_post = validated_data.pop('staff_id', None)
        
        user_instance = None
        if view_id != 0:
            user_instance = Staff.objects.filter(id=view_id).last()
        else:
            user_instance = Staff.objects.filter(id=staff_id_from_post).last()

        if not user_instance:
            raise serializers.ValidationError({"staff_id": f"Staff not found."})
        
       
        team_leader_insatnce = user_instance.team_leader
        if not team_leader_insatnce:
            raise serializers.ValidationError({"team_leader": f"Team Leader not found for staff {user_instance.name}."})
        
        admin_instance = team_leader_insatnce.admin
        if not admin_instance:
            raise serializers.ValidationError({"admin": f"Admin not found for team leader {team_leader_insatnce.name}."})

    
        size_in_gaj_str = validated_data.get('size_in_gaj')
        size_in_gaj_int = int(size_in_gaj_str or 0)

       
        staff_slab = user_instance.achived_slab
        update_staff_slab = int(staff_slab or 0) + size_in_gaj_int
        user_instance.achived_slab = update_staff_slab
        user_instance.save()

       
        team_lead_slab = team_leader_insatnce.achived_slab
        update_staff_slab1 = int(team_lead_slab or 0) + size_in_gaj_int
        team_leader_insatnce.achived_slab = update_staff_slab1
        team_leader_insatnce.save()

        
        admin_slab = admin_instance.achived_slab
        update_staff_slab2 = int(admin_slab or 0) + size_in_gaj_int
        admin_instance.achived_slab = update_staff_slab2
        admin_instance.save()

        current_slab = int(user_instance.achived_slab or 0)
        slabs = Slab.objects.all()

        slab_amount = 0
        myslab = "N/A"
        current_slab_amount = 0

        for slab in slabs:
            start_value = int(slab.start_value or 0)
            if slab.end_value is not None:
                end_value = int(slab.end_value or 0)
                if start_value <= current_slab <= end_value:
                    slab_amount_base = int(slab.amount or 0)
                    if user_instance.user.is_freelancer:
                        slab_amount = slab_amount_base * size_in_gaj_int
                    
                   
                    elif user_instance.user.is_staff_new: 
                        slab_amount = (slab_amount_base - 100) * size_in_gaj_int
                    
                    myslab = f"{start_value}-{end_value}"
                    current_slab_amount = slab_amount_base
                    break
            else:
                if current_slab >= start_value:
                    slab_amount_base = int(slab.amount or 0)
                    if user_instance.user.is_freelancer:
                        slab_amount = slab_amount_base * size_in_gaj_int
                    
                    
                    elif user_instance.user.is_staff_new:
                        slab_amount = (slab_amount_base - 100) * size_in_gaj_int
                    
                    myslab = f"{start_value}+"
                    current_slab_amount = slab_amount_base
                    break
        
       
        sell = Sell_plot.objects.create(
            admin=admin_instance,
            team_leader=team_leader_insatnce,
            staff=user_instance,
            earn_amount=slab_amount,
            slab=myslab,
            slab_amount=current_slab_amount,
            **validated_data  
        )
        return sell



# ==========================================================
# LEAD UPDATE (STATUS/MESSAGE) API SERIALIZER
# ==========================================================
class LeadUpdateSerializer(serializers.Serializer):
 
    status = serializers.CharField(max_length=100, required=True)
    message = serializers.CharField(required=False, allow_blank=True)
    followDate = serializers.DateField(required=False, allow_null=True)
    followTime = serializers.TimeField(required=False, allow_null=True)




# ==========================================================
# API: STAFF-ONLY - ADD NEW LEAD (BY SELF)
# ==========================================================
class StaffLeadCreateSerializer(serializers.ModelSerializer):

    
    
    mobile = serializers.CharField(source='call', required=True)
   
    description = serializers.CharField(source='message', allow_blank=True, required=False)

    class Meta:
        model = LeadUser
        
        fields = [
            'name', 
            'email', 
            'mobile',  
            'status', 
            'description' 
        ]

    def validate_mobile(self, value):
      
        if LeadUser.objects.filter(call=value).exists():
            raise serializers.ValidationError("Mobile number already exists.")
        return value

    def create(self, validated_data):
       
        user = self.context['request'].user

        try:
            staff_instance = Staff.objects.get(email=user.email)
        except Staff.DoesNotExist:
            raise serializers.ValidationError("Staff profile not found for this user.")
        
        if not staff_instance.team_leader:
             raise serializers.ValidationError("Staff is not assigned to any Team Leader.")

        validated_data['user'] = user
        validated_data['assigned_to'] = staff_instance
        validated_data['team_leader'] = staff_instance.team_leader

        lead = LeadUser.objects.create(**validated_data)
        return lead    
class ApiUserSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)
  

    class Meta:
        model = User
        fields = [
            'id', 'username', 'name', 'email', 'mobile',
            'is_team_leader', 'is_staff_new', 'is_admin',
            'is_active', 'duration', 'login_time', 'logout_time',
            'profile_image', 'user_active', 'is_user_login'
        ]

    def get_duration(self, obj):
        return obj.duration  

# ==========================================================
# NAYA SERIALIZER: STAFF PROFILE (BINA TEAMLEADER KE)
# ==========================================================
class StaffOnlyProfileSerializer(serializers.ModelSerializer):
    
    user = DashboardUserSerializer(read_only=True) 

    class Meta:
        model = Staff
        
        fields = [
            'id', 'user', 'staff_id', 'name', 'email', 'mobile', 
            'address', 'city', 'pincode', 'state', 'dob', 'pancard', 
            'aadharCard', 'marksheet', 'degree', 'account_number', 
            'upi_id', 'bank_name', 'ifsc_code', 'salary', 'achived_slab',
            'referral_code', 'join_referral', 'created_date', 'updated_date'
        ]


# ==========================================================
# SUPERUSER PROFILE & SETTINGS SERIALIZERS
# ==========================================================

class SuperUserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Superuser profile update.
    """
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'mobile', 'profile_image']

class DashboardSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for Global Settings (Logo).
    """
    class Meta:
        model = Settings
        fields = ['id', 'logo']


class TeamLeaderAddStaffSerializer(serializers.ModelSerializer):
  
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    profile_image = serializers.ImageField(required=False)

    class Meta:
        model = Staff
       
        fields = [
            'name', 'email', 'password', 'mobile', 'address', 'city', 'state', 'pincode',
            'dob', 'pancard', 'aadharCard', 'marksheet', 'degree', 'account_number',
            'upi_id', 'bank_name', 'ifsc_code', 'salary', 'profile_image'
        ]

    def validate_email(self, value):
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email Already Exists")
        return value

    def create(self, validated_data):
        
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
       
        user = User.objects.create_user(
            username=email, 
            email=email, 
            password=password, 
            name=validated_data.get('name'),
            mobile=validated_data.get('mobile'),
            is_staff_new=True, 
            profile_image=validated_data.get('profile_image')
        )
        
        request = self.context.get('request')
        team_leader_instance = Team_Leader.objects.get(user=request.user)

        staff = Staff.objects.create(
            user=user, 
            email=email, 
            team_leader=team_leader_instance, 
            **validated_data
        )
        return staff
    



class LeadForDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadUser
        fields = '__all__' 




# ==========================================================
# API: TEAM-LEADER - ADD NEW LEAD (BY SELF) SERIALIZER
# ==========================================================
class TeamLeaderLeadCreateSerializer(serializers.ModelSerializer):

    mobile = serializers.CharField(write_only=True, required=False, allow_blank=True)
    description = serializers.CharField(source='message', write_only=True, required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = LeadUser
        # We only accept minimal fields from client
        fields = ('id', 'name', 'email', 'mobile', 'status', 'description')

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required.")
        return value.strip()

    def create(self, validated_data):
     
        mobile = validated_data.pop('mobile', '') or ''
        message = validated_data.pop('message', '')  
        
        team_leader = self.context.get('team_leader') or self._kwargs.get('team_leader') if hasattr(self, '_kwargs') else None
        user = self.context.get('request').user if self.context.get('request') else None

        extra_kwargs = {}
     
        lead = LeadUser.objects.create(
            user = user,
            team_leader = team_leader,
            name = validated_data.get('name', ''),
            email = validated_data.get('email', ''),
            call = mobile,
            message = message,
            status = validated_data.get('status', '')
        )
        return lead




class LeadCreateSerializer(serializers.ModelSerializer):

    mobile = serializers.CharField(write_only=True, required=False, allow_blank=True)
    description = serializers.CharField(source='message', write_only=True, required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = LeadUser
        fields = ('id', 'name', 'email', 'mobile', 'status', 'description')

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required.")
        return value.strip()

    def create(self, validated_data):
        
        mobile = validated_data.pop('mobile', '') or ''
        message = validated_data.pop('message', '')  

        team_leader = self.context.get('team_leader', None)
        user = self.context.get('request').user if self.context.get('request') else None

        lead = LeadUser.objects.create(
            user = user,
            team_leader = team_leader,
            name = validated_data.get('name', ''),
            email = validated_data.get('email', ''),
            call = mobile,
            message = message,
            status = validated_data.get('status', '')
        )
        return lead

# ==========================================================
# TEAM LEADER PROFILE SERIALIZER
# ==========================================================
class TeamLeaderProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Team Leader Profile View.
    Shows TL details and User details.
    """
    user = DashboardUserSerializer(read_only=True)
    
    class Meta:
        model = Team_Leader
        fields = [
            'id', 'user', 'team_leader_id', 'name', 'email', 'mobile',
            'address', 'city', 'pincode', 'state', 'dob', 
            'created_date', 'updated_date'
        ]




# ==========================================================
# SUPERUSER PROFILE SERIALIZERS
# ==========================================================

class SuperUserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Superuser profile update (User model).
    """
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'mobile', 'profile_image', 'username']
        read_only_fields = ['username'] # Username change nahi hoga (email se sync hoga)

class DashboardSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for Global Settings (Logo).
    """
    class Meta:
        model = Settings
        fields = ['id', 'logo']



# ==========================================================
# ADMIN PROFILE SERIALIZER
# ==========================================================
class AdminProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Admin Profile View.
    Shows Admin details and User details.
    """
    user = DashboardUserSerializer(read_only=True)
    
    class Meta:
        model = Admin
        fields = [
            'id', 'user', 'admin_id', 'name', 'email', 'mobile',
            'address', 'city', 'pincode', 'state', 'dob', 'pancard',
            'aadharCard', 'account_number', 'upi_id', 'bank_name', 'ifsc_code',
            'created_date'
        ]




class ActivityLogMinimalSerializer(serializers.ModelSerializer):
    
    description = serializers.CharField(source='description', read_only=True)
    activity_type = serializers.CharField(source='activity_type', read_only=True)
    user_type = serializers.CharField(source='user_type', read_only=True)

    # Format created_date exactly like template (example: "Nov. 21, 2025, 7:19 a.m.")
    created_date = serializers.DateTimeField(format="%b. %d, %Y, %I:%M %p", read_only=True)

    class Meta:
        model = ActivityLog
       
        fields = ['name', 'description', 'activity_type', 'user_type', 'created_date']





class TeamLeaderUpdateSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(source='user.email', required=False)
    # Password field add ki hai (write_only taki response me wapas na dikhe)
    password = serializers.CharField(
        write_only=True, 
        required=False, 
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = Team_Leader
        fields = [
            'name', 'email', 'mobile', 'address', 'city', 'state', 'pincode',
            'dob', 'pancard', 'aadharCard', 'profile_image', 'password' # <-- Password yahan add kiya
        ]

    def update(self, instance, validated_data):
        
        # User se related data nikaal lo
        user_data = validated_data.pop('user', {})
        # Password alag se nikaal lo
        password = validated_data.pop('password', None)
        email = user_data.get('email')

        # --- Team Leader Fields Update ---
        instance.name = validated_data.get('name', instance.name)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.address = validated_data.get('address', instance.address)
        instance.city = validated_data.get('city', instance.city)
        instance.state = validated_data.get('state', instance.state)
        instance.pincode = validated_data.get('pincode', instance.pincode)
        instance.dob = validated_data.get('dob', instance.dob)
        instance.pancard = validated_data.get('pancard', instance.pancard)
        instance.aadharCard = validated_data.get('aadharCard', instance.aadharCard)

        # Note: Yahan 'profile_image' ka naam wahi rakhna jo tumhare model me hai
        if 'profile_image' in validated_data:
            instance.profile_image = validated_data['profile_image']

        instance.save()

        # --- User Model Update ---
        user = instance.user
        
        # 1. Email Update Check
        if email and user.email != email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                raise serializers.ValidationError({"email": "Email already exists."})
            user.email = email
            user.username = email 
        
        # 2. Name & Mobile Update (User model me bhi sync kar rhe ho to)
        user.name = instance.name
        user.mobile = instance.mobile
        
        # 3. PASSWORD CHANGE LOGIC (Ye naya hai)
        if password:
            user.set_password(password) # Password ko hash karke set karega
            
        user.save()

        return instance
    


    

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notifications (Activity Logs).
    """
    class Meta:
        model = ActivityLog
        fields = ['id', 'name', 'user_type', 'activity_type', 'description', 'created_date']
