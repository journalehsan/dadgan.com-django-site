from django import forms
from django.core.validators import RegexValidator
from .models import ContactMessage, ConsultationRequest, Question, Answer, ConsultationType


class ContactForm(forms.ModelForm):
    phone_validator = RegexValidator(
        regex=r'^09\d{9}$',
        message="شماره موبایل باید با 09 شروع شده و 11 رقم باشد."
    )
    
    phone = forms.CharField(
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border rounded-lg dark:bg-gray-800 dark:border-gray-600 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none transition-colors',
            'placeholder': '09xxxxxxxxx'
        })
    )

    class Meta:
        model = ContactMessage
        fields = ['full_name', 'phone', 'email', 'subject']
        
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full p-3 border rounded-lg dark:bg-gray-800 dark:border-gray-600 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none transition-colors',
                'placeholder': 'نام کامل خود را وارد کنید'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-3 border rounded-lg dark:bg-gray-800 dark:border-gray-600 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none transition-colors',
                'placeholder': 'example@email.com (اختیاری)'
            }),
            'subject': forms.Textarea(attrs={
                'class': 'w-full p-3 border rounded-lg h-32 dark:bg-gray-800 dark:border-gray-600 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none transition-colors resize-none',
                'placeholder': 'لطفاً موضوع مورد نظر خود را به طور کامل شرح دهید...',
                'rows': 4
            })
        }

        labels = {
            'full_name': 'نام و نام خانوادگی *',
            'phone': 'شماره تماس *',
            'email': 'ایمیل',
            'subject': 'موضوع مشاوره *'
        }

    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if len(subject) < 10:
            raise forms.ValidationError('موضوع مشاوره باید حداقل 10 کاراکتر باشد.')
        return subject


class ConsultationForm(forms.ModelForm):
    phone_validator = RegexValidator(
        regex=r'^09\d{9}$',
        message="شماره موبایل باید با 09 شروع شده و 11 رقم باشد."
    )
    
    phone = forms.CharField(
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 rounded-lg bg-white/20 border border-white/30 placeholder-white/70 text-white focus:outline-none focus:border-white/60 transition-colors',
            'placeholder': '09xxxxxxxxx'
        })
    )

    class Meta:
        model = ConsultationRequest
        fields = ['full_name', 'phone', 'email', 'consultation_type', 'field', 'description']
        
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full p-3 rounded-lg bg-white/20 border border-white/30 placeholder-white/70 text-white focus:outline-none focus:border-white/60 transition-colors',
                'placeholder': 'نام کامل خود را وارد کنید'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-3 rounded-lg bg-white/20 border border-white/30 placeholder-white/70 text-white focus:outline-none focus:border-white/60 transition-colors',
                'placeholder': 'example@email.com (اختیاری)'
            }),
            'consultation_type': forms.Select(attrs={
                'class': 'w-full p-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:border-white/60 transition-colors'
            }),
            'field': forms.Select(attrs={
                'class': 'w-full p-3 rounded-lg bg-white/20 border border-white/30 text-white focus:outline-none focus:border-white/60 transition-colors'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-3 rounded-lg bg-white/20 border border-white/30 placeholder-white/70 text-white focus:outline-none focus:border-white/60 transition-colors resize-none',
                'placeholder': 'لطفاً مسئله خود را به طور خلاصه شرح دهید...',
                'rows': 4
            })
        }

        labels = {
            'full_name': 'نام و نام خانوادگی',
            'phone': 'شماره موبایل',
            'email': 'ایمیل',
            'consultation_type': 'نوع مشاوره',
            'field': 'زمینه مشاوره',
            'description': 'توضیح کوتاه مسئله'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['consultation_type'].queryset = ConsultationType.objects.filter(is_active=True)


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'content', 'asker_name', 'asker_email', 'category']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 dark:bg-gray-700 dark:text-white',
                'placeholder': 'عنوان سوال خود را وارد کنید...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 dark:bg-gray-700 dark:text-white resize-none',
                'placeholder': 'سوال خود را به تفصیل شرح دهید...',
                'rows': 6
            }),
            'asker_name': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 dark:bg-gray-700 dark:text-white',
                'placeholder': 'نام شما'
            }),
            'asker_email': forms.EmailInput(attrs={
                'class': 'w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 dark:bg-gray-700 dark:text-white',
                'placeholder': 'ایمیل شما'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 dark:bg-gray-700 dark:text-white'
            })
        }

        labels = {
            'title': 'عنوان سوال',
            'content': 'متن سوال',
            'asker_name': 'نام شما',
            'asker_email': 'ایمیل شما',
            'category': 'دسته‌بندی'
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('عنوان سوال باید حداقل 5 کاراکتر باشد.')
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 20:
            raise forms.ValidationError('متن سوال باید حداقل 20 کاراکتر باشد.')
        return content


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content', 'answerer_name', 'answerer_title']
        
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full p-4 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white resize-none',
                'placeholder': 'پاسخ خود را وارد کنید...',
                'rows': 6
            }),
            'answerer_name': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white',
                'placeholder': 'نام شما'
            }),
            'answerer_title': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white',
                'placeholder': 'عنوان یا تخصص شما (اختیاری)'
            })
        }

        labels = {
            'content': 'متن پاسخ',
            'answerer_name': 'نام شما',
            'answerer_title': 'عنوان/تخصص'
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 10:
            raise forms.ValidationError('پاسخ باید حداقل 10 کاراکتر باشد.')
        return content


class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-r-lg focus:outline-none focus:ring-2 focus:ring-orange-500 dark:bg-gray-700 dark:text-white',
            'placeholder': 'جستجو در سوالات...'
        }),
        label=''
    )