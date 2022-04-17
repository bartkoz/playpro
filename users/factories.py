import datetime

import factory
from factory.fuzzy import FuzzyDate
from faker import Faker

from users.models import User, School, UserAvatar


class SchoolFactory(factory.django.DjangoModelFactory):
    name = Faker(['en_US', ]).sentence(nb_words=3)

    class Meta:
        model = School


class UserFactory(factory.django.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Sequence(lambda n: 'user{0}@test.com'.format(n))
    school_email = factory.Sequence(lambda n: 'user{0}@school.com'.format(n))
    school = School.objects.order_by('?').first()
    dob = factory.fuzzy.FuzzyDate(
        start_date=datetime.date(2005, 1, 1),
        end_date=datetime.date(2008, 1, 1),
    )
    user_type = 0
    avatar = UserAvatar.objects.first()
    graduation_year = 2022

    class Meta:
        model = User
