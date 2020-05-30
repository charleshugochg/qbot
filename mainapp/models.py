from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils import timezone

from secrets import token_urlsafe

# Created by DEV-B.

def get_upload_path(instance, filename):
    return f'mainapp/logos/{uuid.uuid4()}/{filename}'

class Shop(models.Model):
    ''' Shop class : to store user's shop information.
        WARNING : Do not create instance of the class,
        without User model specified.
    '''
    BLANK = ''
    INT_BLANK = 0

    # Required
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops', blank=True, null=True)

    name = models.CharField(max_length=128, blank=True)
    shop_type = models.CharField(max_length=64, blank=True)
    capacity = models.PositiveIntegerField(default=INT_BLANK)
    phone_number = models.CharField(max_length=12, blank=True)
    address = models.CharField(max_length=256, blank=True)
    # location_field, to add later

    logo = models.ImageField(upload_to=get_upload_path ,default='mainapp/logos/default.png')

    def __str__(self):
        return f"{self.name}, Type: {self.shop_type}, Capacity: {self.capacity}"


#############################################################################
# Don't come down Rio

class Queue(models.Model):
    class Status(models.TextChoices):
        QUEUE = 'QUEUE'
        BOOK = 'BOOK'
        ONCALL = 'ONCALL'
        SERVING = 'SERVING'
        SUCCESS = 'SUCCESS'
        CANCEL = 'CANCEL'

    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, blank=True, null=True)
    queue_date = models.DateTimeField('datetime queue', default=timezone.now)
    phone_number = models.CharField(max_length=12, blank=True)
    arrival_time = models.DateTimeField('datetime arrival', blank=True, null=True, default=None)
    token_id = models.CharField(max_length=12, default=token_urlsafe(8), editable=False)
    status = models.CharField(max_length=10, choices=Status.choices)

    def __str__(self):
        return f"Queue {self.id} with token {self.token_id}, status {self.status}"
    