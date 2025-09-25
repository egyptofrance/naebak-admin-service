"""
نماذج خدمة الإدارة - مشروع نائبك
إدارة النظام والمستخدمين والصلاحيات
"""
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid


class Governorate(models.Model):
    """نموذج المحافظات المصرية"""
    
    REGIONS = [
        ('cairo', 'القاهرة الكبرى'),
        ('delta', 'الدلتا'),
        ('canal', 'قناة السويس'),
        ('sinai', 'سيناء'),
        ('red_sea', 'البحر الأحمر'),
        ('upper', 'الصعيد'),
    ]
    
    name = models.CharField('اسم المحافظة', max_length=100, unique=True)
    name_en = models.CharField('الاسم بالإنجليزية', max_length=100, unique=True)
    code = models.CharField('كود المحافظة', max_length=10, unique=True)
    region = models.CharField('المنطقة', max_length=20, choices=REGIONS)
    capital = models.CharField('العاصمة', max_length=100)
    area_km2 = models.DecimalField('المساحة (كم²)', max_digits=10, decimal_places=2, null=True, blank=True)
    population = models.PositiveIntegerField('عدد السكان', null=True, blank=True)
    is_active = models.BooleanField('نشط', default=True)
    display_order = models.PositiveIntegerField('ترتيب العرض', default=0)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'محافظة'
        verbose_name_plural = 'المحافظات'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['region']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def users_count(self):
        """عدد المستخدمين في هذه المحافظة"""
        # سيتم ربطها بنموذج المستخدمين لاحقاً
        return 0


class Party(models.Model):
    """نموذج الأحزاب السياسية"""
    
    name = models.CharField('اسم الحزب', max_length=200, unique=True)
    name_en = models.CharField('الاسم بالإنجليزية', max_length=200, unique=True)
    abbreviation = models.CharField('الاختصار', max_length=50, unique=True)
    description = models.TextField('الوصف', blank=True)
    founded_date = models.DateField('تاريخ التأسيس', null=True, blank=True)
    headquarters = models.CharField('المقر الرئيسي', max_length=200, blank=True)
    website = models.URLField('الموقع الإلكتروني', blank=True)
    logo = models.ImageField('الشعار', upload_to='parties/logos/', blank=True, null=True)
    color = models.CharField('اللون الأساسي', max_length=7, default='#007bff',
                           validators=[RegexValidator(r'^#[0-9A-Fa-f]{6}$', 'يجب أن يكون اللون بصيغة hex')])
    is_active = models.BooleanField('نشط', default=True)
    display_order = models.PositiveIntegerField('ترتيب العرض', default=0)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'حزب سياسي'
        verbose_name_plural = 'الأحزاب السياسية'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['abbreviation']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def members_count(self):
        """عدد أعضاء الحزب"""
        # سيتم ربطها بنموذج المستخدمين لاحقاً
        return 0
    
    @property
    def candidates_count(self):
        """عدد مرشحي الحزب"""
        return 0
    
    @property
    def current_members_count(self):
        """عدد الأعضاء الحاليين في البرلمان"""
        return 0


class ComplaintType(models.Model):
    """نموذج أنواع الشكاوى"""
    
    CATEGORIES = [
        ('infrastructure', 'البنية التحتية'),
        ('health', 'الصحة'),
        ('education', 'التعليم'),
        ('utilities', 'المرافق'),
        ('transportation', 'النقل والمواصلات'),
        ('environment', 'البيئة'),
        ('social', 'الخدمات الاجتماعية'),
        ('economic', 'الشؤون الاقتصادية'),
        ('legal', 'الشؤون القانونية'),
        ('security', 'الأمن والسلامة'),
        ('housing', 'الإسكان'),
        ('administrative', 'الخدمات الإدارية'),
        ('other', 'أخرى'),
    ]
    
    COUNCIL_TYPES = [
        ('parliament', 'مجلس النواب'),
        ('senate', 'مجلس الشيوخ'),
        ('both', 'كلا المجلسين'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'منخفضة'),
        ('medium', 'متوسطة'),
        ('high', 'عالية'),
        ('urgent', 'عاجلة'),
    ]
    
    name = models.CharField('اسم نوع الشكوى', max_length=200, unique=True)
    name_en = models.CharField('الاسم بالإنجليزية', max_length=200, unique=True)
    description = models.TextField('الوصف', blank=True)
    category = models.CharField('الفئة', max_length=20, choices=CATEGORIES)
    target_council = models.CharField('المجلس المستهدف', max_length=20, choices=COUNCIL_TYPES, default='parliament')
    icon = models.CharField('الأيقونة', max_length=10, default='📋')
    color = models.CharField('اللون', max_length=7, default='#007bff',
                           validators=[RegexValidator(r'^#[0-9A-Fa-f]{6}$', 'يجب أن يكون اللون بصيغة hex')])
    priority_level = models.CharField('مستوى الأولوية', max_length=10, choices=PRIORITY_LEVELS, default='medium')
    estimated_resolution_days = models.PositiveIntegerField('أيام الحل المقدرة', default=30)
    requires_attachments = models.BooleanField('يتطلب مرفقات', default=False)
    max_attachments = models.PositiveIntegerField('الحد الأقصى للمرفقات', default=5)
    is_active = models.BooleanField('نشط', default=True)
    is_public = models.BooleanField('عام للجمهور', default=True)
    display_order = models.PositiveIntegerField('ترتيب العرض', default=0)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'نوع شكوى'
        verbose_name_plural = 'أنواع الشكاوى'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['target_council']),
            models.Index(fields=['is_active', 'is_public']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def complaints_count(self):
        """عدد الشكاوى من هذا النوع"""
        return 0
    
    @property
    def resolution_rate(self):
        """معدل الحل"""
        return 0.0


class AdminRole(models.Model):
    """نموذج أدوار الإدارة"""
    
    ROLE_TYPES = [
        ('super_admin', 'مدير عام'),
        ('content_moderator', 'مشرف المحتوى'),
        ('complaint_manager', 'مشرف الشكاوى'),
        ('user_manager', 'مشرف المستخدمين'),
        ('statistics_viewer', 'عارض الإحصائيات'),
        ('system_admin', 'مدير النظام'),
        ('data_analyst', 'محلل البيانات'),
        ('support_agent', 'وكيل الدعم'),
    ]
    
    name = models.CharField('اسم الدور', max_length=100, unique=True)
    name_en = models.CharField('الاسم بالإنجليزية', max_length=100, unique=True)
    role_type = models.CharField('نوع الدور', max_length=20, choices=ROLE_TYPES, unique=True)
    description = models.TextField('الوصف', blank=True)
    permissions = models.ManyToManyField(Permission, verbose_name='الصلاحيات', blank=True)
    is_active = models.BooleanField('نشط', default=True)
    is_system_role = models.BooleanField('دور نظام', default=False, help_text='لا يمكن حذف أدوار النظام')
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'دور إداري'
        verbose_name_plural = 'الأدوار الإدارية'
        ordering = ['name']
        indexes = [
            models.Index(fields=['role_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def users_count(self):
        """عدد المستخدمين بهذا الدور"""
        return self.admin_users.filter(is_active=True).count()


class AdminUser(AbstractUser):
    """نموذج المستخدمين الإداريين"""
    
    # إضافة حقول إضافية للمستخدم الإداري
    phone_number = models.CharField('رقم الهاتف', max_length=20, blank=True,
                                  validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'رقم هاتف غير صحيح')])
    employee_id = models.CharField('رقم الموظف', max_length=20, unique=True, null=True, blank=True)
    department = models.CharField('القسم', max_length=100, blank=True)
    position = models.CharField('المنصب', max_length=100, blank=True)
    admin_roles = models.ManyToManyField(AdminRole, verbose_name='الأدوار الإدارية', blank=True)
    governorate = models.ForeignKey(Governorate, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name='المحافظة المسؤول عنها')
    profile_picture = models.ImageField('صورة الملف الشخصي', upload_to='admin/profiles/', blank=True, null=True)
    bio = models.TextField('نبذة تعريفية', blank=True)
    last_activity = models.DateTimeField('آخر نشاط', null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField('محاولات تسجيل الدخول الفاشلة', default=0)
    account_locked_until = models.DateTimeField('مقفل حتى', null=True, blank=True)
    two_factor_enabled = models.BooleanField('المصادقة الثنائية مفعلة', default=False)
    two_factor_secret = models.CharField('سر المصادقة الثنائية', max_length=32, blank=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name='أنشئ بواسطة')
    
    class Meta:
        verbose_name = 'مستخدم إداري'
        verbose_name_plural = 'المستخدمون الإداريون'
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['department']),
            models.Index(fields=['is_active']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    @property
    def is_account_locked(self):
        """هل الحساب مقفل؟"""
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False
    
    def lock_account(self, duration_minutes=30):
        """قفل الحساب لفترة محددة"""
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save(update_fields=['account_locked_until'])
    
    def unlock_account(self):
        """إلغاء قفل الحساب"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['account_locked_until', 'failed_login_attempts'])
    
    def has_admin_permission(self, permission_codename):
        """فحص صلاحية إدارية محددة"""
        return self.user_permissions.filter(codename=permission_codename).exists() or \
               self.admin_roles.filter(permissions__codename=permission_codename, is_active=True).exists()


class AdminActivity(models.Model):
    """نموذج سجل نشاطات الإدارة"""
    
    ACTION_TYPES = [
        ('create', 'إنشاء'),
        ('update', 'تعديل'),
        ('delete', 'حذف'),
        ('view', 'عرض'),
        ('login', 'تسجيل دخول'),
        ('logout', 'تسجيل خروج'),
        ('approve', 'موافقة'),
        ('reject', 'رفض'),
        ('suspend', 'إيقاف'),
        ('activate', 'تفعيل'),
        ('export', 'تصدير'),
        ('import', 'استيراد'),
        ('backup', 'نسخ احتياطي'),
        ('restore', 'استعادة'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin_user = models.ForeignKey(AdminUser, on_delete=models.CASCADE, verbose_name='المستخدم الإداري')
    action_type = models.CharField('نوع العملية', max_length=20, choices=ACTION_TYPES)
    action_description = models.CharField('وصف العملية', max_length=500)
    
    # Generic foreign key للربط مع أي نموذج
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # بيانات إضافية
    ip_address = models.GenericIPAddressField('عنوان IP', null=True, blank=True)
    user_agent = models.TextField('معلومات المتصفح', blank=True)
    session_key = models.CharField('مفتاح الجلسة', max_length=40, blank=True)
    
    # بيانات العملية
    old_values = models.JSONField('القيم القديمة', null=True, blank=True)
    new_values = models.JSONField('القيم الجديدة', null=True, blank=True)
    additional_data = models.JSONField('بيانات إضافية', null=True, blank=True)
    
    # معلومات التوقيت
    timestamp = models.DateTimeField('وقت العملية', auto_now_add=True)
    duration_ms = models.PositiveIntegerField('مدة العملية (ميلي ثانية)', null=True, blank=True)
    
    # حالة العملية
    is_successful = models.BooleanField('نجحت العملية', default=True)
    error_message = models.TextField('رسالة الخطأ', blank=True)
    
    class Meta:
        verbose_name = 'نشاط إداري'
        verbose_name_plural = 'النشاطات الإدارية'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['admin_user', '-timestamp']),
            models.Index(fields=['action_type', '-timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.get_action_type_display()} - {self.timestamp}"


class SystemSettings(models.Model):
    """نموذج إعدادات النظام"""
    
    SETTING_TYPES = [
        ('string', 'نص'),
        ('integer', 'رقم صحيح'),
        ('float', 'رقم عشري'),
        ('boolean', 'صحيح/خطأ'),
        ('json', 'JSON'),
        ('text', 'نص طويل'),
        ('email', 'بريد إلكتروني'),
        ('url', 'رابط'),
        ('color', 'لون'),
        ('file', 'ملف'),
    ]
    
    key = models.CharField('مفتاح الإعداد', max_length=100, unique=True)
    name = models.CharField('اسم الإعداد', max_length=200)
    description = models.TextField('الوصف', blank=True)
    setting_type = models.CharField('نوع الإعداد', max_length=20, choices=SETTING_TYPES, default='string')
    value = models.TextField('القيمة', blank=True)
    default_value = models.TextField('القيمة الافتراضية', blank=True)
    is_public = models.BooleanField('عام للجمهور', default=False, help_text='هل يمكن عرضه في الواجهة الأمامية؟')
    is_editable = models.BooleanField('قابل للتعديل', default=True)
    is_required = models.BooleanField('مطلوب', default=False)
    validation_rules = models.JSONField('قواعد التحقق', null=True, blank=True)
    category = models.CharField('الفئة', max_length=100, default='general')
    display_order = models.PositiveIntegerField('ترتيب العرض', default=0)
    updated_by = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name='محدث بواسطة')
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    
    class Meta:
        verbose_name = 'إعداد النظام'
        verbose_name_plural = 'إعدادات النظام'
        ordering = ['category', 'display_order', 'name']
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['category']),
            models.Index(fields=['is_public']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_typed_value(self):
        """الحصول على القيمة بالنوع الصحيح"""
        if not self.value:
            return self.get_typed_default_value()
        
        try:
            if self.setting_type == 'integer':
                return int(self.value)
            elif self.setting_type == 'float':
                return float(self.value)
            elif self.setting_type == 'boolean':
                return self.value.lower() in ('true', '1', 'yes', 'on')
            elif self.setting_type == 'json':
                import json
                return json.loads(self.value)
            else:
                return self.value
        except (ValueError, TypeError):
            return self.get_typed_default_value()
    
    def get_typed_default_value(self):
        """الحصول على القيمة الافتراضية بالنوع الصحيح"""
        if not self.default_value:
            return None
        
        try:
            if self.setting_type == 'integer':
                return int(self.default_value)
            elif self.setting_type == 'float':
                return float(self.default_value)
            elif self.setting_type == 'boolean':
                return self.default_value.lower() in ('true', '1', 'yes', 'on')
            elif self.setting_type == 'json':
                import json
                return json.loads(self.default_value)
            else:
                return self.default_value
        except (ValueError, TypeError):
            return None


class AdminDashboard(models.Model):
    """نموذج إعدادات لوحة التحكم الإدارية"""
    
    WIDGET_TYPES = [
        ('stats_card', 'بطاقة إحصائيات'),
        ('chart', 'رسم بياني'),
        ('table', 'جدول'),
        ('list', 'قائمة'),
        ('calendar', 'تقويم'),
        ('map', 'خريطة'),
        ('progress', 'شريط تقدم'),
        ('alert', 'تنبيه'),
    ]
    
    admin_user = models.ForeignKey(AdminUser, on_delete=models.CASCADE, verbose_name='المستخدم الإداري')
    widget_type = models.CharField('نوع الودجت', max_length=20, choices=WIDGET_TYPES)
    widget_title = models.CharField('عنوان الودجت', max_length=200)
    widget_config = models.JSONField('إعدادات الودجت', default=dict)
    position_x = models.PositiveIntegerField('الموضع الأفقي', default=0)
    position_y = models.PositiveIntegerField('الموضع الرأسي', default=0)
    width = models.PositiveIntegerField('العرض', default=1)
    height = models.PositiveIntegerField('الارتفاع', default=1)
    is_visible = models.BooleanField('مرئي', default=True)
    refresh_interval = models.PositiveIntegerField('فترة التحديث (ثواني)', default=300)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'ودجت لوحة التحكم'
        verbose_name_plural = 'ودجتات لوحة التحكم'
        ordering = ['admin_user', 'position_y', 'position_x']
        unique_together = ['admin_user', 'position_x', 'position_y']
        indexes = [
            models.Index(fields=['admin_user', 'is_visible']),
        ]
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.widget_title}"


class AdminSettings(models.Model):
    """نموذج إعدادات خدمة الإدارة"""
    
    # إعدادات عامة
    max_login_attempts = models.PositiveIntegerField('الحد الأقصى لمحاولات تسجيل الدخول', default=5)
    account_lockout_duration = models.PositiveIntegerField('مدة قفل الحساب (دقائق)', default=30)
    session_timeout = models.PositiveIntegerField('انتهاء الجلسة (دقائق)', default=60)
    password_expiry_days = models.PositiveIntegerField('انتهاء كلمة المرور (أيام)', default=90)
    
    # إعدادات الأمان
    require_two_factor = models.BooleanField('المصادقة الثنائية مطلوبة', default=False)
    allow_concurrent_sessions = models.BooleanField('السماح بجلسات متعددة', default=False)
    log_all_activities = models.BooleanField('تسجيل جميع النشاطات', default=True)
    enable_ip_whitelist = models.BooleanField('تفعيل قائمة IP المسموحة', default=False)
    allowed_ip_addresses = models.JSONField('عناوين IP المسموحة', default=list, blank=True)
    
    # إعدادات النسخ الاحتياطي
    auto_backup_enabled = models.BooleanField('النسخ الاحتياطي التلقائي مفعل', default=True)
    backup_frequency_hours = models.PositiveIntegerField('تكرار النسخ الاحتياطي (ساعات)', default=24)
    backup_retention_days = models.PositiveIntegerField('الاحتفاظ بالنسخ الاحتياطية (أيام)', default=30)
    
    # إعدادات الإشعارات
    email_notifications_enabled = models.BooleanField('إشعارات البريد الإلكتروني مفعلة', default=True)
    sms_notifications_enabled = models.BooleanField('إشعارات الرسائل النصية مفعلة', default=False)
    notification_email = models.EmailField('بريد الإشعارات', blank=True)
    
    # إعدادات الأداء
    max_records_per_page = models.PositiveIntegerField('الحد الأقصى للسجلات في الصفحة', default=50)
    cache_timeout_minutes = models.PositiveIntegerField('انتهاء التخزين المؤقت (دقائق)', default=15)
    enable_query_optimization = models.BooleanField('تفعيل تحسين الاستعلامات', default=True)
    
    # إعدادات التقارير
    default_report_format = models.CharField('تنسيق التقرير الافتراضي', max_length=10, 
                                           choices=[('pdf', 'PDF'), ('excel', 'Excel'), ('csv', 'CSV')], 
                                           default='pdf')
    include_charts_in_reports = models.BooleanField('تضمين الرسوم البيانية في التقارير', default=True)
    
    # معلومات التحديث
    updated_by = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name='محدث بواسطة')
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'إعدادات الإدارة'
        verbose_name_plural = 'إعدادات الإدارة'
    
    def __str__(self):
        return 'إعدادات خدمة الإدارة'
    
    def save(self, *args, **kwargs):
        # التأكد من وجود سجل واحد فقط
        if not self.pk and AdminSettings.objects.exists():
            raise ValueError('يمكن وجود سجل واحد فقط من إعدادات الإدارة')
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """الحصول على إعدادات الإدارة"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
