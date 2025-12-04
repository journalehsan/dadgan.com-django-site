from django.urls import path, register_converter
from django.contrib.auth.views import LogoutView
from . import views


class UnicodeSlugConverter:
    """Custom slug converter that supports Unicode characters (Persian/Arabic)"""
    regex = r'[\w\u0600-\u06FF-]+'
    
    def to_python(self, value):
        return value
    
    def to_url(self, value):
        return value


# Register custom converter
register_converter(UnicodeSlugConverter, 'unicode_slug')

app_name = 'lawfirm'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='lawfirm:home'), name='logout'),
    path('accounts/signup/', views.signup, name='signup'),
    path('search/', views.search, name='search'),
    path('api/search/', views.search_api, name='search_api'),
    path('api/notifications/count/', views.get_unread_notifications_count, name='notifications_count'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<unicode_slug:slug>/', views.blog_detail, name='blog_detail'),
    path('qa/', views.qa_list, name='qa_list'),
    path('qa/<unicode_slug:slug>/', views.qa_detail, name='qa_detail'),
    path('ajax/vote-question/<int:question_id>/', views.vote_question, name='vote_question'),
    path('ajax/vote-answer/<int:answer_id>/', views.vote_answer, name='vote_answer'),
]
