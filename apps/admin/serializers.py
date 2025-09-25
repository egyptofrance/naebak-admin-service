"""
Serializers لخدمة الإدارة - مشروع نائبك
تحويل النماذج إلى JSON للـ APIs
"""
from rest_framework import serializers
from django.contrib.auth.models import Permission
from apps.admin.models import (
    Governorate, Party, ComplaintType, AdminRole, AdminUser,
    AdminActivity, SystemSettings, AdminDashboard, AdminSettings
)


class GovernorateSerializer(serializers.ModelSerializer):
    """Serializer للمحافظات"""
    
    users_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Governorate
        fields = [
            'id', 'name', 'name_en', 'code', 'region', 'capital',
            'area_km2', 'population', 'is_active', 'display_order',
            'users_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PartySerializer(serializers.ModelSerializer):
    """Serializer للأحزاب السياسية"""
    
    members_count = serializers.ReadOnlyField()
    candidates_count = serializers.ReadOnlyField()
    current_members_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Party
        fields = [
            'id', 'name', 'name_en', 'abbreviation', 'description',
            'founded_date', 'headquarters', 'website', 'logo', 'color',
            'is_active', 'display_order', 'members_count', 'candidates_count',
            'current_members_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ComplaintTypeSerializer(serializers.ModelSerializer):
    """Serializer لأنواع الشكاوى"""
    
    complaints_count = serializers.ReadOnlyField()
    resolution_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = ComplaintType
        fields = [
            'id', 'name', 'name_en', 'description', 'category', 'target_council',
            'icon', 'color', 'priority_level', 'estimated_resolution_days',
            'requires_attachments', 'max_attachments', 'is_active', 'is_public',
            'display_order', 'complaints_count', 'resolution_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer للصلاحيات"""
    
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']


class AdminRoleSerializer(serializers.ModelSerializer):
    """Serializer للأدوار الإدارية"""
    
    permissions = PermissionSerializer(many=True, read_only=True)
    users_count = serializers.ReadOnlyField()
    
    class Meta:
        model = AdminRole
        fields = [
            'id', 'name', 'name_en', 'role_type', 'description',
            'permissions', 'is_active', 'is_system_role',
            'users_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer للمستخدمين الإداريين"""
    
    admin_roles = AdminRoleSerializer(many=True, read_only=True)
    governorate = GovernorateSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    is_account_locked = serializers.ReadOnlyField()
    
    class Meta:
        model = AdminUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'employee_id', 'department', 'position',
            'admin_roles', 'governorate', 'profile_picture', 'bio',
            'is_active', 'is_staff', 'is_superuser', 'last_login',
            'last_activity', 'failed_login_attempts', 'is_account_locked',
            'two_factor_enabled', 'date_joined'
        ]
        read_only_fields = [
            'last_login', 'date_joined', 'last_activity',
            'failed_login_attempts', 'is_account_locked'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """إنشاء مستخدم إداري جديد"""
        password = validated_data.pop('password', None)
        user = AdminUser.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """Serializer لإنشاء مستخدم إداري"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = AdminUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone_number', 'employee_id', 'department', 'position',
            'governorate', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        """التحقق من تطابق كلمات المرور"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("كلمات المرور غير متطابقة")
        return attrs
    
    def create(self, validated_data):
        """إنشاء مستخدم إداري جديد"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = AdminUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AdminActivitySerializer(serializers.ModelSerializer):
    """Serializer لسجل النشاطات الإدارية"""
    
    admin_user = serializers.StringRelatedField(read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = AdminActivity
        fields = [
            'id', 'admin_user', 'action_type', 'action_type_display',
            'action_description', 'content_type', 'object_id',
            'ip_address', 'user_agent', 'old_values', 'new_values',
            'additional_data', 'timestamp', 'duration_ms',
            'is_successful', 'error_message'
        ]
        read_only_fields = ['timestamp']


class SystemSettingsSerializer(serializers.ModelSerializer):
    """Serializer لإعدادات النظام"""
    
    typed_value = serializers.ReadOnlyField(source='get_typed_value')
    setting_type_display = serializers.CharField(source='get_setting_type_display', read_only=True)
    
    class Meta:
        model = SystemSettings
        fields = [
            'id', 'key', 'name', 'description', 'setting_type',
            'setting_type_display', 'value', 'typed_value', 'default_value',
            'is_public', 'is_editable', 'is_required', 'validation_rules',
            'category', 'display_order', 'updated_by', 'updated_at', 'created_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AdminDashboardSerializer(serializers.ModelSerializer):
    """Serializer لودجتات لوحة التحكم"""
    
    admin_user = serializers.StringRelatedField(read_only=True)
    widget_type_display = serializers.CharField(source='get_widget_type_display', read_only=True)
    
    class Meta:
        model = AdminDashboard
        fields = [
            'id', 'admin_user', 'widget_type', 'widget_type_display',
            'widget_title', 'widget_config', 'position_x', 'position_y',
            'width', 'height', 'is_visible', 'refresh_interval',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AdminSettingsSerializer(serializers.ModelSerializer):
    """Serializer لإعدادات الإدارة"""
    
    updated_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = AdminSettings
        fields = [
            'id', 'max_login_attempts', 'account_lockout_duration',
            'session_timeout', 'password_expiry_days', 'require_two_factor',
            'allow_concurrent_sessions', 'log_all_activities',
            'enable_ip_whitelist', 'allowed_ip_addresses',
            'auto_backup_enabled', 'backup_frequency_hours',
            'backup_retention_days', 'email_notifications_enabled',
            'sms_notifications_enabled', 'notification_email',
            'max_records_per_page', 'cache_timeout_minutes',
            'enable_query_optimization', 'default_report_format',
            'include_charts_in_reports', 'updated_by', 'updated_at'
        ]
        read_only_fields = ['updated_at']


# Serializers للإحصائيات والتقارير
class AdminStatsSerializer(serializers.Serializer):
    """Serializer لإحصائيات الإدارة"""
    
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    total_complaints = serializers.IntegerField()
    pending_complaints = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    total_ratings = serializers.IntegerField()
    system_health = serializers.CharField()
    last_backup = serializers.DateTimeField()


class GovernorateStatsSerializer(serializers.Serializer):
    """Serializer لإحصائيات المحافظات"""
    
    governorate_name = serializers.CharField()
    users_count = serializers.IntegerField()
    complaints_count = serializers.IntegerField()
    messages_count = serializers.IntegerField()
    ratings_count = serializers.IntegerField()


class PartyStatsSerializer(serializers.Serializer):
    """Serializer لإحصائيات الأحزاب"""
    
    party_name = serializers.CharField()
    members_count = serializers.IntegerField()
    candidates_count = serializers.IntegerField()
    current_members_count = serializers.IntegerField()
    average_rating = serializers.FloatField()


class ComplaintTypeStatsSerializer(serializers.Serializer):
    """Serializer لإحصائيات أنواع الشكاوى"""
    
    complaint_type_name = serializers.CharField()
    total_complaints = serializers.IntegerField()
    resolved_complaints = serializers.IntegerField()
    pending_complaints = serializers.IntegerField()
    resolution_rate = serializers.FloatField()
    average_resolution_time = serializers.FloatField()


class ActivityLogSerializer(serializers.Serializer):
    """Serializer لسجل النشاطات المبسط"""
    
    timestamp = serializers.DateTimeField()
    admin_user = serializers.CharField()
    action = serializers.CharField()
    description = serializers.CharField()
    ip_address = serializers.IPAddressField()
    is_successful = serializers.BooleanField()
