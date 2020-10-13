from rest_framework import routers

from .views import SubscriberView

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'subscribers', SubscriberView, basename='subscribers')
urlpatterns = router.urls

