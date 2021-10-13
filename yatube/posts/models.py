from django.db import models

<<<<<<< HEAD
User = get_user_model()


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    ) 
=======
# Create your models here.
>>>>>>> parent of 5487f2c (Added admin and post (test))
