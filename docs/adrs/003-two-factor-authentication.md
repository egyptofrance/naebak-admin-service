# ADR-003: استراتيجية المصادقة الثنائية

## الحالة
مقبول

## السياق والمشكلة

المستخدمون الإداريون في منصة نائبك يتعاملون مع بيانات حساسة ولديهم صلاحيات واسعة. نحتاج لطبقة أمان إضافية تتجاوز كلمة المرور التقليدية. التحدي هو اختيار وتطبيق نظام مصادقة ثنائية يحقق:

- **أمان عالي:** حماية قوية ضد اختراق الحسابات
- **سهولة الاستخدام:** تجربة مستخدم سلسة وغير معقدة
- **موثوقية:** يعمل بشكل مستقر في جميع الظروف
- **مرونة:** دعم طرق متعددة للمصادقة الثنائية

## البدائل المدروسة

### البديل 1: SMS-based 2FA
```python
# إرسال رمز عبر الرسائل النصية
def send_sms_code(user):
    code = generate_random_code(6)
    send_sms(user.phone_number, f"رمز التحقق: {code}")
    cache.set(f"sms_code_{user.id}", code, timeout=300)
```

**المزايا:**
- سهولة الفهم والاستخدام
- لا يحتاج تطبيقات إضافية
- مألوف لمعظم المستخدمين

**العيوب:**
- عرضة لهجمات SIM Swapping
- يعتمد على شبكة الهاتف المحمول
- تكلفة إضافية لإرسال الرسائل
- مشاكل في التغطية أو التأخير

### البديل 2: Email-based 2FA
```python
# إرسال رمز عبر البريد الإلكتروني
def send_email_code(user):
    code = generate_random_code(8)
    send_email(user.email, "رمز التحقق", f"رمز التحقق: {code}")
    cache.set(f"email_code_{user.id}", code, timeout=600)
```

**المزايا:**
- لا توجد تكلفة إضافية
- سهولة التطبيق
- يعمل في جميع أنحاء العالم

**العيوب:**
- أمان أقل من الطرق الأخرى
- يعتمد على أمان البريد الإلكتروني
- قد يصل للبريد المهمل
- بطء نسبي في الوصول

### البديل 3: TOTP (Time-based OTP) - المختار
```python
# استخدام تطبيقات المصادقة مثل Google Authenticator
import pyotp

def setup_totp(user):
    secret = pyotp.random_base32()
    user.two_factor_secret = secret
    user.save()
    
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email,
        issuer_name="نائبك - منصة المواطن"
    )
    return totp_uri  # لإنشاء QR Code

def verify_totp(user, token):
    totp = pyotp.TOTP(user.two_factor_secret)
    return totp.verify(token, valid_window=1)
```

## القرار المتخذ

اخترنا **TOTP (Time-based One-Time Password)** كطريقة أساسية مع دعم SMS كبديل للأسباب التالية:

### المبررات التقنية

1. **أمان متقدم:**
   - لا يعتمد على الشبكة أثناء التحقق
   - مقاوم لهجمات Man-in-the-Middle
   - رموز متغيرة كل 30 ثانية
   - يعمل حتى بدون اتصال إنترنت

2. **معايير صناعية:**
   - يتبع معيار RFC 6238
   - متوافق مع تطبيقات شائعة (Google Authenticator, Authy)
   - مدعوم من معظم منصات الأمان

3. **تجربة مستخدم محسنة:**
   - سرعة في التحقق (لا انتظار للرسائل)
   - يعمل في جميع أنحاء العالم
   - لا توجد تكاليف إضافية

### التطبيق التقني

```python
class AdminUser(AbstractUser):
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    backup_codes = models.JSONField(default=list, blank=True)
    two_factor_setup_at = models.DateTimeField(null=True, blank=True)
    
    def enable_two_factor(self):
        """تفعيل المصادقة الثنائية"""
        if not self.two_factor_secret:
            self.two_factor_secret = pyotp.random_base32()
        
        self.two_factor_enabled = True
        self.two_factor_setup_at = timezone.now()
        
        # إنشاء رموز احتياطية
        self.backup_codes = [
            secrets.token_hex(4).upper() 
            for _ in range(10)
        ]
        
        self.save()
        
        # تسجيل في سجل النشاطات
        AdminActivity.objects.create(
            admin_user=self,
            action_type='activate',
            action_description='تفعيل المصادقة الثنائية'
        )
    
    def get_qr_code_uri(self):
        """إنشاء URI لرمز QR"""
        if not self.two_factor_secret:
            return None
            
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.provisioning_uri(
            name=f"{self.username}@naebak.gov.eg",
            issuer_name="نائبك - النظام الإداري"
        )
    
    def verify_totp_token(self, token):
        """التحقق من رمز TOTP"""
        if not self.two_factor_enabled or not self.two_factor_secret:
            return False
        
        # فحص الرمز الاحتياطي أولاً
        if token.upper() in self.backup_codes:
            self.backup_codes.remove(token.upper())
            self.save(update_fields=['backup_codes'])
            
            # تسجيل استخدام الرمز الاحتياطي
            AdminActivity.objects.create(
                admin_user=self,
                action_type='login',
                action_description='استخدام رمز احتياطي للمصادقة الثنائية'
            )
            return True
        
        # فحص رمز TOTP
        totp = pyotp.TOTP(self.two_factor_secret)
        is_valid = totp.verify(token, valid_window=1)
        
        if is_valid:
            AdminActivity.objects.create(
                admin_user=self,
                action_type='login',
                action_description='تسجيل دخول بالمصادقة الثنائية'
            )
        
        return is_valid
```

### نظام الرموز الاحتياطية

```python
def generate_backup_codes(count=10):
    """إنشاء رموز احتياطية للطوارئ"""
    return [
        f"{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}"
        for _ in range(count)
    ]

def use_backup_code(user, code):
    """استخدام رمز احتياطي"""
    if code.upper() in user.backup_codes:
        user.backup_codes.remove(code.upper())
        user.save(update_fields=['backup_codes'])
        
        # تنبيه إذا بقي أقل من 3 رموز
        if len(user.backup_codes) < 3:
            send_low_backup_codes_alert(user)
        
        return True
    return False
```

### تكامل مع نظام تسجيل الدخول

```python
class TwoFactorLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        totp_token = request.data.get('totp_token')
        
        # التحقق من اسم المستخدم وكلمة المرور
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'بيانات دخول خاطئة'}, status=400)
        
        # فحص قفل الحساب
        if user.is_account_locked:
            return Response({'error': 'الحساب مقفل'}, status=423)
        
        # فحص المصادقة الثنائية
        if user.two_factor_enabled:
            if not totp_token:
                return Response({
                    'requires_2fa': True,
                    'message': 'يرجى إدخال رمز المصادقة الثنائية'
                }, status=200)
            
            if not user.verify_totp_token(totp_token):
                user.failed_login_attempts += 1
                user.save()
                return Response({'error': 'رمز المصادقة الثنائية خاطئ'}, status=400)
        
        # تسجيل دخول ناجح
        login(request, user)
        user.failed_login_attempts = 0
        user.last_login = timezone.now()
        user.save()
        
        return Response({'success': True, 'token': generate_jwt_token(user)})
```

## العواقب

### النتائج الإيجابية

1. **أمان محسن بشكل كبير:**
   - حماية قوية ضد اختراق الحسابات
   - مقاومة لمعظم أنواع الهجمات الشائعة
   - تقليل مخاطر الوصول غير المصرح به

2. **مرونة في الاستخدام:**
   - دعم تطبيقات متعددة للمصادقة
   - رموز احتياطية للطوارئ
   - إمكانية إعادة التعيين عند الحاجة

3. **امتثال للمعايير:**
   - يتبع أفضل الممارسات الأمنية
   - متوافق مع معايير الحكومة الإلكترونية
   - قابل للتدقيق والمراجعة

### التحديات المحتملة

1. **منحنى التعلم:**
   - قد يحتاج المستخدمون لتعلم استخدام التطبيقات
   - الحاجة لتدريب وتوجيه أولي

2. **إدارة الطوارئ:**
   - التعامل مع فقدان الهاتف أو التطبيق
   - الحاجة لإجراءات استرداد واضحة

### استراتيجيات التخفيف

1. **دليل المستخدم الشامل:**
```markdown
# دليل إعداد المصادقة الثنائية

## الخطوة 1: تحميل التطبيق
- Google Authenticator (مجاني)
- Microsoft Authenticator (مجاني)
- Authy (مجاني مع نسخ احتياطي)

## الخطوة 2: مسح رمز QR
1. افتح التطبيق
2. اضغط على "إضافة حساب"
3. امسح الرمز المعروض
4. احفظ الرموز الاحتياطية في مكان آمن
```

2. **نظام الدعم المتقدم:**
```python
class TwoFactorRecovery:
    def initiate_recovery(self, user, admin_approver):
        """بدء عملية استرداد المصادقة الثنائية"""
        recovery_request = RecoveryRequest.objects.create(
            user=user,
            requested_by=admin_approver,
            status='pending',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # إرسال تنبيه للمديرين العامين
        notify_super_admins(
            f'طلب استرداد مصادقة ثنائية للمستخدم {user.username}',
            recovery_request
        )
        
        return recovery_request
```

3. **مراقبة وتنبيهات:**
   - تتبع محاولات المصادقة الفاشلة
   - تنبيهات عند استخدام الرموز الاحتياطية
   - إحصائيات عن معدلات النجاح

## المراجعة والتقييم

### معايير النجاح
- معدل تفعيل المصادقة الثنائية > 95% للمديرين
- تقليل حوادث اختراق الحسابات بنسبة > 99%
- رضا المستخدمين عن سهولة الاستخدام > 85%

### مؤشرات المراقبة
- عدد المستخدمين المفعلين للمصادقة الثنائية
- معدل نجاح التحقق من الرموز
- عدد طلبات الاسترداد شهرياً
- أنماط استخدام الرموز الاحتياطية

### جدولة المراجعة
- **مراجعة شهرية:** إحصائيات الاستخدام والأمان
- **مراجعة ربع سنوية:** تقييم فعالية النظام
- **مراجعة سنوية:** تحديث الاستراتيجية والتقنيات

---

**تاريخ الإنشاء:** سبتمبر 2024  
**المؤلف:** فريق الأمان - نائبك  
**المراجعون:** فريق التطوير، فريق تجربة المستخدم  
**الحالة:** مقبول ومطبق
