"""
SEO utilities for Django templates
"""

from django.template.loader import render_to_string


class SEOMixin:
    """Mixin to add SEO metadata to template context"""
    
    seo_title = None
    seo_description = None
    seo_keywords = None
    seo_image = None
    seo_url = None
    
    def get_seo_context(self):
        """Return SEO context for template"""
        return {
            'seo_title': self.seo_title or 'موسسه حقوقی دادگان',
            'seo_description': self.seo_description or 'مشاوره حقوقی و خدمات حقوقی',
            'seo_keywords': self.seo_keywords or 'موسسه حقوقی، مشاوره حقوقی، وکیل',
            'seo_image': self.seo_image or '/static/images/logo.png',
            'seo_url': self.seo_url or 'https://dadgan.com',
        }


def render_seo_meta_tags(obj):
    """Render SEO meta tags from an object with SEO methods"""
    if hasattr(obj, 'get_seo_title'):
        return {
            'title': obj.get_seo_title(),
            'description': obj.get_seo_description(),
            'keywords': obj.get_seo_keywords(),
        }
    return {}


# Template tag for structured data (Schema.org)
def render_question_schema(question):
    """Render Schema.org Question schema"""
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": {
            "@type": "Question",
            "name": question.title,
            "text": question.content,
            "datePublished": question.created_at.isoformat(),
            "author": {
                "@type": "Person",
                "name": question.asker_name
            },
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "",
                "author": {
                    "@type": "Organization",
                    "name": "موسسه حقوقی دادگان"
                }
            } if question.get_best_answer() else None
        }
    }
    
    # Add best answer if exists
    best_answer = question.get_best_answer()
    if best_answer:
        schema["mainEntity"]["acceptedAnswer"]["text"] = best_answer.content
    else:
        del schema["mainEntity"]["acceptedAnswer"]
    
    return schema


def render_article_schema(article):
    """Render Schema.org Article schema"""
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article.title,
        "description": article.excerpt,
        "image": str(article.image.url) if article.image else None,
        "datePublished": article.created_at.isoformat(),
        "dateModified": article.updated_at.isoformat(),
        "author": {
            "@type": "Person",
            "name": article.author.get_full_name() or article.author.username
        },
        "publisher": {
            "@type": "Organization",
            "name": "موسسه حقوقی دادگان",
            "logo": {
                "@type": "ImageObject",
                "url": "/static/images/logo.png"
            }
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://dadgan.com{article.get_absolute_url()}"
        }
    }
    return schema
