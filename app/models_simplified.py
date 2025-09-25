"""
نماذج الإدارة المبسطة لتطبيق نائبك
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class SocialMediaLink(models.Model):
    """
    روابط وسائل التواصل الاجتماعي
    """
    
    class Platform(models.TextChoices):
        FACEBOOK = 'facebook', _('فيسبوك')
        TWITTER = 'twitter', _('تويتر')
        INSTAGRAM = 'instagram', _('إنستجرام')
        YOUTUBE = 'youtube', _('يوتيوب')
        LINKEDIN = 'linkedin', _('لينكد إن')
    
    platform = models.CharField(
        _('المنصة'),
        max_length=20,
        choices=Platform.choices,
        unique=True
    )
    
    url = models.URLField(_('الرابط'), max_length=500)
    is_active = models.BooleanField(_('نشط'), default=True)
    icon_class = models.CharField(_('فئة الأيقونة'), max_length=50, blank=True)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('رابط وسائل التواصل')
        verbose_name_plural = _('روابط وسائل التواصل')
        ordering = ['platform']
    
    def __str__(self):
        return f"{self.get_platform_display()}: {self.url}"


class SystemSettings(models.Model):
    """
    إعدادات النظام العامة
    """
    
    class SettingType(models.TextChoices):
        STRING = 'string', _('نص')
        INTEGER = 'integer', _('رقم صحيح')
        BOOLEAN = 'boolean', _('صحيح/خطأ')
        JSON = 'json', _('JSON')
    
    key = models.CharField(_('المفتاح'), max_length=100, unique=True)
    value = models.TextField(_('القيمة'))
    setting_type = models.CharField(
        _('نوع الإعداد'),
        max_length=10,
        choices=SettingType.choices,
        default=SettingType.STRING
    )
    
    description = models.TextField(_('الوصف'), blank=True)
    is_public = models.BooleanField(_('عام'), default=False)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('إعداد النظام')
        verbose_name_plural = _('إعدادات النظام')
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"


class AdminUser(models.Model):
    """
    مستخدمو الإدارة
    """
    
    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', _('مدير عام')
        ADMIN = 'admin', _('مدير')
        MODERATOR = 'moderator', _('مشرف')
        VIEWER = 'viewer', _('مشاهد')
    
    username = models.CharField(_('اسم المستخدم'), max_length=150, unique=True)
    email = models.EmailField(_('البريد الإلكتروني'), unique=True)
    full_name = models.CharField(_('الاسم الكامل'), max_length=200)
    
    role = models.CharField(
        _('الدور'),
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER
    )
    
    is_active = models.BooleanField(_('نشط'), default=True)
    last_login = models.DateTimeField(_('آخر تسجيل دخول'), blank=True, null=True)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('مستخدم إدارة')
        verbose_name_plural = _('مستخدمو الإدارة')
        ordering = ['full_name']
    
    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"


class AuditLog(models.Model):
    """
    سجل العمليات الإدارية
    """
    
    class Action(models.TextChoices):
        CREATE = 'create', _('إنشاء')
        UPDATE = 'update', _('تحديث')
        DELETE = 'delete', _('حذف')
        LOGIN = 'login', _('تسجيل دخول')
        LOGOUT = 'logout', _('تسجيل خروج')
    
    admin_user = models.ForeignKey(
        AdminUser,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        verbose_name=_('المستخدم الإداري')
    )
    
    action = models.CharField(
        _('العملية'),
        max_length=10,
        choices=Action.choices
    )
    
    resource_type = models.CharField(_('نوع المورد'), max_length=100)
    resource_id = models.CharField(_('معرف المورد'), max_length=100, blank=True)
    description = models.TextField(_('الوصف'), blank=True)
    
    ip_address = models.GenericIPAddressField(_('عنوان IP'), blank=True, null=True)
    user_agent = models.TextField(_('متصفح المستخدم'), blank=True)
    
    created_at = models.DateTimeField(_('تاريخ العملية'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('سجل العمليات')
        verbose_name_plural = _('سجلات العمليات')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.admin_user.full_name} - {self.get_action_display()} - {self.resource_type}"
