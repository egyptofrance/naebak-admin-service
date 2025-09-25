"""
Management command لتحميل البيانات الأساسية لخدمة الإدارة - مشروع نائبك
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from apps.admin.models import (
    Governorate, Party, ComplaintType, AdminRole, 
    AdminUser, SystemSettings, AdminSettings
)


class Command(BaseCommand):
    help = 'تحميل البيانات الأساسية لخدمة الإدارة'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='حذف البيانات الموجودة وإعادة تحميلها',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('بدء تحميل البيانات الأساسية لخدمة الإدارة...')
        )

        try:
            with transaction.atomic():
                if options['reset']:
                    self.stdout.write('حذف البيانات الموجودة...')
                    self.reset_data()

                self.load_governorates()
                self.load_parties()
                self.load_complaint_types()
                self.load_admin_roles()
                self.load_system_settings()
                self.load_admin_settings()

            self.stdout.write(
                self.style.SUCCESS('تم تحميل البيانات الأساسية بنجاح!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'خطأ في تحميل البيانات: {str(e)}')
            )
            raise

    def reset_data(self):
        """حذف البيانات الموجودة"""
        models_to_reset = [
            SystemSettings, AdminSettings, ComplaintType, 
            Party, Governorate
        ]
        
        for model in models_to_reset:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f'تم حذف {count} سجل من {model.__name__}')

    def load_governorates(self):
        """تحميل المحافظات المصرية"""
        governorates_data = [
            {
                'name': 'القاهرة', 'name_en': 'Cairo', 'code': 'CAI',
                'region': 'cairo', 'capital': 'القاهرة',
                'area_km2': 606, 'population': 10230350, 'display_order': 1
            },
            {
                'name': 'الجيزة', 'name_en': 'Giza', 'code': 'GIZ',
                'region': 'cairo', 'capital': 'الجيزة',
                'area_km2': 13184, 'population': 9200000, 'display_order': 2
            },
            {
                'name': 'القليوبية', 'name_en': 'Qalyubia', 'code': 'QLY',
                'region': 'cairo', 'capital': 'بنها',
                'area_km2': 1124, 'population': 5915000, 'display_order': 3
            },
            {
                'name': 'الإسكندرية', 'name_en': 'Alexandria', 'code': 'ALX',
                'region': 'delta', 'capital': 'الإسكندرية',
                'area_km2': 2300, 'population': 5450000, 'display_order': 4
            },
            {
                'name': 'البحيرة', 'name_en': 'Beheira', 'code': 'BEH',
                'region': 'delta', 'capital': 'دمنهور',
                'area_km2': 9826, 'population': 6500000, 'display_order': 5
            },
            {
                'name': 'المنوفية', 'name_en': 'Monufia', 'code': 'MNF',
                'region': 'delta', 'capital': 'شبين الكوم',
                'area_km2': 2499, 'population': 4500000, 'display_order': 6
            },
            {
                'name': 'الغربية', 'name_en': 'Gharbia', 'code': 'GHR',
                'region': 'delta', 'capital': 'طنطا',
                'area_km2': 1942, 'population': 5100000, 'display_order': 7
            },
            {
                'name': 'كفر الشيخ', 'name_en': 'Kafr el-Sheikh', 'code': 'KFS',
                'region': 'delta', 'capital': 'كفر الشيخ',
                'area_km2': 3437, 'population': 3400000, 'display_order': 8
            },
            {
                'name': 'الدقهلية', 'name_en': 'Dakahlia', 'code': 'DKH',
                'region': 'delta', 'capital': 'المنصورة',
                'area_km2': 3459, 'population': 6700000, 'display_order': 9
            },
            {
                'name': 'دمياط', 'name_en': 'Damietta', 'code': 'DMT',
                'region': 'delta', 'capital': 'دمياط',
                'area_km2': 910, 'population': 1500000, 'display_order': 10
            },
            {
                'name': 'الشرقية', 'name_en': 'Sharqia', 'code': 'SHR',
                'region': 'delta', 'capital': 'الزقازيق',
                'area_km2': 4180, 'population': 7500000, 'display_order': 11
            },
            {
                'name': 'بورسعيد', 'name_en': 'Port Said', 'code': 'PTS',
                'region': 'canal', 'capital': 'بورسعيد',
                'area_km2': 1345, 'population': 750000, 'display_order': 12
            },
            {
                'name': 'الإسماعيلية', 'name_en': 'Ismailia', 'code': 'ISM',
                'region': 'canal', 'capital': 'الإسماعيلية',
                'area_km2': 1442, 'population': 1400000, 'display_order': 13
            },
            {
                'name': 'السويس', 'name_en': 'Suez', 'code': 'SUZ',
                'region': 'canal', 'capital': 'السويس',
                'area_km2': 9002, 'population': 750000, 'display_order': 14
            },
            {
                'name': 'شمال سيناء', 'name_en': 'North Sinai', 'code': 'NSI',
                'region': 'sinai', 'capital': 'العريش',
                'area_km2': 27574, 'population': 450000, 'display_order': 15
            },
            {
                'name': 'جنوب سيناء', 'name_en': 'South Sinai', 'code': 'SSI',
                'region': 'sinai', 'capital': 'الطور',
                'area_km2': 31272, 'population': 200000, 'display_order': 16
            },
            {
                'name': 'البحر الأحمر', 'name_en': 'Red Sea', 'code': 'RSE',
                'region': 'red_sea', 'capital': 'الغردقة',
                'area_km2': 203685, 'population': 400000, 'display_order': 17
            },
            {
                'name': 'الفيوم', 'name_en': 'Faiyum', 'code': 'FYM',
                'region': 'upper', 'capital': 'الفيوم',
                'area_km2': 6068, 'population': 3700000, 'display_order': 18
            },
            {
                'name': 'بني سويف', 'name_en': 'Beni Suef', 'code': 'BSW',
                'region': 'upper', 'capital': 'بني سويف',
                'area_km2': 10954, 'population': 3300000, 'display_order': 19
            },
            {
                'name': 'المنيا', 'name_en': 'Minya', 'code': 'MNY',
                'region': 'upper', 'capital': 'المنيا',
                'area_km2': 32279, 'population': 5700000, 'display_order': 20
            },
            {
                'name': 'أسيوط', 'name_en': 'Asyut', 'code': 'ASY',
                'region': 'upper', 'capital': 'أسيوط',
                'area_km2': 25926, 'population': 4500000, 'display_order': 21
            },
            {
                'name': 'الوادي الجديد', 'name_en': 'New Valley', 'code': 'NVL',
                'region': 'upper', 'capital': 'الخارجة',
                'area_km2': 376505, 'population': 250000, 'display_order': 22
            },
            {
                'name': 'سوهاج', 'name_en': 'Sohag', 'code': 'SOH',
                'region': 'upper', 'capital': 'سوهاج',
                'area_km2': 11218, 'population': 5200000, 'display_order': 23
            },
            {
                'name': 'قنا', 'name_en': 'Qena', 'code': 'QNA',
                'region': 'upper', 'capital': 'قنا',
                'area_km2': 8980, 'population': 3200000, 'display_order': 24
            },
            {
                'name': 'الأقصر', 'name_en': 'Luxor', 'code': 'LXR',
                'region': 'upper', 'capital': 'الأقصر',
                'area_km2': 2409, 'population': 1400000, 'display_order': 25
            },
            {
                'name': 'أسوان', 'name_en': 'Aswan', 'code': 'ASW',
                'region': 'upper', 'capital': 'أسوان',
                'area_km2': 62726, 'population': 1600000, 'display_order': 26
            },
            {
                'name': 'مطروح', 'name_en': 'Matrouh', 'code': 'MTR',
                'region': 'red_sea', 'capital': 'مرسى مطروح',
                'area_km2': 166563, 'population': 500000, 'display_order': 27
            },
        ]

        created_count = 0
        for gov_data in governorates_data:
            governorate, created = Governorate.objects.get_or_create(
                code=gov_data['code'],
                defaults=gov_data
            )
            if created:
                created_count += 1

        self.stdout.write(f'تم إنشاء {created_count} محافظة')

    def load_parties(self):
        """تحميل الأحزاب السياسية"""
        parties_data = [
            {
                'name': 'حزب الوفد', 'name_en': 'Al-Wafd Party', 'abbreviation': 'الوفد',
                'description': 'حزب سياسي مصري تأسس عام 1919',
                'founded_date': '1919-01-01', 'color': '#0066CC', 'display_order': 1
            },
            {
                'name': 'الحزب الوطني الديمقراطي', 'name_en': 'National Democratic Party', 
                'abbreviation': 'الوطني', 'description': 'حزب سياسي مصري',
                'color': '#FF6600', 'display_order': 2
            },
            {
                'name': 'حزب النور', 'name_en': 'Al-Nour Party', 'abbreviation': 'النور',
                'description': 'حزب سياسي إسلامي', 'color': '#FFD700', 'display_order': 3
            },
            {
                'name': 'حزب المصريين الأحرار', 'name_en': 'Free Egyptians Party', 
                'abbreviation': 'المصريين الأحرار', 'description': 'حزب ليبرالي مصري',
                'color': '#800080', 'display_order': 4
            },
            {
                'name': 'حزب الغد', 'name_en': 'Al-Ghad Party', 'abbreviation': 'الغد',
                'description': 'حزب سياسي ليبرالي', 'color': '#008000', 'display_order': 5
            },
            {
                'name': 'حزب التجمع', 'name_en': 'Tagammu Party', 'abbreviation': 'التجمع',
                'description': 'حزب التجمع الوطني التقدمي الوحدوي',
                'color': '#DC143C', 'display_order': 6
            },
            {
                'name': 'حزب الكرامة', 'name_en': 'Al-Karama Party', 'abbreviation': 'الكرامة',
                'description': 'حزب الكرامة المصري', 'color': '#8B4513', 'display_order': 7
            },
            {
                'name': 'حزب الإصلاح والتنمية', 'name_en': 'Reform and Development Party', 
                'abbreviation': 'الإصلاح والتنمية', 'description': 'حزب سياسي مصري',
                'color': '#4169E1', 'display_order': 8
            },
            {
                'name': 'حزب الشعب الجمهوري', 'name_en': 'Republican People\'s Party', 
                'abbreviation': 'الشعب الجمهوري', 'description': 'حزب سياسي مصري',
                'color': '#FF1493', 'display_order': 9
            },
            {
                'name': 'حزب مستقبل وطن', 'name_en': 'Future of a Nation Party', 
                'abbreviation': 'مستقبل وطن', 'description': 'حزب سياسي مصري',
                'color': '#FF4500', 'display_order': 10
            },
            {
                'name': 'حزب الحرية المصري', 'name_en': 'Egyptian Freedom Party', 
                'abbreviation': 'الحرية المصري', 'description': 'حزب سياسي مصري',
                'color': '#32CD32', 'display_order': 11
            },
            {
                'name': 'حزب الوسط', 'name_en': 'Al-Wasat Party', 'abbreviation': 'الوسط',
                'description': 'حزب الوسط المصري', 'color': '#9932CC', 'display_order': 12
            },
            {
                'name': 'مستقل', 'name_en': 'Independent', 'abbreviation': 'مستقل',
                'description': 'مرشحون مستقلون غير منتمين لأحزاب',
                'color': '#808080', 'display_order': 13
            },
        ]

        created_count = 0
        for party_data in parties_data:
            # تحويل التاريخ إذا كان موجوداً
            if 'founded_date' in party_data and party_data['founded_date']:
                from datetime import datetime
                party_data['founded_date'] = datetime.strptime(
                    party_data['founded_date'], '%Y-%m-%d'
                ).date()

            party, created = Party.objects.get_or_create(
                abbreviation=party_data['abbreviation'],
                defaults=party_data
            )
            if created:
                created_count += 1

        self.stdout.write(f'تم إنشاء {created_count} حزب سياسي')

    def load_complaint_types(self):
        """تحميل أنواع الشكاوى"""
        complaint_types_data = [
            {
                'name': 'البنية التحتية والطرق', 'name_en': 'Infrastructure and Roads',
                'category': 'infrastructure', 'icon': '🛣️', 'color': '#FF6B35',
                'priority_level': 'medium', 'estimated_resolution_days': 45,
                'requires_attachments': True, 'max_attachments': 5, 'display_order': 1
            },
            {
                'name': 'الخدمات الصحية', 'name_en': 'Health Services',
                'category': 'health', 'icon': '🏥', 'color': '#E74C3C',
                'priority_level': 'high', 'estimated_resolution_days': 15,
                'requires_attachments': True, 'max_attachments': 3, 'display_order': 2
            },
            {
                'name': 'التعليم والمدارس', 'name_en': 'Education and Schools',
                'category': 'education', 'icon': '🏫', 'color': '#3498DB',
                'priority_level': 'medium', 'estimated_resolution_days': 30,
                'requires_attachments': False, 'max_attachments': 2, 'display_order': 3
            },
            {
                'name': 'المياه والصرف الصحي', 'name_en': 'Water and Sanitation',
                'category': 'utilities', 'icon': '💧', 'color': '#1ABC9C',
                'priority_level': 'high', 'estimated_resolution_days': 20,
                'requires_attachments': True, 'max_attachments': 4, 'display_order': 4
            },
            {
                'name': 'النقل والمواصلات', 'name_en': 'Transportation',
                'category': 'transportation', 'icon': '🚌', 'color': '#9B59B6',
                'priority_level': 'medium', 'estimated_resolution_days': 25,
                'requires_attachments': False, 'max_attachments': 3, 'display_order': 5
            },
            {
                'name': 'البيئة والنظافة', 'name_en': 'Environment and Cleanliness',
                'category': 'environment', 'icon': '🌱', 'color': '#27AE60',
                'priority_level': 'medium', 'estimated_resolution_days': 15,
                'requires_attachments': True, 'max_attachments': 5, 'display_order': 6
            },
            {
                'name': 'الخدمات الاجتماعية', 'name_en': 'Social Services',
                'category': 'social', 'icon': '👥', 'color': '#F39C12',
                'priority_level': 'medium', 'estimated_resolution_days': 35,
                'requires_attachments': False, 'max_attachments': 2, 'display_order': 7
            },
            {
                'name': 'الشؤون الاقتصادية', 'name_en': 'Economic Affairs',
                'category': 'economic', 'icon': '💰', 'color': '#E67E22',
                'priority_level': 'low', 'estimated_resolution_days': 60,
                'requires_attachments': True, 'max_attachments': 10, 'display_order': 8
            },
            {
                'name': 'الشؤون القانونية', 'name_en': 'Legal Affairs',
                'category': 'legal', 'icon': '⚖️', 'color': '#34495E',
                'priority_level': 'high', 'estimated_resolution_days': 90,
                'requires_attachments': True, 'max_attachments': 15, 'display_order': 9
            },
            {
                'name': 'الأمن والسلامة', 'name_en': 'Security and Safety',
                'category': 'security', 'icon': '🛡️', 'color': '#C0392B',
                'priority_level': 'urgent', 'estimated_resolution_days': 7,
                'requires_attachments': True, 'max_attachments': 8, 'display_order': 10
            },
            {
                'name': 'الإسكان والعقارات', 'name_en': 'Housing and Real Estate',
                'category': 'housing', 'icon': '🏠', 'color': '#8E44AD',
                'priority_level': 'medium', 'estimated_resolution_days': 45,
                'requires_attachments': True, 'max_attachments': 7, 'display_order': 11
            },
            {
                'name': 'الخدمات الإدارية', 'name_en': 'Administrative Services',
                'category': 'administrative', 'icon': '📋', 'color': '#2C3E50',
                'priority_level': 'low', 'estimated_resolution_days': 21,
                'requires_attachments': False, 'max_attachments': 3, 'display_order': 12
            },
            {
                'name': 'الكهرباء والطاقة', 'name_en': 'Electricity and Energy',
                'category': 'utilities', 'icon': '⚡', 'color': '#F1C40F',
                'priority_level': 'high', 'estimated_resolution_days': 10,
                'requires_attachments': True, 'max_attachments': 4, 'display_order': 13
            },
            {
                'name': 'شكاوى أخرى', 'name_en': 'Other Complaints',
                'category': 'other', 'icon': '📝', 'color': '#95A5A6',
                'priority_level': 'medium', 'estimated_resolution_days': 30,
                'requires_attachments': False, 'max_attachments': 5, 'display_order': 14
            },
        ]

        created_count = 0
        for complaint_data in complaint_types_data:
            complaint_type, created = ComplaintType.objects.get_or_create(
                name=complaint_data['name'],
                defaults=complaint_data
            )
            if created:
                created_count += 1

        self.stdout.write(f'تم إنشاء {created_count} نوع شكوى')

    def load_admin_roles(self):
        """تحميل أدوار الإدارة"""
        roles_data = [
            {
                'name': 'مدير عام', 'name_en': 'Super Admin', 'role_type': 'super_admin',
                'description': 'صلاحيات كاملة على النظام', 'is_system_role': True
            },
            {
                'name': 'مشرف المحتوى', 'name_en': 'Content Moderator', 'role_type': 'content_moderator',
                'description': 'إدارة ومراجعة المحتوى والإنجازات', 'is_system_role': True
            },
            {
                'name': 'مشرف الشكاوى', 'name_en': 'Complaint Manager', 'role_type': 'complaint_manager',
                'description': 'إدارة الشكاوى وأنواعها', 'is_system_role': True
            },
            {
                'name': 'مشرف المستخدمين', 'name_en': 'User Manager', 'role_type': 'user_manager',
                'description': 'إدارة المستخدمين والأحزاب', 'is_system_role': True
            },
            {
                'name': 'عارض الإحصائيات', 'name_en': 'Statistics Viewer', 'role_type': 'statistics_viewer',
                'description': 'عرض الإحصائيات والتقارير فقط', 'is_system_role': True
            },
            {
                'name': 'مدير النظام', 'name_en': 'System Admin', 'role_type': 'system_admin',
                'description': 'إدارة إعدادات النظام والخوادم', 'is_system_role': True
            },
            {
                'name': 'محلل البيانات', 'name_en': 'Data Analyst', 'role_type': 'data_analyst',
                'description': 'تحليل البيانات وإنشاء التقارير', 'is_system_role': False
            },
            {
                'name': 'وكيل الدعم', 'name_en': 'Support Agent', 'role_type': 'support_agent',
                'description': 'تقديم الدعم الفني للمستخدمين', 'is_system_role': False
            },
        ]

        created_count = 0
        for role_data in roles_data:
            role, created = AdminRole.objects.get_or_create(
                role_type=role_data['role_type'],
                defaults=role_data
            )
            if created:
                created_count += 1

        self.stdout.write(f'تم إنشاء {created_count} دور إداري')

    def load_system_settings(self):
        """تحميل إعدادات النظام"""
        settings_data = [
            {
                'key': 'site_name', 'name': 'اسم الموقع', 'setting_type': 'string',
                'value': 'نائبك', 'default_value': 'نائبك', 'is_public': True,
                'category': 'general', 'display_order': 1
            },
            {
                'key': 'site_description', 'name': 'وصف الموقع', 'setting_type': 'text',
                'value': 'منصة التواصل بين المواطنين والنواب', 
                'default_value': 'منصة التواصل بين المواطنين والنواب',
                'is_public': True, 'category': 'general', 'display_order': 2
            },
            {
                'key': 'contact_email', 'name': 'بريد التواصل', 'setting_type': 'email',
                'value': 'info@naebak.com', 'default_value': 'info@naebak.com',
                'is_public': True, 'category': 'contact', 'display_order': 3
            },
            {
                'key': 'support_phone', 'name': 'هاتف الدعم', 'setting_type': 'string',
                'value': '+201234567890', 'default_value': '+201234567890',
                'is_public': True, 'category': 'contact', 'display_order': 4
            },
            {
                'key': 'max_complaint_length', 'name': 'الحد الأقصى لطول الشكوى', 'setting_type': 'integer',
                'value': '1500', 'default_value': '1500', 'is_public': False,
                'category': 'complaints', 'display_order': 5
            },
            {
                'key': 'max_message_length', 'name': 'الحد الأقصى لطول الرسالة', 'setting_type': 'integer',
                'value': '500', 'default_value': '500', 'is_public': False,
                'category': 'messaging', 'display_order': 6
            },
            {
                'key': 'enable_ratings', 'name': 'تفعيل التقييمات', 'setting_type': 'boolean',
                'value': 'true', 'default_value': 'true', 'is_public': False,
                'category': 'features', 'display_order': 7
            },
            {
                'key': 'maintenance_mode', 'name': 'وضع الصيانة', 'setting_type': 'boolean',
                'value': 'false', 'default_value': 'false', 'is_public': False,
                'category': 'system', 'display_order': 8
            },
            {
                'key': 'primary_color', 'name': 'اللون الأساسي', 'setting_type': 'color',
                'value': '#007bff', 'default_value': '#007bff', 'is_public': True,
                'category': 'appearance', 'display_order': 9
            },
            {
                'key': 'secondary_color', 'name': 'اللون الثانوي', 'setting_type': 'color',
                'value': '#6c757d', 'default_value': '#6c757d', 'is_public': True,
                'category': 'appearance', 'display_order': 10
            },
        ]

        created_count = 0
        for setting_data in settings_data:
            setting, created = SystemSettings.objects.get_or_create(
                key=setting_data['key'],
                defaults=setting_data
            )
            if created:
                created_count += 1

        self.stdout.write(f'تم إنشاء {created_count} إعداد نظام')

    def load_admin_settings(self):
        """تحميل إعدادات الإدارة"""
        if not AdminSettings.objects.exists():
            AdminSettings.objects.create()
            self.stdout.write('تم إنشاء إعدادات الإدارة الافتراضية')
        else:
            self.stdout.write('إعدادات الإدارة موجودة بالفعل')
