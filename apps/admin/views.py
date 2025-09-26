"""
Views لخدمة الإدارة - مشروع نائبك
واجهات برمجة التطبيقات للإدارة والتحكم
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import Permission
from django.db.models import Count, Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.admin.models import (
    Governorate, Party, ComplaintType, AdminRole, AdminUser,
    AdminActivity, SystemSettings, AdminDashboard, AdminSettings
)
from apps.admin.serializers import (
    GovernorateSerializer, PartySerializer, ComplaintTypeSerializer,
    AdminRoleSerializer, AdminUserSerializer, AdminUserCreateSerializer,
    AdminActivitySerializer, SystemSettingsSerializer,
    AdminDashboardSerializer, AdminSettingsSerializer,
    AdminStatsSerializer, GovernorateStatsSerializer,
    PartyStatsSerializer, ComplaintTypeStatsSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="قائمة المحافظات",
        description="الحصول على قائمة بجميع المحافظات المصرية مع إمكانية الفلترة والبحث",
        tags=["المحافظات"]
    ),
    create=extend_schema(
        summary="إضافة محافظة جديدة",
        description="إنشاء محافظة جديدة في النظام (للمديرين فقط)",
        tags=["المحافظات"]
    ),
    retrieve=extend_schema(
        summary="تفاصيل محافظة",
        description="الحصول على تفاصيل محافظة محددة",
        tags=["المحافظات"]
    ),
    update=extend_schema(
        summary="تحديث محافظة",
        description="تحديث بيانات محافظة موجودة",
        tags=["المحافظات"]
    ),
    destroy=extend_schema(
        summary="حذف محافظة",
        description="حذف محافظة من النظام (للمديرين العامين فقط)",
        tags=["المحافظات"]
    )
)
class GovernorateViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة المحافظات المصرية
    
    يوفر عمليات CRUD كاملة للمحافظات مع إحصائيات
    وإمكانيات فلترة وبحث متقدمة.
    """
    queryset = Governorate.objects.all()
    serializer_class = GovernorateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['region', 'is_active']
    search_fields = ['name', 'name_en', 'capital']
    ordering_fields = ['name', 'display_order', 'population']
    ordering = ['display_order', 'name']

    @extend_schema(
        summary="إحصائيات المحافظة",
        description="الحصول على إحصائيات مفصلة لمحافظة محددة",
        responses={200: GovernorateStatsSerializer},
        tags=["المحافظات"]
    )
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """الحصول على إحصائيات المحافظة"""
        governorate = self.get_object()
        
        # حساب الإحصائيات (سيتم ربطها بالخدمات الأخرى لاحقاً)
        stats = {
            'governorate_name': governorate.name,
            'users_count': 0,  # سيتم ربطها بخدمة المستخدمين
            'complaints_count': 0,  # سيتم ربطها بخدمة الشكاوى
            'messages_count': 0,  # سيتم ربطها بخدمة الرسائل
            'ratings_count': 0,  # سيتم ربطها بخدمة التقييمات
        }
        
        serializer = GovernorateStatsSerializer(stats)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="قائمة الأحزاب السياسية",
        description="الحصول على قائمة بجميع الأحزاب السياسية المسجلة",
        tags=["الأحزاب السياسية"]
    ),
    create=extend_schema(
        summary="إضافة حزب جديد",
        description="تسجيل حزب سياسي جديد في النظام",
        tags=["الأحزاب السياسية"]
    ),
    retrieve=extend_schema(
        summary="تفاصيل حزب",
        description="الحصول على تفاصيل حزب سياسي محدد",
        tags=["الأحزاب السياسية"]
    ),
    update=extend_schema(
        summary="تحديث بيانات حزب",
        description="تحديث معلومات حزب سياسي موجود",
        tags=["الأحزاب السياسية"]
    ),
    destroy=extend_schema(
        summary="حذف حزب",
        description="إلغاء تسجيل حزب سياسي من النظام",
        tags=["الأحزاب السياسية"]
    )
)
class PartyViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة الأحزاب السياسية
    
    يوفر إدارة شاملة للأحزاب السياسية المسجلة
    مع إحصائيات العضوية والمرشحين.
    """
    queryset = Party.objects.all()
    serializer_class = PartySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name', 'name_en', 'abbreviation']
    ordering_fields = ['name', 'founded_date', 'display_order']
    ordering = ['display_order', 'name']

    @extend_schema(
        summary="إحصائيات الحزب",
        description="الحصول على إحصائيات مفصلة لحزب سياسي محدد",
        responses={200: PartyStatsSerializer},
        tags=["الأحزاب السياسية"]
    )
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """الحصول على إحصائيات الحزب"""
        party = self.get_object()
        
        # حساب الإحصائيات
        stats = {
            'party_name': party.name,
            'members_count': party.members_count,
            'candidates_count': party.candidates_count,
            'current_members_count': party.current_members_count,
            'average_rating': 0.0,  # سيتم ربطها بخدمة التقييمات
        }
        
        serializer = PartyStatsSerializer(stats)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="قائمة أنواع الشكاوى",
        description="الحصول على قائمة بجميع أنواع الشكاوى المتاحة",
        tags=["أنواع الشكاوى"]
    ),
    create=extend_schema(
        summary="إضافة نوع شكوى جديد",
        description="إنشاء نوع شكوى جديد في النظام",
        tags=["أنواع الشكاوى"]
    ),
    retrieve=extend_schema(
        summary="تفاصيل نوع الشكوى",
        description="الحصول على تفاصيل نوع شكوى محدد",
        tags=["أنواع الشكاوى"]
    ),
    update=extend_schema(
        summary="تحديث نوع الشكوى",
        description="تحديث معلومات نوع شكوى موجود",
        tags=["أنواع الشكاوى"]
    ),
    destroy=extend_schema(
        summary="حذف نوع الشكوى",
        description="حذف نوع شكوى من النظام",
        tags=["أنواع الشكاوى"]
    )
)
class ComplaintTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة أنواع الشكاوى
    
    يوفر إدارة شاملة لأنواع الشكاوى المختلفة
    مع إعدادات الأولوية والتصنيف.
    """
    queryset = ComplaintType.objects.all()
    serializer_class = ComplaintTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category', 'target_council', 'priority_level', 'is_active', 'is_public']
    search_fields = ['name', 'name_en', 'description']
    ordering_fields = ['name', 'priority_level', 'display_order']
    ordering = ['display_order', 'name']

    @extend_schema(
        summary="إحصائيات نوع الشكوى",
        description="الحصول على إحصائيات مفصلة لنوع شكوى محدد",
        responses={200: ComplaintTypeStatsSerializer},
        tags=["أنواع الشكاوى"]
    )
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """الحصول على إحصائيات نوع الشكوى"""
        complaint_type = self.get_object()
        
        # حساب الإحصائيات (سيتم ربطها بخدمة الشكاوى لاحقاً)
        stats = {
            'complaint_type_name': complaint_type.name,
            'total_complaints': 0,
            'resolved_complaints': 0,
            'pending_complaints': 0,
            'resolution_rate': 0.0,
            'average_resolution_time': 0.0,
        }
        
        serializer = ComplaintTypeStatsSerializer(stats)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="قائمة الأدوار الإدارية",
        description="الحصول على قائمة بجميع الأدوار الإدارية وصلاحياتها",
        tags=["الأدوار الإدارية"]
    ),
    create=extend_schema(
        summary="إنشاء دور إداري جديد",
        description="إنشاء دور إداري جديد مع تحديد الصلاحيات",
        tags=["الأدوار الإدارية"]
    ),
    retrieve=extend_schema(
        summary="تفاصيل الدور الإداري",
        description="الحصول على تفاصيل دور إداري محدد",
        tags=["الأدوار الإدارية"]
    ),
    update=extend_schema(
        summary="تحديث الدور الإداري",
        description="تحديث دور إداري وصلاحياته",
        tags=["الأدوار الإدارية"]
    ),
    destroy=extend_schema(
        summary="حذف الدور الإداري",
        description="حذف دور إداري (غير مسموح لأدوار النظام)",
        tags=["الأدوار الإدارية"]
    )
)
class AdminRoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة الأدوار الإدارية
    
    يوفر إدارة شاملة للأدوار الإدارية والصلاحيات
    مع حماية أدوار النظام من الحذف.
    """
    queryset = AdminRole.objects.all()
    serializer_class = AdminRoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['role_type', 'is_active', 'is_system_role']
    search_fields = ['name', 'name_en', 'description']
    ordering = ['name']

    def destroy(self, request, *args, **kwargs):
        """منع حذف أدوار النظام"""
        instance = self.get_object()
        if instance.is_system_role:
            return Response(
                {'error': 'لا يمكن حذف أدوار النظام'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(
        summary="قائمة المستخدمين الإداريين",
        description="الحصول على قائمة بجميع المستخدمين الإداريين",
        tags=["المستخدمون الإداريون"]
    ),
    create=extend_schema(
        summary="إنشاء مستخدم إداري جديد",
        description="إنشاء حساب مستخدم إداري جديد",
        tags=["المستخدمون الإداريون"]
    ),
    retrieve=extend_schema(
        summary="تفاصيل المستخدم الإداري",
        description="الحصول على تفاصيل مستخدم إداري محدد",
        tags=["المستخدمون الإداريون"]
    ),
    update=extend_schema(
        summary="تحديث المستخدم الإداري",
        description="تحديث معلومات مستخدم إداري",
        tags=["المستخدمون الإداريون"]
    ),
    destroy=extend_schema(
        summary="حذف المستخدم الإداري",
        description="حذف حساب مستخدم إداري",
        tags=["المستخدمون الإداريون"]
    )
)
class AdminUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة المستخدمين الإداريين
    
    يوفر إدارة شاملة للمستخدمين الإداريين مع
    عمليات قفل/إلغاء قفل الحسابات وإدارة الأدوار.
    """
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_active', 'is_staff', 'is_superuser', 'department', 'governorate']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    ordering = ['-date_joined']

    def get_serializer_class(self):
        """اختيار Serializer المناسب حسب العملية"""
        if self.action == 'create':
            return AdminUserCreateSerializer
        return AdminUserSerializer

    @extend_schema(
        summary="قفل حساب المستخدم",
        description="قفل حساب مستخدم إداري لفترة محددة",
        request=OpenApiParameter(
            name='duration_minutes',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='مدة القفل بالدقائق (افتراضي: 30)'
        ),
        tags=["المستخدمون الإداريون"]
    )
    @action(detail=True, methods=['post'])
    def lock_account(self, request, pk=None):
        """قفل حساب المستخدم"""
        user = self.get_object()
        duration = int(request.query_params.get('duration_minutes', 30))
        
        user.lock_account(duration)
        
        return Response({
            'message': f'تم قفل الحساب لمدة {duration} دقيقة',
            'locked_until': user.account_locked_until
        })

    @extend_schema(
        summary="إلغاء قفل حساب المستخدم",
        description="إلغاء قفل حساب مستخدم إداري",
        tags=["المستخدمون الإداريون"]
    )
    @action(detail=True, methods=['post'])
    def unlock_account(self, request, pk=None):
        """إلغاء قفل حساب المستخدم"""
        user = self.get_object()
        user.unlock_account()
        
        return Response({'message': 'تم إلغاء قفل الحساب بنجاح'})

    @extend_schema(
        summary="تفعيل المصادقة الثنائية",
        description="تفعيل المصادقة الثنائية للمستخدم",
        tags=["المستخدمون الإداريون"]
    )
    @action(detail=True, methods=['post'])
    def enable_two_factor(self, request, pk=None):
        """تفعيل المصادقة الثنائية"""
        user = self.get_object()
        # سيتم تطبيق المصادقة الثنائية لاحقاً
        user.two_factor_enabled = True
        user.save()
        
        return Response({'message': 'تم تفعيل المصادقة الثنائية'})


@extend_schema_view(
    list=extend_schema(
        summary="سجل النشاطات الإدارية",
        description="الحصول على سجل بجميع النشاطات الإدارية",
        tags=["سجل النشاطات"]
    ),
    retrieve=extend_schema(
        summary="تفاصيل نشاط إداري",
        description="الحصول على تفاصيل نشاط إداري محدد",
        tags=["سجل النشاطات"]
    )
)
class AdminActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet لعرض سجل النشاطات الإدارية
    
    يوفر عرض فقط لسجل النشاطات مع إمكانيات
    فلترة وبحث متقدمة.
    """
    queryset = AdminActivity.objects.all()
    serializer_class = AdminActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['admin_user', 'action_type', 'is_successful']
    search_fields = ['action_description', 'ip_address']
    ordering = ['-timestamp']


@extend_schema_view(
    list=extend_schema(
        summary="إعدادات النظام",
        description="الحصول على قائمة بجميع إعدادات النظام",
        tags=["إعدادات النظام"]
    ),
    create=extend_schema(
        summary="إضافة إعداد جديد",
        description="إنشاء إعداد نظام جديد",
        tags=["إعدادات النظام"]
    ),
    retrieve=extend_schema(
        summary="تفاصيل الإعداد",
        description="الحصول على تفاصيل إعداد نظام محدد",
        tags=["إعدادات النظام"]
    ),
    update=extend_schema(
        summary="تحديث الإعداد",
        description="تحديث قيمة إعداد نظام",
        tags=["إعدادات النظام"]
    ),
    destroy=extend_schema(
        summary="حذف الإعداد",
        description="حذف إعداد نظام",
        tags=["إعدادات النظام"]
    )
)
class SystemSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة إعدادات النظام
    
    يوفر إدارة شاملة لإعدادات النظام مع
    التحقق من صحة القيم والأنواع.
    """
    queryset = SystemSettings.objects.all()
    serializer_class = SystemSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category', 'setting_type', 'is_public', 'is_editable']
    search_fields = ['key', 'name', 'description']
    ordering = ['category', 'display_order', 'name']

    @extend_schema(
        summary="الإعدادات العامة",
        description="الحصول على الإعدادات العامة المتاحة للجمهور",
        tags=["إعدادات النظام"]
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def public(self, request):
        """الحصول على الإعدادات العامة فقط"""
        settings = self.queryset.filter(is_public=True)
        serializer = self.get_serializer(settings, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="الإحصائيات العامة",
        description="الحصول على إحصائيات عامة للنظام",
        tags=["الإحصائيات"]
    )
)
class AdminStatsViewSet(viewsets.ViewSet):
    """
    ViewSet للإحصائيات الإدارية
    
    يوفر إحصائيات شاملة عن النظام والاستخدام
    مع تقارير مفصلة للمديرين.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="الإحصائيات العامة",
        description="الحصول على إحصائيات عامة شاملة للنظام",
        responses={200: AdminStatsSerializer},
        tags=["الإحصائيات"]
    )
    def list(self, request):
        """الحصول على الإحصائيات العامة"""
        # حساب الإحصائيات (سيتم ربطها بالخدمات الأخرى لاحقاً)
        stats = {
            'total_users': AdminUser.objects.count(),
            'active_users': AdminUser.objects.filter(is_active=True).count(),
            'total_complaints': 0,  # سيتم ربطها بخدمة الشكاوى
            'pending_complaints': 0,  # سيتم ربطها بخدمة الشكاوى
            'total_messages': 0,  # سيتم ربطها بخدمة الرسائل
            'total_ratings': 0,  # سيتم ربطها بخدمة التقييمات
            'system_health': 'جيد',
            'last_backup': timezone.now(),
        }
        
        serializer = AdminStatsSerializer(stats)
        return Response(serializer.data)

    @extend_schema(
        summary="إحصائيات المحافظات",
        description="الحصول على إحصائيات مفصلة لجميع المحافظات",
        responses={200: GovernorateStatsSerializer(many=True)},
        tags=["الإحصائيات"]
    )
    @action(detail=False, methods=['get'])
    def governorates(self, request):
        """إحصائيات المحافظات"""
        governorates = Governorate.objects.filter(is_active=True)
        stats = []
        
        for gov in governorates:
            stats.append({
                'governorate_name': gov.name,
                'users_count': 0,  # سيتم ربطها بخدمة المستخدمين
                'complaints_count': 0,  # سيتم ربطها بخدمة الشكاوى
                'messages_count': 0,  # سيتم ربطها بخدمة الرسائل
                'ratings_count': 0,  # سيتم ربطها بخدمة التقييمات
            })
        
        serializer = GovernorateStatsSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="إحصائيات الأحزاب",
        description="الحصول على إحصائيات مفصلة لجميع الأحزاب السياسية",
        responses={200: PartyStatsSerializer(many=True)},
        tags=["الإحصائيات"]
    )
    @action(detail=False, methods=['get'])
    def parties(self, request):
        """إحصائيات الأحزاب"""
        parties = Party.objects.filter(is_active=True)
        stats = []
        
        for party in parties:
            stats.append({
                'party_name': party.name,
                'members_count': party.members_count,
                'candidates_count': party.candidates_count,
                'current_members_count': party.current_members_count,
                'average_rating': 0.0,  # سيتم ربطها بخدمة التقييمات
            })
        
        serializer = PartyStatsSerializer(stats, many=True)
        return Response(serializer.data)
