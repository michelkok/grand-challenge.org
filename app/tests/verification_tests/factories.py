import factory

from grandchallenge.verifications.models import Verification
from tests.factories import UserFactory


class VerificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Verification

    user = factory.SubFactory(UserFactory)
    email = factory.LazyAttribute(lambda u: "%s@example.com" % u.user.pk)
