from django.urls import path, re_path
from . import views

app_name = 'lawfirm'

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/', views.blog_list, name='blog_list'),
    re_path(r'^blog/(?P<slug>[\w\u0600-\u06FF\u200C\u200D-]+)/$', views.blog_detail, name='blog_detail'),
    path('qa/', views.qa_list, name='qa_list'),
    re_path(r'^qa/(?P<slug>[\w\u0600-\u06FF\u200C\u200D-]+)/$', views.qa_detail, name='qa_detail'),
    path('ajax/vote-question/<int:question_id>/', views.vote_question, name='vote_question'),
    path('ajax/vote-answer/<int:answer_id>/', views.vote_answer, name='vote_answer'),
]