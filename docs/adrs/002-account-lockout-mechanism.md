# ADR-002: آلية قفل الحسابات الذكية

## الحالة
مقبول

## السياق والمشكلة

منصة نائبك تحتاج لحماية قوية ضد هجمات القوة الغاشمة (Brute Force) وتخمين كلمات المرور. التحدي هو تصميم نظام قفل حسابات يوازن بين:

- **الأمان القوي:** حماية فعالة ضد الهجمات الآلية
- **تجربة المستخدم:** عدم إزعاج المستخدمين الشرعيين
- **المرونة الإدارية:** إمكانية التحكم والتدخل اليدوي
- **قابلية التوسع:** أداء جيد مع آلاف المستخدمين

## البدائل المدروسة

### البديل 1: القفل الثابت البسيط
```python
# قفل لمدة ثابتة بعد 3 محاولات فاشلة
if failed_attempts >= 3:
    lock_until = now() + timedelta(minutes=30)
```

**المزايا:**
- بساطة التطبيق والفهم
- أداء سريع وموثوق
- سهولة الاختبار والصيانة

**العيوب:**
- عدم مرونة في التعامل مع حالات مختلفة
- قد يكون قاسياً جداً أو متساهلاً جداً
- لا يتكيف مع أنماط الهجمات المختلفة

### البديل 2: القفل التدريجي المتصاعد
```python
# زيادة مدة القفل مع كل محاولة
lock_duration = base_duration * (2 ** (failed_attempts - threshold))
```

**المزايا:**
- تدرج في العقوبة يتناسب مع شدة المحاولات
- ردع أقوى للهجمات المستمرة
- مرونة أكبر في التعامل مع الحالات

**العيوب:**
- تعقيد أكبر في التطبيق
- صعوبة في تحديد المعاملات المثلى
- قد يؤدي لقفل طويل جداً

### البديل 3: النظام الذكي المتكيف (المختار)
```python
# نظام متكيف يعتمد على عوامل متعددة
def calculate_lockout_duration(user, failed_attempts, context):
    base_duration = 30  # دقيقة
    
    # عوامل التصعيد
    if failed_attempts <= 3:
        return 0  # لا قفل
    elif failed_attempts <= 5:
        return base_duration
    elif failed_attempts <= 10:
        return base_duration * 2
    else:
        return base_duration * 4  # حد أقصى 2 ساعة
```

## القرار المتخذ

اخترنا **النظام الذكي المتكيف** للأسباب التالية:

### المبررات التقنية

1. **التوازن الأمثل:**
   - حماية قوية ضد الهجمات الآلية
   - تجربة مستخدم معقولة للأخطاء البشرية
   - مرونة في التعامل مع حالات مختلفة

2. **قابلية التخصيص:**
   - معاملات قابلة للتعديل حسب البيئة
   - إمكانية تخصيص قواعد لأنواع مستخدمين مختلفة
   - تكامل مع نظام المراقبة والتنبيهات

3. **الشفافية والتحكم:**
   - تسجيل مفصل لجميع محاولات القفل
   - إمكانية التدخل اليدوي من المديرين
   - تقارير وإحصائيات عن أنماط الهجمات

### التطبيق التقني

```python
class AdminUser(AbstractUser):
    failed_login_attempts = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    
    def should_lock_account(self):
        """تحديد ما إذا كان يجب قفل الحساب"""
        if self.failed_login_attempts < 3:
            return False
            
        # فحص التوقيت - إعادة تعيين العداد بعد ساعة
        if self.last_failed_login:
            time_since_last = timezone.now() - self.last_failed_login
            if time_since_last > timedelta(hours=1):
                self.failed_login_attempts = 0
                self.save()
                return False
        
        return True
    
    def calculate_lockout_duration(self):
        """حساب مدة القفل بناءً على عدد المحاولات"""
        attempts = self.failed_login_attempts
        
        if attempts <= 3:
            return 0
        elif attempts <= 5:
            return 30  # 30 دقيقة
        elif attempts <= 10:
            return 60  # ساعة واحدة
        else:
            return 120  # ساعتان (حد أقصى)
    
    def lock_account(self, duration_minutes=None):
        """قفل الحساب مع تسجيل السبب"""
        if duration_minutes is None:
            duration_minutes = self.calculate_lockout_duration()
        
        self.account_locked_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save(update_fields=['account_locked_until'])
        
        # تسجيل في سجل النشاطات
        AdminActivity.objects.create(
            admin_user=self,
            action_type='suspend',
            action_description=f'قفل الحساب لمدة {duration_minutes} دقيقة - محاولات فاشلة: {self.failed_login_attempts}',
            additional_data={
                'failed_attempts': self.failed_login_attempts,
                'lockout_duration': duration_minutes,
                'lockout_reason': 'failed_login_attempts'
            }
        )
```

### قواعد القفل المفصلة

```python
LOCKOUT_RULES = {
    'attempts_threshold': 3,      # بداية القفل
    'reset_window_hours': 1,      # إعادة تعيين العداد
    'base_duration_minutes': 30,  # المدة الأساسية
    'max_duration_minutes': 120,  # الحد الأقصى
    'escalation_factor': 2,       # معامل التصعيد
}

def get_lockout_duration(failed_attempts):
    """حساب مدة القفل وفقاً للقواعد المحددة"""
    if failed_attempts < LOCKOUT_RULES['attempts_threshold']:
        return 0
    
    excess_attempts = failed_attempts - LOCKOUT_RULES['attempts_threshold']
    duration = LOCKOUT_RULES['base_duration_minutes'] * (
        LOCKOUT_RULES['escalation_factor'] ** min(excess_attempts, 3)
    )
    
    return min(duration, LOCKOUT_RULES['max_duration_minutes'])
```

## العواقب

### النتائج الإيجابية

1. **حماية أمنية قوية:**
   - ردع فعال للهجمات الآلية
   - حماية متدرجة تتناسب مع شدة التهديد
   - تقليل كبير في محاولات الاختراق الناجحة

2. **تجربة مستخدم محسنة:**
   - تسامح مع الأخطاء البشرية العادية
   - رسائل واضحة عن سبب القفل ومدته
   - إمكانية الاتصال بالدعم لإلغاء القفل

3. **مرونة إدارية:**
   - تحكم كامل في معاملات النظام
   - إمكانية إلغاء القفل يدوياً
   - تقارير مفصلة عن أنماط الهجمات

### التحديات المحتملة

1. **تعقيد التطبيق:**
   - منطق أكثر تعقيداً من النظام البسيط
   - الحاجة لاختبارات شاملة لجميع السيناريوهات

2. **ضبط المعاملات:**
   - صعوبة في تحديد القيم المثلى
   - الحاجة لمراقبة مستمرة وتعديل

### استراتيجيات التخفيف

1. **مراقبة وتنبيهات:**
```python
# تنبيه عند محاولات مشبوهة
def check_suspicious_activity(user):
    recent_attempts = AdminActivity.objects.filter(
        admin_user=user,
        action_type='login',
        is_successful=False,
        timestamp__gte=timezone.now() - timedelta(hours=1)
    ).count()
    
    if recent_attempts >= 5:
        send_security_alert(
            f'محاولات دخول مشبوهة للمستخدم {user.username}',
            {'attempts': recent_attempts, 'user_id': user.id}
        )
```

2. **إعدادات قابلة للتخصيص:**
```python
# إعدادات في قاعدة البيانات
class SecuritySettings(models.Model):
    lockout_threshold = models.IntegerField(default=3)
    base_lockout_minutes = models.IntegerField(default=30)
    max_lockout_minutes = models.IntegerField(default=120)
    reset_window_hours = models.IntegerField(default=1)
    
    @classmethod
    def get_current(cls):
        return cls.objects.first() or cls.objects.create()
```

3. **واجهة إدارة متقدمة:**
   - لوحة تحكم لمراقبة الحسابات المقفلة
   - إحصائيات عن أنماط الهجمات
   - أدوات لإلغاء القفل الجماعي عند الحاجة

## المراجعة والتقييم

### معايير النجاح
- تقليل محاولات الاختراق الناجحة بنسبة > 95%
- عدم شكاوى مستخدمين شرعيين > 5% شهرياً
- وقت استجابة فحص القفل < 100ms

### مؤشرات المراقبة
- عدد الحسابات المقفلة يومياً
- متوسط مدة القفل
- عدد طلبات إلغاء القفل اليدوي
- أنماط IP المشبوهة

### جدولة المراجعة
- **مراجعة أسبوعية:** إحصائيات الأمان
- **مراجعة شهرية:** تقييم فعالية المعاملات
- **مراجعة ربع سنوية:** تحديث استراتيجية الأمان

---

**تاريخ الإنشاء:** سبتمبر 2024  
**المؤلف:** فريق الأمان - نائبك  
**المراجعون:** فريق التطوير، فريق تجربة المستخدم  
**الحالة:** مقبول ومطبق
