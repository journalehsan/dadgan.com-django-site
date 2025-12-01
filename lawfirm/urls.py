from django.urls import path
from . import views

app_name = 'lawfirm'

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('qa/', views.qa_list, name='qa_list'),
    path('qa/<slug:slug>/', views.qa_detail, name='qa_detail'),
    path('ajax/vote-question/<int:question_id>/', views.vote_question, name='vote_question'),
    path('ajax/vote-answer/<int:answer_id>/', views.vote_answer, name='vote_answer'),
]