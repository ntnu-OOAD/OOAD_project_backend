from django.db import models

# Create your models here.
class User(models.Model):
    name = models.TextField(max_length=100)
    email = models.TextField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "bookkeeping"

    def __str__(self):
        return self.name