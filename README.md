# 🏷️ خدمة الإدارة (naebak-admin-service)

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/egyptofrance/naebak-admin-service/actions)
[![Coverage](https://img.shields.io/badge/coverage-95%25-green)](https://github.com/egyptofrance/naebak-admin-service)
[![Version](https://img.shields.io/badge/version-1.2.0-blue)](https://github.com/egyptofrance/naebak-admin-service/releases)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

## 📝 الوصف

خدمة الإدارة المركزية لمنصة نائبك. توفر واجهة خلفية قوية لإدارة جميع جوانب النظام، بما في ذلك المستخدمين، الشكاوى، المحتوى، والإعدادات العامة. تقتصر هذه الخدمة على المسؤولين والمشرفين فقط.

---

## ✨ الميزات الرئيسية

- **إدارة المستخدمين**: إدارة كاملة لحسابات المستخدمين وصلاحياتهم.
- **إدارة المحتوى**: التحكم في المحتوى المعروض في التطبيق (مقالات، إعلانات).
- **لوحة تحكم شاملة**: عرض إحصائيات وتقارير حول أداء النظام.
- **إدارة الإعدادات**: التحكم في إعدادات النظام العامة.

---

## 🛠️ التقنيات المستخدمة

| التقنية | الإصدار | الغرض |
|---------|---------|-------|
| **Django** | 4.2.5 | إطار العمل الأساسي |
| **Django REST Framework** | 3.14.0 | تطوير APIs |
| **PostgreSQL** | 13+ | قاعدة البيانات الرئيسية |
| **Redis** | 6+ | التخزين المؤقت |

---

## 🚀 التثبيت والتشغيل

```bash
git clone https://github.com/egyptofrance/naebak-admin-service.git
cd naebak-admin-service

# اتبع نفس خطوات التثبيت والتشغيل لباقي خدمات Django
```

---

## 📚 توثيق الـ API

- **Swagger UI**: [http://localhost:8002/api/docs/](http://localhost:8002/api/docs/)

---

## 🤝 المساهمة

يرجى مراجعة [دليل المساهمة](CONTRIBUTING.md) و [معايير التوثيق الموحدة](../../naebak-almakhzan/DOCUMENTATION_STANDARDS.md).

---

## 📄 الترخيص

هذا المشروع مرخص تحت [رخصة MIT](LICENSE).

