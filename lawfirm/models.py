from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="نامک")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ['name']

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="نامک")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="نویسنده")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="دسته‌بندی")
    excerpt = models.TextField(max_length=300, verbose_name="خلاصه")
    content = models.TextField(verbose_name="محتوا")
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True, verbose_name="تصویر")
    published = models.BooleanField(default=False, verbose_name="منتشر شده")
    featured = models.BooleanField(default=False, verbose_name="ویژه")
    views = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ آپدیت")

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('lawfirm:blog_detail', kwargs={'slug': self.slug})

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])


class QACategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="نامک")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "دسته‌بندی پرسش و پاسخ"
        verbose_name_plural = "دسته‌بندی‌های پرسش و پاسخ"
        ordering = ['name']

    def __str__(self):
        return self.name


class Question(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان سوال")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="نامک")
    content = models.TextField(verbose_name="متن سوال")
    asker_name = models.CharField(max_length=100, verbose_name="نام پرسنده")
    asker_email = models.EmailField(verbose_name="ایمیل پرسنده")
    category = models.ForeignKey(QACategory, on_delete=models.CASCADE, verbose_name="دسته‌بندی")
    views = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    votes = models.IntegerField(default=0, verbose_name="امتیاز")
    is_answered = models.BooleanField(default=False, verbose_name="پاسخ داده شده")
    is_published = models.BooleanField(default=False, verbose_name="منتشر شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ آپدیت")

    class Meta:
        verbose_name = "سوال"
        verbose_name_plural = "سوالات"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('lawfirm:qa_detail', kwargs={'slug': self.slug})

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def get_best_answer(self):
        return self.answers.filter(is_best_answer=True).first()

    def get_answers_count(self):
        return self.answers.count()


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE, verbose_name="سوال")
    content = models.TextField(verbose_name="متن پاسخ")
    answerer_name = models.CharField(max_length=100, verbose_name="نام پاسخ‌دهنده")
    answerer_title = models.CharField(max_length=100, blank=True, verbose_name="عنوان پاسخ‌دهنده")
    votes = models.IntegerField(default=0, verbose_name="امتیاز")
    is_best_answer = models.BooleanField(default=False, verbose_name="بهترین پاسخ")
    is_published = models.BooleanField(default=False, verbose_name="منتشر شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ آپدیت")

    class Meta:
        verbose_name = "پاسخ"
        verbose_name_plural = "پاسخ‌ها"
        ordering = ['-is_best_answer', '-votes', 'created_at']

    def __str__(self):
        return f"پاسخ {self.answerer_name} به {self.question.title}"

    def save(self, *args, **kwargs):
        # If this answer is marked as best answer, unmark others
        if self.is_best_answer:
            Answer.objects.filter(question=self.question, is_best_answer=True).update(is_best_answer=False)
            # Update question as answered
            self.question.is_answered = True
            self.question.save(update_fields=['is_answered'])
        super().save(*args, **kwargs)


class ConsultationType(models.Model):
    name = models.CharField(max_length=100, verbose_name="نوع مشاوره")
    price = models.PositiveIntegerField(verbose_name="قیمت (تومان)")
    duration = models.PositiveIntegerField(verbose_name="مدت زمان (دقیقه)")
    description = models.TextField(verbose_name="توضیحات")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "نوع مشاوره"
        verbose_name_plural = "انواع مشاوره"
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - {self.price:,} تومان"


class ConsultationRequest(models.Model):
    CONSULTATION_FIELDS = [
        ('family', 'حقوق خانواده'),
        ('criminal', 'حقوق کیفری'),
        ('commercial', 'حقوق تجاری'),
        ('civil', 'حقوق مدنی'),
        ('other', 'سایر موارد'),
    ]

    STATUS_CHOICES = [
        ('pending', 'در انتظار بررسی'),
        ('confirmed', 'تأیید شده'),
        ('completed', 'انجام شده'),
        ('cancelled', 'لغو شده'),
    ]

    full_name = models.CharField(max_length=100, verbose_name="نام و نام خانوادگی")
    phone = models.CharField(max_length=15, verbose_name="شماره موبایل")
    email = models.EmailField(blank=True, verbose_name="ایمیل")
    consultation_type = models.ForeignKey(ConsultationType, on_delete=models.CASCADE, verbose_name="نوع مشاوره")
    field = models.CharField(max_length=20, choices=CONSULTATION_FIELDS, verbose_name="زمینه مشاوره")
    description = models.TextField(verbose_name="توضیح مسئله")
    preferred_date = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ مطلوب")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    admin_notes = models.TextField(blank=True, verbose_name="یادداشت مدیر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ درخواست")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ آپدیت")

    class Meta:
        verbose_name = "درخواست مشاوره"
        verbose_name_plural = "درخواست‌های مشاوره"
        ordering = ['-created_at']

    def __str__(self):
        return f"مشاوره {self.full_name} - {self.get_field_display()}"


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="نام و نام خانوادگی")
    phone = models.CharField(max_length=15, verbose_name="شماره تماس")
    email = models.EmailField(blank=True, verbose_name="ایمیل")
    subject = models.TextField(verbose_name="موضوع")
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")
    admin_response = models.TextField(blank=True, verbose_name="پاسخ مدیر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ آپدیت")

    class Meta:
        verbose_name = "پیام تماس"
        verbose_name_plural = "پیام‌های تماس"
        ordering = ['-created_at']

    def __str__(self):
        return f"پیام {self.full_name} - {self.created_at.strftime('%Y/%m/%d')}"


class Testimonial(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام")
    title = models.CharField(max_length=100, blank=True, verbose_name="عنوان/سمت")
    content = models.TextField(verbose_name="متن نظر")
    rating = models.PositiveIntegerField(default=5, verbose_name="امتیاز (1-5)")
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True, verbose_name="تصویر")
    is_published = models.BooleanField(default=True, verbose_name="منتشر شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "نظر مشتری"
        verbose_name_plural = "نظرات مشتریان"
        ordering = ['-created_at']

    def __str__(self):
        return f"نظر {self.name}"

    def get_rating_stars(self):
        return "⭐" * self.rating


class SiteSettings(models.Model):
    site_title = models.CharField(max_length=200, default="مؤسسه حقوقی دادگان", verbose_name="عنوان سایت")
    site_description = models.TextField(verbose_name="توضیحات سایت")
    phone = models.CharField(max_length=15, verbose_name="شماره تماس")
    email = models.EmailField(verbose_name="ایمیل")
    address = models.TextField(verbose_name="آدرس")
    logo = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="لوگو")
    
    # Stats
    consultation_count = models.PositiveIntegerField(default=1400, verbose_name="تعداد مشاوره")
    success_cases = models.PositiveIntegerField(default=950, verbose_name="پرونده موفق")
    contracts_count = models.PositiveIntegerField(default=500, verbose_name="تنظیم قرارداد")
    experience_years = models.PositiveIntegerField(default=12, verbose_name="سال تجربه")

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return self.site_title

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            raise Exception('تنها یک نمونه از تنظیمات سایت مجاز است')
        return super().save(*args, **kwargs)
