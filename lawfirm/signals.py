from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import ConsultationRequest, Notification


@receiver(post_save, sender=ConsultationRequest)
def create_notification_on_consultation_update(sender, instance, created, **kwargs):
    """
    Signal to create notification when consultation is updated
    """
    if not instance.user:
        return
    
    # Only create notification if status changed or scheduled_date was set
    if created:
        # New consultation created
        Notification.objects.create(
            user=instance.user,
            notification_type='general',
            title='درخواست مشاوره ثبت شد',
            message='درخواست مشاوره شما با موفقیت ثبت شد. منتظر تأیید مدیریت باشید.',
            consultation=instance,
        )
    else:
        # Check if consultation was updated
        try:
            previous = ConsultationRequest.objects.get(pk=instance.pk)
            
            # Notification for status change
            if previous.status != instance.status:
                if instance.status == 'confirmed':
                    Notification.objects.create(
                        user=instance.user,
                        notification_type='consultation_scheduled',
                        title='درخواست مشاوره تأیید شد',
                        message='درخواست مشاوره شما توسط مدیریت تأیید شد. لطفاً برای مشاهده جزئیات وارد پروفایل خود شوید.',
                        consultation=instance,
                    )
                elif instance.status == 'completed':
                    Notification.objects.create(
                        user=instance.user,
                        notification_type='consultation_completed',
                        title='مشاوره انجام شد',
                        message='مشاوره شما با موفقیت انجام شد. از استفاده از خدمات ما متشکریم.',
                        consultation=instance,
                    )
                elif instance.status == 'cancelled':
                    Notification.objects.create(
                        user=instance.user,
                        notification_type='consultation_update',
                        title='درخواست مشاوره لغو شد',
                        message='درخواست مشاوره شما لغو شده است. برای اطلاعات بیشتر با ما تماس بگیرید.',
                        consultation=instance,
                    )
            
            # Notification for scheduled date
            if previous.scheduled_date != instance.scheduled_date and instance.scheduled_date:
                # Format date in Persian format
                scheduled_date_str = instance.scheduled_date.strftime('%Y/%m/%d')
                scheduled_time_str = instance.scheduled_date.strftime('%H:%M')
                
                message = f'زمان مشاوره شما تعیین شد: {scheduled_date_str} ساعت {scheduled_time_str}'
                
                Notification.objects.create(
                    user=instance.user,
                    notification_type='consultation_scheduled',
                    title='زمان مشاوره تعیین شد',
                    message=message,
                    consultation=instance,
                )
            
            # Notification for admin message
            if previous.admin_message != instance.admin_message and instance.admin_message:
                Notification.objects.create(
                    user=instance.user,
                    notification_type='consultation_update',
                    title='پیام جدید از مدیریت',
                    message=instance.admin_message,
                    consultation=instance,
                )
        except ConsultationRequest.DoesNotExist:
            pass
