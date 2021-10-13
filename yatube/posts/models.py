from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.TextField()
    slug = 
    description = models.TextField()
    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = Group(blank=True, null=True)


# class Event(models.Model):
#     name = models.CharField(max_length=200)
#     start_at = models.DateTimeField(auto_now_add=True)
#     description = models.TextField() 
#     contact = models.EmailField()
#     author = models.ForeignKey(
#         User, 
#         on_delete=models.CASCADE, 
#         related_name="events"
#     )
#     location = models.CharField(max_length=400)