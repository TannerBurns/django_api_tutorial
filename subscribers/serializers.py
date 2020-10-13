from rest_framework import serializers

from .models import Location, Subscriber

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
    email = serializers.CharField()
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