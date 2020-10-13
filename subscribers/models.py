from django.db import models

class Location(models.Model):
    city = models.CharField(null=False, max_length=256)
    state = models.CharField(null=False, max_length=64)

class Subscriber(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(null=False, max_length=64)
    last_name = models.CharField(null=False, max_length=64)
    email = models.TextField()
    gender = models.CharField(null=False, max_length=8)
    location = models.ForeignKey(Location, related_name='subscriber_location', on_delete=models.DO_NOTHING)
