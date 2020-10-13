# Django API Tutorial

The goal of this tutorial is to create an api to create and list subscribers. 
In this tutorial we will inspect the data, create models, serializers, and views, time the difference between create and bulk create, and learn how to filter the queryset.
Well-known libraries we will use include [Django](https://docs.djangoproject.com/en/3.1/), and [Djangorestframework](https://www.django-rest-framework.org/).

- [Installing libraries](#install)
- [Creating django project and app](#creating_project)
- [Project structure](#project_structure)
- [Understanding the data](#understanding_data)
- [Creating models](#creating_models)
- [Creating serializers](#creating_serializers)
- [Creating views](#creating_views)
- [Creating routes (urls)](#creating_routes)
- [Adding command for test data](#adding_commands)
- [Creating a bulk serializer](#creating_bulk_serializer)
- [Queryset Filtering](#queryset_filtering)

<a name="install"></a>
## Installing Django and Djangorestframework

`pip3 install django djangorestframework`

<a name="creating_project"></a>
## Creating a Django Project and Django App

1. Create a working directory for the django project
    ```bash
    mkdir django_api_tutorial && cd django_api_tutorial
    ```
2. Create the django project
    ```bash
   django-admin startproject api .
    ```
3. Create the django app for subscribers
    ```bash
   python3 manage.py startapp subscribers
    ```
4. Connect subscribers and rest_framework app to the api settings in `api/settings.py`
    ```python3
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',         # new (djangorestframework)
        'subscribers'             # new
    ]    
    ```
   Add the following to the bottom of the settings for paged list results
   ```python3
   REST_FRAMEWORK = {
       'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
       'PAGE_SIZE': 32
   }
   ```

<a name="project_structure"></a>
## Project structure

```
./django_api_tutorial
│   manage.py
│   README.md
│
├───api
│       asgi.py
│       settings.py
│       urls.py
│       wsgi.py
│       __init__.py
│
├───data
│       fake_users.csv
│
└───subscribers
    │   admin.py
    │   apps.py
    │   models.py
    │   serializers.py
    │   tests.py
    │   urls.py
    │   views.py
    │   __init__.py
    │
    ├───management
    │   └───commands
    │           bulktestdata.py
    │           testdata.py
    │
    └───migrations
            __init__.py

```

Learn more about django project structure [here](https://djangobook.com/mdj2-django-structure/).

<a name="understanding_data"></a>
## Understanding the data

Here are the first 10 rows of our data for the tutorial. This data was created using Mockaroo.

| first\_name | last\_name | email                          | gender | city           | state          |
|-------------|------------|--------------------------------|--------|----------------|----------------|
| Mohammed    | Poad       | mpoad0@cisco\.com              | Male   | Watertown      | Massachusetts  |
| Briana      | Liddall    | bliddall1@odnoklassniki\.ru    | Female | Indianapolis   | Indiana        |
| Jodie       | Pattington | jpattington2@telegraph\.co\.uk | Male   | Brockton       | Massachusetts  |
| Cari        | Worcs      | cworcs3@youku\.com             | Female | Richmond       | Virginia       |
| Shane       | Pickford   | spickford4@arstechnica\.com    | Male   | Newark         | New Jersey     |
| Bethany     | McColm     | bmccolm5@comsenz\.com          | Female | Evansville     | Indiana        |
| Elsi        | Wyrill     | ewyrill6@opera\.com            | Female | Lexington      | Kentucky       |
| Kylynn      | Hartill    | khartill7@webeden\.co\.uk      | Female | Columbia       | South Carolina |
| Lonnie      | Elliot     | lelliot8@msn\.com              | Male   | Joliet         | Illinois       |
| Kellyann    | Kelso      | kkelso9@sbwire\.com            | Female | San Bernardino | California     |

Now we will break down each one of these columns corresponding data type.

    first_name      Charvar(64)
    last_name       Charvar(64)
    email           Text
    gender          Charvar(8)
    city            Charvar(256)
    state           Charvar(24)

Knowing how we want to handle each of these variables is going to enable us to easily create our models and serializers.

<a name="creating_models"></a>
## Creating models

The model definitions can be found in `subscribers/models.py`.

```python3
from django.db import models

class Location(models.Model):
    city = models.CharField(null=False, max_length=256)
    state = models.CharField(null=False, max_length=64)

class Subscriber(models.Model):
    first_name = models.CharField(null=False, max_length=64)
    last_name = models.CharField(null=False, max_length=64)
    email = models.TextField()
    gender = models.CharField(null=False, max_length=8)
    location = models.ForeignKey(Location, related_name='subscriber_location', on_delete=models.DO_NOTHING)
```

Above, we defined our models for a Subscriber and Location. 
The Location model is a Many to One relationship with the Subscriber model since we can have many subscribers in one location.

<a name="creating_serializers"></a>
## Creating serializers

We will now define our serializers for the models. This allows us to easily convert the model objects into json objects for api responses.
When we create serializers, we can add a lot of functionality to our api easily with djangorestframework. 
The serializers are defined in `subscribers/serializers.py`. Notice that in the SubscriberSerializer we have to overwrite the create method. 
This is normal when you are using relational models.
```python3
from rest_framework import serializers

class LocationSerializer(serializers.Serializer):
    city = serializers.CharField(required=True, max_length=256)
    state = serializers.CharField(required=True, max_length=64)

    class Meta:
        fields = ['city', 'state']

class SubscriberSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    created = serializers.DateTimeField(required=False)
    first_name = serializers.CharField(required=True, max_length=64)
    last_name = serializers.CharField(required=True, max_length=64)
    email = serializers.CharField(required=False)
    gender = serializers.CharField(required=True, max_length=8)
    location = LocationSerializer(required=True)

    class Meta:
        fields = ['first_name', 'last_name', 'email', 'gender', 'location']
        read_only_fields = ['id', 'created']

        def create(self, validated_data):
        # remove location from serialized data and add model object
        location = validated_data.pop('location')
        city = location.get('city', None)
        state = location.get('state', None)

        if not city and not state:
            raise serializers.ValidationError('No location input found')

        # call get or create to reuse location objects
        location_obj = Location.objects.get_or_create(city=city, state=state)[0]
        # add location back to validated data
        validated_data.update({'location': location_obj})

        # unpack validated_data to create a new Subscriber object
        return Subscriber.objects.create(**validated_data)

```

We have now defined our serializers so that we can easily do things like create, read, update, delete and list objects from our models. 
We will see this in action when we implement our Views.

<a name="creating_views"></a>
## Creating views

The views are defined in `subscribers/views.py` and contain the functionality that will be available to users of the api.
In this tutorial we will focus on being able to create and list subscribers. 
However, I will give an example how to easily add a delete operation to the api using djangorestframework mixins.

```python3
from rest_framework import viewsets, mixins

from .models import Subscriber
from .serializers import SubscriberSerializer

class SubscriberView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer
```

This simple view above provides a generic api interface with list and create functionality for Subscribers.
To easily add the delete method and functionality it would look like the following:

```python3
from rest_framework import viewsets, mixins

from .models import Subscriber
from .serializers import SubscriberSerializer

class SubscriberView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                     mixins.DestroyModelMixin):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer
```

Notice the only new change was the addition of `mixins.DestroyModelMixin` in the class definition.

<a name="creating_routes"></a>
## Creating routes

Now to be able to navigate to our api we will need to add the urls. The urls are defined in `subscribers/urls.py`.
We will also want to tell our base api where to find the routes from subscribers and this is defined in `api/urls.py`.

```python3
# api/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tutorial/', include('subscribers.urls'))
]
```

```python3
# subscribers/urls.py
from rest_framework import routers

from .views import SubscriberView

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'subscribers', SubscriberView, basename='subscribers')
urlpatterns = router.urls
```

In the subscribers urls we use a router from djangorestframework to easily add all of the functionality that we defined in the views.
The router with the viewset enabled the following routes for the api.

```
GET     /tutorial/subscribers       List view of subscribers
POST    /tutorial/subscribers       Create a new subscriber
```

<a name="adding_commands"></a>
## Adding a command for test data

Now we will add a command to django to easily allow us to add test data to our api. The commands are defined in `subscribers/management/commands` and our first command is named `testdata.py`.

```python3
import csv

from time import time
from django.core.management.base import BaseCommand, CommandError

from subscribers.serializers import SubscriberSerializer

class Command(BaseCommand):
    help = 'Adds the fake test data to the api'

    def handle(self, *args, **options):
        try:
            with open('data/fake_users.csv', 'r') as fin:
                csvreader = csv.reader(fin)
                headers = next(csvreader)
                data = [{'first_name': row[0],
                         'last_name': row[1],
                         'email': row[2],
                         'gender': row[3],
                         'location': {'city': row[4], 'state': row[5]}
                         } for row in csvreader
                        ]
                # time how fast it takes to add all records 1 by 1
                start = time()
                for item in data:
                    serializer = SubscriberSerializer(data=item)
                    if serializer.is_valid():
                        serializer.create(item)
                stop = time()
                print(f'{len(data)} items added in {stop-start} seconds')
        except FileExistsError:
            raise CommandError('No testdata found')
```

This command will add our test records to the api. It will also track how many records and how quickly they were added.
We will run the command and see what the output is.

```bash
python3 manage.py testdata
```
Output: `6000 items added in 31.6553955078125`

Next we will implement a bulk serializer and add a new bulk command to see if we can speed up creating records.

<a name="creating_bulk_serializer"></a>
## Creating a bulk serializer

Instead of having to create objects one by one we will create a bulk serializer to create many at a time.

```python3
class BulkSubscriberSerializer(serializers.Serializer):
    subscribers = SubscriberSerializer(many=True)

    class Meta:
        fields = ['subscribers']

    def create(self, validated_data):
        # store the Subscriber objects to be created in bulk
        create_objects_list = []
        # iterate over the validated_data and add Subscriber objects to a list to be created
        for data in validated_data:
            # notice the same functionality from the regular serializer
            location = data.pop('location')
            city = location.get('city', None)
            state = location.get('state', None)
            location_obj = Location.objects.get_or_create(city=city, state=state)[0]
            # combine data and {'location': location_obj} and unpack to the Subscriber model
            create_objects_list.append(Subscriber(**{**data, **{'location': location_obj}}))
        return Subscriber.objects.bulk_create(create_objects_list)
```

We will also create a new command called bulktestdata that is defined in `subscribers/management/commands/bulktestdata.py`.
This will use our bulk serializer and time how long it took to add the records.

```python3
import csv

from time import time
from django.core.management.base import BaseCommand, CommandError

from subscribers.serializers import BulkSubscriberSerializer

class Command(BaseCommand):
    help = 'Adds the fake test data to the api'

    def handle(self, *args, **options):
        try:
            with open('data/fake_users.csv', 'r') as fin:
                csvreader = csv.reader(fin)
                headers = next(csvreader)
                data = [{'first_name': row[0],
                         'last_name': row[1],
                         'email': row[2],
                         'gender': row[3],
                         'location': {'city': row[4], 'state': row[5]}
                         } for row in csvreader
                        ]
                # time how fast it takes to add records in bulk
                start = time()
                bulk_serializer = BulkSubscriberSerializer(data={'subscribers': data})
                if bulk_serializer.is_valid():
                    bulk_serializer.create(data)
                stop = time()
                print(f'{len(data)} items added in {stop-start} seconds')
        except FileExistsError:
            raise CommandError('No testdata found')
```

Now when we run our new command lets see how fast the records get added.

```bash
python3 manage.py bulktestdata
```
Output: `6000 items added in 5.3229029178619385 seconds`

Lastly, we will update the views to use the regular or bulk serializer based on the data sent to the route.

```python3
from rest_framework import viewsets, mixins
from rest_framework.response import Response

from .models import Subscriber
from .serializers import SubscriberSerializer, BulkSubscriberSerializer

class SubscriberView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                     mixins.DestroyModelMixin):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer

    def create(self, request, *args, **kwargs):
        # if the data is a dictionary, use parent create that relies on serializer_class
        if isinstance(request.data, dict):
            return super(SubscriberView, self).create(request, *args, **kwargs)
        # if the data is a list, send to the bulk serializer to handle creation
        elif isinstance(request.data, list):
            serializer = BulkSubscriberSerializer(data={'subscribers': request.data})
            if serializer.is_valid():
                serializer.create(request.data)
                return Response(serializer.data, status=201)
            else:
                return Response(serializer.errors, status=400)
        else:
            return Response('Invalid data received', status=400)
```

At this point, our api can now create one to many records at a time and allow users to browse the current subscribers.
Here is a snippet of a response from our api for a GET request to `http://127.0.0.1:8000/tutorial/subscribers`.

```
{
    "count": 6000,
    "next": "http://127.0.0.1:8000/tutorial/subscribers?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "created": "2020-10-13T15:51:50.850563Z",
            "first_name": "Mohammed",
            "last_name": "Poad",
            "email": "mpoad0@cisco.com",
            "gender": "Male",
            "location": {
                "city": "Watertown",
                "state": "Massachusetts"
            }
        },
        {
            "id": 2,
            "created": "2020-10-13T15:51:50.862560Z",
            "first_name": "Briana",
            "last_name": "Liddall",
            "email": "bliddall1@odnoklassniki.ru",
            "gender": "Female",
            "location": {
                "city": "Indianapolis",
                "state": "Indiana"
            }
        },
        {
            "id": 3,
            "created": "2020-10-13T15:51:50.874563Z",
            "first_name": "Jodie",
            "last_name": "Pattington",
            "email": "jpattington2@telegraph.co.uk",
            "gender": "Male",
            "location": {
                "city": "Brockton",
                "state": "Massachusetts"
            }
        },
        ...
    ]
}
```

