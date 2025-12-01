"""
Django template tags for SEO optimization
"""

import json
from django import template
from django.utils.html import mark_safe
from lawfirm.seo import render_question_schema, render_article_schema

register = template.Library()


@register.filter
def seo_title(value):
    """Return SEO optimized title"""
    if hasattr(value, 'get_seo_title'):
        return value.get_seo_title()
    return str(value)


@register.filter
def seo_description(value):
    """Return SEO optimized description"""
    if hasattr(value, 'get_seo_description'):
        return value.get_seo_description()
    return str(value)


@register.filter
def seo_keywords(value):
    """Return SEO optimized keywords"""
    if hasattr(value, 'get_seo_keywords'):
        return value.get_seo_keywords()
    return ""


@register.simple_tag
def question_schema(question):
    """Render Schema.org Question schema"""
    schema = render_question_schema(question)
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>')


@register.simple_tag
def article_schema(article):
    """Render Schema.org Article schema"""
    schema = render_article_schema(article)
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>')


@register.simple_tag
def organization_schema():
    """Render Schema.org Organization schema"""
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "موسسه حقوقی دادگان",
        "url": "https://dadgan.com",
        "logo": "https://dadgan.com/static/images/logo.png",
        "description": "موسسه حقوقی دادگان - مشاوره حقوقی و خدمات حقوقی",
        "sameAs": [
            "https://www.facebook.com/dadgan",
            "https://www.instagram.com/dadgan",
            "https://www.linkedin.com/company/dadgan"
        ],
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "Customer Service",
            "telephone": "+98-xxx-xxx-xxxx",
            "availableLanguage": ["fa", "en"]
        }
    }
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>')


@register.simple_tag
def breadcrumb_schema(breadcrumbs):
    """Render Schema.org Breadcrumb schema"""
    items = []
    for i, (name, url) in enumerate(breadcrumbs, 1):
        items.append({
            "@type": "ListItem",
            "position": i,
            "name": name,
            "item": f"https://dadgan.com{url}" if url else "https://dadgan.com"
        })
    
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>')
