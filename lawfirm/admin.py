from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Category, BlogPost, QACategory, Question, Answer,
    ConsultationType, ConsultationRequest, ContactMessage,
    Testimonial, SiteSettings
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ['answerer_name', 'answerer_title', 'content', 'votes', 'is_best_answer', 'is_published']
    readonly_fields = ['votes']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'published', 'featured', 'views', 'created_at']
    list_filter = ['published', 'featured', 'category', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['published', 'featured']
    readonly_fields = ['views', 'created_at', 'updated_at']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('محتوا', {
            'fields': ('excerpt', 'content', 'image')
        }),
        ('تنظیمات', {
            'fields': ('published', 'featured')
        }),
        ('آمار', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(QACategory)
class QACategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'asker_name', 'category', 'votes', 'views', 'is_answered', 'is_published', 'created_at']
    list_filter = ['is_answered', 'is_published', 'category', 'created_at']
    search_fields = ['title', 'content', 'asker_name']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published']
    readonly_fields = ['votes', 'views', 'is_answered', 'created_at', 'updated_at']
    inlines = [AnswerInline]
    
    fieldsets = (
        ('اطلاعات سوال', {
            'fields': ('title', 'slug', 'content', 'category')
        }),
        ('اطلاعات پرسنده', {
            'fields': ('asker_name', 'asker_email')
        }),
        ('تنظیمات', {
            'fields': ('is_published',)
        }),
        ('آمار', {
            'fields': ('votes', 'views', 'is_answered', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question_title', 'answerer_name', 'answerer_title', 'votes', 'is_best_answer', 'is_published', 'created_at']
    list_filter = ['is_best_answer', 'is_published', 'created_at']
    search_fields = ['content', 'answerer_name', 'question__title']
    list_editable = ['is_best_answer', 'is_published']
    readonly_fields = ['votes', 'created_at', 'updated_at']

    def question_title(self, obj):
        return obj.question.title[:50] + '...' if len(obj.question.title) > 50 else obj.question.title
    question_title.short_description = 'سوال'


@admin.register(ConsultationType)
class ConsultationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'formatted_price', 'duration', 'is_active']
    list_editable = ['is_active']
    list_filter = ['is_active']

    def formatted_price(self, obj):
        return f"{obj.price:,} تومان"
    formatted_price.short_description = 'قیمت'


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'consultation_type', 'get_field_display', 'status', 'created_at']
    list_filter = ['status', 'field', 'consultation_type', 'created_at']
    search_fields = ['full_name', 'phone', 'description']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('اطلاعات متقاضی', {
            'fields': ('full_name', 'phone', 'email')
        }),
        ('جزئیات مشاوره', {
            'fields': ('consultation_type', 'field', 'description', 'preferred_date')
        }),
        ('مدیریت', {
            'fields': ('status', 'admin_notes')
        }),
        ('زمان‌بندی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('consultation_type')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'subject_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['full_name', 'phone', 'subject']
    list_editable = ['is_read']
    readonly_fields = ['created_at', 'updated_at']

    def subject_preview(self, obj):
        return obj.subject[:50] + '...' if len(obj.subject) > 50 else obj.subject
    subject_preview.short_description = 'موضوع'

    fieldsets = (
        ('اطلاعات پیام', {
            'fields': ('full_name', 'phone', 'email', 'subject')
        }),
        ('مدیریت', {
            'fields': ('is_read', 'admin_response')
        }),
        ('زمان‌بندی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'rating_display', 'is_published', 'created_at']
    list_filter = ['rating', 'is_published', 'created_at']
    search_fields = ['name', 'content']
    list_editable = ['is_published']

    def rating_display(self, obj):
        return "⭐" * obj.rating
    rating_display.short_description = 'امتیاز'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('اطلاعات سایت', {
            'fields': ('site_title', 'site_description', 'logo')
        }),
        ('اطلاعات تماس', {
            'fields': ('phone', 'email', 'address')
        }),
        ('آمار سایت', {
            'fields': ('consultation_count', 'success_cases', 'contracts_count', 'experience_years')
        })
    )

    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False


# Admin site customization
admin.site.site_header = "مدیریت مؤسسه حقوقی دادگان"
admin.site.site_title = "دادگان"
admin.site.index_title = "پنل مدیریت"
