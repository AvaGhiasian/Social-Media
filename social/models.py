from django.db import models
from django.contrib.auth.models import AbstractUser, User
from taggit.managers import TaggableManager
from django.urls import reverse
from django.contrib.auth import get_user_model

# Create your models here.

class User(AbstractUser):  # username, password, email, firstname, lastname already satisfied
    date_of_birth = models.DateField(verbose_name="تاریخ تولد", blank=True, null=True)
    bio = models.TextField(verbose_name="بایو", null=True, blank=True)
    photo = models.ImageField(verbose_name="تصویر", upload_to="", null=True, blank=True)
    job = models.CharField(verbose_name="شغل", max_length=25, null=True, blank=True)
    phone = models.CharField(max_length=11, null=True, blank=True)
    following = models.ManyToManyField('self', through='Contact', related_name="followers", symmetrical=False)


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_posts", verbose_name="نویسنده")
    description = models.TextField(verbose_name="توضیحات")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True, verbose_name="لایک ها")
    saved_by = models.ManyToManyField(User, related_name='saved_posts', blank=True)
    tags = TaggableManager()

    class Meta:
        ordering = ['-created']  # when getting all objects from DB it orders this way
        indexes = [  # writes this way to the DB
            models.Index(fields=['-created'])
        ]
        verbose_name = "پست"
        verbose_name_plural = "پست ها"

    def __str__(self):
        return self.author.first_name

    def get_absolute_url(self):
        return reverse('social:post_detail', args=[self.id])


class Contact(models.Model):
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rel_from_set")
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rel_to_set")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created'])
        ]
        ordering = ['-created']

    def __str__(self):
        return f"{self.user_from} follows {self.user_to}"
