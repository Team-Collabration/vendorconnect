from rest_framework import serializers
from django.contrib.auth import authenticate,get_user_model
from orders.models import  VendorProfile, SupplierProfile
import math
User = get_user_model()
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    business_name = serializers.CharField(write_only=True)
    business_type = serializers.CharField(write_only=True, required=False)
    gst_number = serializers.CharField(write_only=True, required=False)
    pan_number = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm', 'user_type',
            'phone_number', 'address', 'city', 'state', 'pincode',
            'business_name', 'business_type', 'gst_number', 'pan_number'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        password_confirm = validated_data.pop('password_confirm')
        business_name = validated_data.pop('business_name')
        business_type = validated_data.pop('business_type', '')
        gst_number = validated_data.pop('gst_number', '')
        pan_number = validated_data.pop('pan_number', '')
        
        # Ensure username uniqueness (derive a unique variant if taken)
        base_username = (validated_data.get('username') or '').strip()
        if base_username:
            candidate = base_username
            suffix = 1
            while User.objects.filter(username__iexact=candidate).exists():
                candidate = f"{base_username}{suffix}"
                suffix += 1
            validated_data['username'] = candidate
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create profile based on user type
        if user.user_type == 'vendor':
            VendorProfile.objects.create(
                user=user,
                business_name=business_name,
                business_type=business_type,
                gst_number=gst_number,
                pan_number=pan_number
            )
        elif user.user_type == 'supplier':
            SupplierProfile.objects.create(
                user=user,
                business_name=business_name,
                business_type=business_type,
                gst_number=gst_number,
                pan_number=pan_number
            )
        
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Allow email or username; fall back to manual password check
            from .models import User
            user = None
            try:
                if '@' in username:
                    user = User.objects.filter(email__iexact=username).first()
                if user is None:
                    user = User.objects.filter(username__iexact=username).first()
                if user and not user.check_password(password):
                    user = None
            except Exception:
                user = None
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password')
        
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    vendor_profile = serializers.SerializerMethodField()
    supplier_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'user_type', 'phone_number',
            'address', 'city', 'state', 'pincode', 'latitude', 'longitude',
            'is_verified', 'profile_picture', 'created_at', 'updated_at',
            'vendor_profile', 'supplier_profile'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_vendor_profile(self, obj):
        if hasattr(obj, 'vendor_profile'):
            return {
                'business_name': obj.vendor_profile.business_name,
                'business_type': obj.vendor_profile.business_type,
                'gst_number': obj.vendor_profile.gst_number,
                'pan_number': obj.vendor_profile.pan_number,
                'preferred_supply_schedule': obj.vendor_profile.preferred_supply_schedule,
            }
        return None
    
    def get_supplier_profile(self, obj):
        if hasattr(obj, 'supplier_profile'):
            return {
                'business_name': obj.supplier_profile.business_name,
                'business_type': obj.supplier_profile.business_type,
                'gst_number': obj.supplier_profile.gst_number,
                'pan_number': obj.supplier_profile.pan_number,
                'delivery_radius': obj.supplier_profile.delivery_radius,
                'minimum_order_amount': obj.supplier_profile.minimum_order_amount,
                'delivery_charge': obj.supplier_profile.delivery_charge,
            }
        return None

class VendorProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = VendorProfile
        fields = '__all__'

    def get_distance_km(self, obj):
        lat = self.context.get('lat')
        lng = self.context.get('lng')
        if lat is None or lng is None:
            return None
        try:
            user_lat = float(obj.user.latitude)
            user_lng = float(obj.user.longitude)
            return round(self._haversine(float(lat), float(lng), user_lat, user_lng), 2)
        except (TypeError, ValueError):
            return None

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

class SupplierProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = SupplierProfile
        fields = '__all__'

    def get_distance_km(self, obj):
        lat = self.context.get('lat')
        lng = self.context.get('lng')
        if lat is None or lng is None:
            return None
        try:
            user_lat = float(obj.user.latitude)
            user_lng = float(obj.user.longitude)
            return round(self._haversine(float(lat), float(lng), user_lat, user_lng), 2)
        except (TypeError, ValueError):
            return None

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
