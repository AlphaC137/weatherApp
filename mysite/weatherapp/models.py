from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class FavoriteCity(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Favorite Cities"
        ordering = ['-date_added']
    
    def __str__(self):
        return f"{self.name} (added by {self.user.username})"
