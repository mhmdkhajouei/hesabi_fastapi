<div dir="rtl" align="right">

# Git Workflow & Repository Guidelines

این مستند شامل استانداردهای مدیریت نسخه (Version Control)، قوانین پوش کردن کد و ساختار شاخه‌ها برای پروژه حسابی است.

---

## 1. Branching Strategy (GitHub Flow)

در این پروژه از الگوی GitHub Flow استفاده می‌شود:

* **main**: شاخه اصلی و پایدار پروژه. کدهای این شاخه همیشه باید بدون ارور، تست‌شده و آماده اجرا باشند. هیچ کامیت مستقیمی روی این شاخه انجام نمی‌شود.
* **feat/<week-or-feature-name>**: شاخه‌های فرعی برای توسعه کارهای هر هفته یا فیچرهای مجزا (مانند `feat/week2-alembic-config`).

---

## 2. Protection Rules & Repository Settings

تنظیمات زیر روی ریپازیتوری گیت‌هاب اعمال شده‌اند تا از سلامت کدهای شاخه اصلی محافظت شود:

### الف) Branch Protection / Ruleset (main)
* **Require a pull request before merging:** تمامی تغییرات باید ابتدا روی شاخه فرعی توسعه یافته و از طریق Pull Request به main منتقل شوند.
* **Required approvals = 0:** با توجه به تک‌نفره بودن تیم توسعه، نیاز به تاییدیه سایر اعضا نیست، اما ساخت Pull Request الزامی است.

### ب) Automatic Cleanup
* **Automatically delete head branches:** پس از ادغام موفق یک Pull Request، شاخه فرعی به طور خودکار پاک می‌شود تا محیط ریپازیتوری تمیز بماند.

---

## 3. Commit Message Convention (Conventional Commits)

برای خوانایی تاریخچه پروژه، پیام‌های کامیت باید با یکی از پیشوندهای استاندارد زیر شروع شوند:

* **feat:** افزودن یک قابلیت یا فیچر جدید (مانند `feat: setup pydantic settings`)
* **fix:** رفع یک باگ یا مشکل فنی (مانند `fix: resolve alembic migration conflict`)
* **refactor:** بازنویسی یا تمیزکاری کد بدون تغییر در رفتار سیستم (مانند `refactor: replace os.environ with settings object`)
* **docs:** افزودن یا ویرایش مستندات پروژه (مانند `docs: add ADR-003 migration strategy`)
* **chore:** کارهای زیرساختی و نگهداری (مانند `chore: update .gitignore rules`)

---

## 4. Step-by-Step Development Workflow

برای توسعه هر هفته یا فیچر جدید، مراحل زیر به ترتیب طی می‌شوند:

* **گام اول: بروزرسانی شاخه اصلی و ساخت شاخه جدید**
  ```bash
  git checkout main
  git pull origin main
  git checkout -b feat/weekX-topic-name

* **گام دوم: توسعه و ثبت کامیت‌های خرد**

```Bash
git add .
git commit -m "feat: <description>"
```
* **گام سوم: پوش کردن شاخه فرعی به گیت‌هاب**

```Bash
git push -u origin feat/weekX-topic-name
```
* **گام چهارم: ایجاد و ادغام Pull Request در گیت‌هاب**

مراجعه به صفحه اصلی ریپازیتوری در گیت‌هاب.

کلیک روی گزینه Compare & pull request.

ثبت توضیحات خلاصه از کارهای انجام‌شده و کلیک روی Create pull request.

بررسی نهایی تغییرات و کلیک روی Merge pull request و سپس Confirm merge.

</div>