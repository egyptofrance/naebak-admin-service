# ADR-004: نظام سجل النشاطات والتدقيق

## الحالة
مقبول

## السياق والمشكلة

منصة نائبك تتعامل مع بيانات حساسة وعمليات إدارية مهمة تتطلب مساءلة كاملة وشفافية. نحتاج لنظام تدقيق شامل يسجل جميع العمليات الإدارية لضمان:

- **المساءلة الكاملة:** تتبع جميع الإجراءات والقرارات الإدارية
- **الامتثال القانوني:** تلبية متطلبات الشفافية والحوكمة
- **الأمان والمراقبة:** اكتشاف الأنشطة المشبوهة أو غير المصرح بها
- **التحليل والتحسين:** فهم أنماط الاستخدام وتحسين العمليات

## البدائل المدروسة

### البديل 1: تسجيل بسيط في ملفات Log
```python
import logging

logger = logging.getLogger('admin_actions')

def log_admin_action(user, action, details):
    logger.info(f"{user.username} performed {action}: {details}")
```

**المزايا:**
- بساطة التطبيق والصيانة
- أداء سريع وموثوق
- أدوات تحليل متوفرة

**العيوب:**
- صعوبة في البحث والاستعلام
- لا يدعم الربط مع الكائنات
- محدودية في التحليل والتقارير
- صعوبة في الأرشفة طويلة المدى

### البديل 2: نظام تدقيق خارجي (External Audit Service)
```python
# استخدام خدمة خارجية مثل AWS CloudTrail
import boto3

def log_to_cloudtrail(event_data):
    cloudtrail = boto3.client('cloudtrail')
    cloudtrail.put_events(Records=[event_data])
```

**المزايا:**
- موثوقية عالية ومقاومة للتلاعب
- قابلية توسع ممتازة
- أدوات تحليل متقدمة
- نسخ احتياطي تلقائي

**العيوب:**
- تكلفة إضافية مستمرة
- اعتماد على خدمات خارجية
- تعقيد في التكامل والإعداد
- قيود على تخصيص البيانات

### البديل 3: نظام تدقيق داخلي متقدم (المختار)
```python
class AdminActivity(models.Model):
    admin_user = models.ForeignKey(AdminUser, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    # ... المزيد من الحقول
```

## القرار المتخذ

اخترنا **نظام التدقيق الداخلي المتقدم** للأسباب التالية:

### المبررات التقنية

1. **تحكم كامل:**
   - تخصيص كامل لهيكل البيانات
   - مرونة في إضافة حقول جديدة
   - تكامل مباشر مع نماذج Django

2. **أداء محسن:**
   - استعلامات سريعة ومحسنة
   - فهارس مخصصة للبحث
   - تخزين محلي يقلل زمن الاستجابة

3. **أمان وخصوصية:**
   - بيانات محفوظة داخلياً
   - تحكم كامل في الوصول والصلاحيات
   - إمكانية التشفير والحماية المتقدمة

### التطبيق التقني

```python
class AdminActivity(models.Model):
    """نموذج سجل النشاطات الإدارية الشامل"""
    
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
        ('assign', 'تعيين'),
        ('transfer', 'نقل'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'منخفض'),
        ('medium', 'متوسط'),
        ('high', 'عالي'),
        ('critical', 'حرج'),
    ]
    
    # معلومات أساسية
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin_user = models.ForeignKey(AdminUser, on_delete=models.CASCADE, 
                                 verbose_name='المستخدم الإداري')
    action_type = models.CharField('نوع العملية', max_length=20, choices=ACTION_TYPES)
    action_description = models.CharField('وصف العملية', max_length=500)
    severity = models.CharField('مستوى الأهمية', max_length=10, 
                              choices=SEVERITY_LEVELS, default='medium')
    
    # ربط مع الكائن المتأثر
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, 
                                   null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # معلومات تقنية
    ip_address = models.GenericIPAddressField('عنوان IP', null=True, blank=True)
    user_agent = models.TextField('معلومات المتصفح', blank=True)
    session_key = models.CharField('مفتاح الجلسة', max_length=40, blank=True)
    
    # بيانات إضافية
    old_values = models.JSONField('القيم السابقة', default=dict, blank=True)
    new_values = models.JSONField('القيم الجديدة', default=dict, blank=True)
    additional_data = models.JSONField('بيانات إضافية', default=dict, blank=True)
    
    # معلومات زمنية
    timestamp = models.DateTimeField('وقت العملية', auto_now_add=True)
    duration_ms = models.PositiveIntegerField('مدة العملية (مللي ثانية)', 
                                            null=True, blank=True)
    
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
            models.Index(fields=['ip_address', '-timestamp']),
            models.Index(fields=['severity', '-timestamp']),
            models.Index(fields=['is_successful', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.get_action_type_display()} - {self.timestamp}"
    
    @classmethod
    def log_activity(cls, admin_user, action_type, description, **kwargs):
        """تسجيل نشاط إداري جديد"""
        activity = cls.objects.create(
            admin_user=admin_user,
            action_type=action_type,
            action_description=description,
            **kwargs
        )
        
        # إرسال تنبيه للعمليات الحرجة
        if kwargs.get('severity') == 'critical':
            send_critical_activity_alert(activity)
        
        return activity
```

### نظام التسجيل التلقائي

```python
class AuditMiddleware:
    """Middleware لتسجيل النشاطات تلقائياً"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # تسجيل بداية الطلب
        start_time = time.time()
        
        response = self.get_response(request)
        
        # تسجيل النشاط إذا كان مستخدم إداري
        if hasattr(request, 'user') and isinstance(request.user, AdminUser):
            duration_ms = int((time.time() - start_time) * 1000)
            
            self.log_request_activity(request, response, duration_ms)
        
        return response
    
    def log_request_activity(self, request, response, duration_ms):
        """تسجيل نشاط الطلب"""
        action_type = self.determine_action_type(request)
        
        if action_type:  # تسجيل العمليات المهمة فقط
            AdminActivity.log_activity(
                admin_user=request.user,
                action_type=action_type,
                action_description=f"{request.method} {request.path}",
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                session_key=request.session.session_key,
                duration_ms=duration_ms,
                is_successful=200 <= response.status_code < 400,
                additional_data={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'query_params': dict(request.GET),
                }
            )

# Decorator للتسجيل اليدوي
def log_admin_activity(action_type, description=None, severity='medium'):
    """Decorator لتسجيل النشاطات الإدارية"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            start_time = time.time()
            error_message = ""
            is_successful = True
            
            try:
                result = func(self, request, *args, **kwargs)
                return result
            except Exception as e:
                is_successful = False
                error_message = str(e)
                raise
            finally:
                duration_ms = int((time.time() - start_time) * 1000)
                
                AdminActivity.log_activity(
                    admin_user=request.user,
                    action_type=action_type,
                    action_description=description or f"{func.__name__}",
                    severity=severity,
                    duration_ms=duration_ms,
                    is_successful=is_successful,
                    error_message=error_message,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                )
        
        return wrapper
    return decorator
```

### نظام التقارير والتحليل

```python
class AuditReportGenerator:
    """مولد تقارير التدقيق"""
    
    @staticmethod
    def generate_user_activity_report(user, start_date, end_date):
        """تقرير نشاط مستخدم محدد"""
        activities = AdminActivity.objects.filter(
            admin_user=user,
            timestamp__range=[start_date, end_date]
        ).select_related('admin_user', 'content_type')
        
        return {
            'user': user.get_full_name(),
            'period': f"{start_date} - {end_date}",
            'total_activities': activities.count(),
            'successful_activities': activities.filter(is_successful=True).count(),
            'failed_activities': activities.filter(is_successful=False).count(),
            'activities_by_type': activities.values('action_type').annotate(
                count=Count('id')
            ).order_by('-count'),
            'critical_activities': activities.filter(severity='critical').count(),
            'activities': activities[:100]  # آخر 100 نشاط
        }
    
    @staticmethod
    def generate_security_report(start_date, end_date):
        """تقرير الأمان والأنشطة المشبوهة"""
        activities = AdminActivity.objects.filter(
            timestamp__range=[start_date, end_date]
        )
        
        # تحليل الأنشطة المشبوهة
        suspicious_ips = activities.values('ip_address').annotate(
            failed_attempts=Count('id', filter=Q(is_successful=False))
        ).filter(failed_attempts__gte=5).order_by('-failed_attempts')
        
        return {
            'period': f"{start_date} - {end_date}",
            'total_activities': activities.count(),
            'failed_activities': activities.filter(is_successful=False).count(),
            'critical_activities': activities.filter(severity='critical').count(),
            'suspicious_ips': suspicious_ips,
            'login_attempts': activities.filter(action_type='login').count(),
            'failed_logins': activities.filter(
                action_type='login', is_successful=False
            ).count(),
        }
```

## العواقب

### النتائج الإيجابية

1. **مساءلة شاملة:**
   - تتبع كامل لجميع العمليات الإدارية
   - إمكانية تحديد المسؤول عن كل إجراء
   - سجل تاريخي لا يمكن تعديله

2. **أمان محسن:**
   - اكتشاف الأنشطة المشبوهة فوراً
   - تتبع محاولات الوصول غير المصرح بها
   - تحليل أنماط الهجمات

3. **امتثال قانوني:**
   - تلبية متطلبات الشفافية الحكومية
   - سجلات قابلة للتدقيق والمراجعة
   - إثبات الامتثال للمعايير

### التحديات المحتملة

1. **حجم البيانات:**
   - نمو سريع في حجم سجل النشاطات
   - الحاجة لاستراتيجية أرشفة فعالة

2. **الأداء:**
   - تأثير محتمل على أداء العمليات
   - الحاجة لتحسين الاستعلامات

### استراتيجيات التخفيف

1. **إدارة دورة حياة البيانات:**
```python
class AuditDataManager:
    @staticmethod
    def archive_old_activities(days_to_keep=365):
        """أرشفة النشاطات القديمة"""
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        old_activities = AdminActivity.objects.filter(
            timestamp__lt=cutoff_date
        )
        
        # تصدير للأرشيف
        archive_file = f"audit_archive_{cutoff_date.strftime('%Y%m%d')}.json"
        export_to_archive(old_activities, archive_file)
        
        # حذف من قاعدة البيانات الرئيسية
        old_activities.delete()
```

2. **تحسين الأداء:**
```python
# استخدام Celery للتسجيل غير المتزامن
@shared_task
def log_activity_async(user_id, action_type, description, **kwargs):
    """تسجيل النشاط بشكل غير متزامن"""
    user = AdminUser.objects.get(id=user_id)
    AdminActivity.log_activity(user, action_type, description, **kwargs)
```

## المراجعة والتقييم

### معايير النجاح
- تسجيل 100% من العمليات الإدارية الحساسة
- وقت استجابة التسجيل < 50ms
- اكتشاف الأنشطة المشبوهة خلال < 5 دقائق

### مؤشرات المراقبة
- عدد النشاطات المسجلة يومياً
- معدل نمو حجم البيانات
- وقت الاستجابة للاستعلامات
- عدد التنبيهات الأمنية

### جدولة المراجعة
- **مراجعة يومية:** تقارير الأمان والأنشطة المشبوهة
- **مراجعة أسبوعية:** تحليل الأداء وحجم البيانات
- **مراجعة شهرية:** تقييم فعالية النظام وتحديث السياسات

---

**تاريخ الإنشاء:** سبتمبر 2024  
**المؤلف:** فريق الأمان والتطوير - نائبك  
**المراجعون:** فريق الامتثال، فريق الأداء  
**الحالة:** مقبول ومطبق
