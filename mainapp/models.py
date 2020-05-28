from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Created by DEV-B.

class Shop(models.Model):
    BLANK = ''
    INT_BLANK = 0

    name = models.CharField(max_length=128, blank=True)
    logo = models.ImageField(upload_to='mainapp/media/logos',default='mainapp/media/logos/default.png')
    shop_type = models.CharField(max_length=64, blank=True)
    capacity = models.PositiveIntegerField(default=INT_BLANK)
    phone_number = models.CharField(max_length=12, blank=True)
    address = models.CharField(max_length=256, blank=True)
    # location_field, to add later

    # auto
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops', blank=True, null=True)

    def __str__(self):
        return f"{self.name}"
