from django.core.mail import send_mail
from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver

from .models import Post


@receiver(m2m_changed, sender=Post.likes.through)  # m2m_changed is receiver type
def users_like_changed(sender, instance, **kwargs):
    instance.total_likes = instance.likes.count()
    instance.save()


@receiver(post_delete, sender=Post)
def users_like_changed(sender, instance, **kwargs):
    author = instance.author
    subject = f"Your post was deleted"
    message = f"Your post was deleted (Id:{instance.id})"
    from_email = 'avaghiasian82@gmail.com'
    send_mail(subject, message, from_email, [author.email], fail_silently=False)
