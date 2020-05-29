from django.test import TestCase
from django.contrib.auth.models import User

from .models import Shop

# Create your test here.
class MainTestCase(TestCase):

    def setUp(self):
        # Create user and shops.
        user = User.objects.create_user("user1", "user@email.com", "abc123")
        s1 = Shop.objects.create(name="ShopA",user=user,
        shop_type="TypeA",capacity="10",phone_number="09797979797",address="ABC/123")
        
