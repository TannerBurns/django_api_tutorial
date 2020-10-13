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