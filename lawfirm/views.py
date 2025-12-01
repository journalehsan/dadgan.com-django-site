from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.text import slugify
import json

from .models import (
    BlogPost, Question, Answer, ConsultationRequest, ContactMessage,
    Testimonial, SiteSettings, Category, QACategory, ConsultationType
)
from .forms import ContactForm, ConsultationForm, QuestionForm, AnswerForm, SearchForm


def home(request):
    """صفحه اصلی"""
    # Get latest blog posts
    recent_blogs = BlogPost.objects.filter(published=True)[:3]
    
    # Get featured Q&As
    featured_questions = Question.objects.filter(is_published=True)[:4]
    
    # Get testimonials
    testimonials = Testimonial.objects.filter(is_published=True)[:3]
    
    # Get site settings for stats
    try:
        site_settings = SiteSettings.objects.first()
    except:
        site_settings = None
    
    # Get consultation types for pricing
    consultation_types = ConsultationType.objects.filter(is_active=True)[:2]
    
    # Handle contact form
    contact_form = ContactForm()
    if request.method == 'POST' and 'contact_submit' in request.POST:
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            contact_form.save()
            messages.success(request, 'درخواست شما با موفقیت ارسال شد. در اسرع وقت با شما تماس خواهیم گرفت.')
            return redirect('home')
    
    # Handle consultation form
    consultation_form = ConsultationForm()
    if request.method == 'POST' and 'consultation_submit' in request.POST:
        consultation_form = ConsultationForm(request.POST)
        if consultation_form.is_valid():
            consultation_form.save()
            messages.success(request, 'درخواست مشاوره شما ثبت شد. به زودی با شما تماس خواهیم گرفت.')
            return redirect('home')
    
    context = {
        'recent_blogs': recent_blogs,
        'featured_questions': featured_questions,
        'testimonials': testimonials,
        'site_settings': site_settings,
        'consultation_types': consultation_types,
        'contact_form': contact_form,
        'consultation_form': consultation_form,
    }
    return render(request, 'lawfirm/home.html', context)


def blog_list(request):
    """لیست مقالات بلاگ"""
    category_slug = request.GET.get('category')
    search_query = request.GET.get('search', '')
    
    blogs = BlogPost.objects.filter(published=True)
    
    # Filter by category
    if category_slug:
        blogs = blogs.filter(category__slug=category_slug)
    
    # Search functionality
    if search_query:
        blogs = blogs.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(blogs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
    }
    return render(request, 'lawfirm/blog_list.html', context)


def blog_detail(request, slug):
    """جزئیات مقاله"""
    blog = get_object_or_404(BlogPost, slug=slug, published=True)
    blog.increment_views()
    
    # Get related posts
    related_posts = BlogPost.objects.filter(
        category=blog.category, 
        published=True
    ).exclude(id=blog.id)[:3]
    
    context = {
        'blog': blog,
        'related_posts': related_posts,
        # SEO Meta Tags
        'seo_title': blog.get_seo_title(),
        'seo_description': blog.get_seo_description(),
        'seo_keywords': blog.get_seo_keywords(),
    }
    return render(request, 'lawfirm/blog_detail.html', context)


def qa_list(request):
    """لیست پرسش و پاسخ"""
    category_slug = request.GET.get('category')
    
    questions = Question.objects.filter(is_published=True)
    
    # Filter by category
    if category_slug:
        questions = questions.filter(category__slug=category_slug)
    
    # Search functionality
    search_form = SearchForm(request.GET)
    if search_form.is_valid() and search_form.cleaned_data.get('query'):
        query = search_form.cleaned_data['query']
        questions = questions.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(questions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = QACategory.objects.all()
    
    # Handle question submission
    question_form = QuestionForm()
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.slug = slugify(question.title, allow_unicode=True)
            question.save()
            messages.success(request, 'سوال شما ثبت شد و پس از بررسی منتشر خواهد شد.')
            return redirect('qa_list')
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'search_form': search_form,
        'question_form': question_form,
    }
    return render(request, 'lawfirm/qa_list.html', context)


def qa_detail(request, slug):
    """جزئیات پرسش و پاسخ"""
    question = get_object_or_404(Question, slug=slug, is_published=True)
    question.increment_views()
    
    # Get answers
    answers = question.answers.filter(is_published=True)
    
    # Get related questions
    related_questions = Question.objects.filter(
        category=question.category,
        is_published=True
    ).exclude(id=question.id)[:5]
    
    # Handle answer submission
    answer_form = AnswerForm()
    if request.method == 'POST':
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.question = question
            answer.save()
            messages.success(request, 'پاسخ شما ثبت شد و پس از بررسی منتشر خواهد شد.')
            return redirect('qa_detail', slug=slug)
    
    context = {
        'question': question,
        'answers': answers,
        'related_questions': related_questions,
        'answer_form': answer_form,
        # SEO Meta Tags
        'seo_title': question.get_seo_title(),
        'seo_description': question.get_seo_description(),
        'seo_keywords': question.get_seo_keywords(),
    }
    return render(request, 'lawfirm/qa_detail.html', context)


@require_http_methods(["POST"])
def vote_question(request, question_id):
    """امتیاز دادن به سوال"""
    if not request.headers.get('Content-Type') == 'application/json':
        return JsonResponse({'error': 'Invalid content type'}, status=400)
    
    try:
        data = json.loads(request.body)
        vote_type = data.get('vote_type')  # 'up' or 'down'
        
        question = get_object_or_404(Question, id=question_id, is_published=True)
        
        if vote_type == 'up':
            question.votes += 1
        elif vote_type == 'down':
            question.votes -= 1
        else:
            return JsonResponse({'error': 'Invalid vote type'}, status=400)
        
        question.save()
        
        return JsonResponse({
            'success': True,
            'new_votes': question.votes
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
def vote_answer(request, answer_id):
    """امتیاز دادن به پاسخ"""
    if not request.headers.get('Content-Type') == 'application/json':
        return JsonResponse({'error': 'Invalid content type'}, status=400)
    
    try:
        data = json.loads(request.body)
        vote_type = data.get('vote_type')  # 'up' or 'down'
        
        answer = get_object_or_404(Answer, id=answer_id, is_published=True)
        
        if vote_type == 'up':
            answer.votes += 1
        elif vote_type == 'down':
            answer.votes -= 1
        else:
            return JsonResponse({'error': 'Invalid vote type'}, status=400)
        
        answer.save()
        
        return JsonResponse({
            'success': True,
            'new_votes': answer.votes
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def search(request):
    """جستجو در مقالات و سوالات"""
    query = request.GET.get('q', '').strip()
    
    context = {
        'query': query,
        'blogs': [],
        'questions': [],
        'total_results': 0,
    }
    
    if query and len(query) >= 2:
        # Search in blog posts
        blogs = BlogPost.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(excerpt__icontains=query),
            published=True
        )[:10]
        
        # Search in questions
        questions = Question.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query),
            is_published=True
        )[:10]
        
        context['blogs'] = blogs
        context['questions'] = questions
        context['total_results'] = blogs.count() + questions.count()
    
    return render(request, 'lawfirm/search.html', context)
