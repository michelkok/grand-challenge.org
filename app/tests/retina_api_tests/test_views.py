import json
import pytest

from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory
from django.core.cache import cache
from django.test import TestCase
from django.contrib.auth.models import Group
from django.conf import settings

from grandchallenge.subdomains.utils import reverse
from tests.conftest import generate_annotation_set
from tests.viewset_helpers import view_test
from tests.retina_api_tests.helpers import (
    create_datastructures_data,
    batch_test_image_endpoint_redirects,
    batch_test_data_endpoints,
    client_login,
)
from tests.cases_tests.factories import ImageFactory
from tests.factories import UserFactory
from tests.annotations_tests.factories import (
    PolygonAnnotationSetFactory,
    SinglePolygonAnnotationFactory,
)
from grandchallenge.annotations.serializers import (
    PolygonAnnotationSetSerializer,
    SinglePolygonAnnotationSerializer,
)
from grandchallenge.annotations.models import PolygonAnnotationSet
from grandchallenge.retina_api.views import (
    PolygonAnnotationSetViewSet,
    SinglePolygonViewSet,
    PolygonListView,
)


@pytest.mark.django_db
class TestArchiveIndexAPIEndpoints:
    def test_archive_view_non_auth(self, client):
        # Clear cache manually (this is not done by pytest-django for some reason...)
        cache.clear()
        url = reverse("retina:api:archives-api-view")
        response = client.get(url, HTTP_ACCEPT="application/json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_archive_view_normal_non_auth(self, client):
        # Create data
        create_datastructures_data()

        # login client
        client, _ = client_login(client, user="normal")

        url = reverse("retina:api:archives-api-view")
        response = client.get(url, HTTP_ACCEPT="application/json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_archive_view_retina_auth(self, client):
        # Create data
        create_datastructures_data()

        # login client
        client, _ = client_login(client, user="retina_user")

        url = reverse("retina:api:archives-api-view")
        response = client.get(url, HTTP_ACCEPT="application/json")
        assert response.status_code == status.HTTP_200_OK

    def test_archive_view_returns_correct_data(self, client):
        # Clear cache manually (this is not done by pytest-django for some reason...)
        cache.clear()
        # Create data
        datastructures, datastructures_aus, oct_obs_registration, oct_obs_registration_aus = (
            create_datastructures_data()
        )

        # login client
        client, _ = client_login(client, user="retina_user")

        url = reverse("retina:api:archives-api-view")
        response = client.get(url, HTTP_ACCEPT="application/json")
        response_data = json.loads(response.content)
        # check if correct data is sent
        expected_response_data = {
            "subfolders": {
                datastructures["archive"].name: {
                    "subfolders": {
                        datastructures["patient"].name: {
                            "subfolders": {
                                datastructures["study_oct"].name: {
                                    "info": "level 5",
                                    "images": {
                                        datastructures["image_oct"].name: {
                                            "images": {
                                                "trc_000": "no info",
                                                "obs_000": str(
                                                    datastructures[
                                                        "image_obs"
                                                    ].id
                                                ),
                                                "mot_comp": "no info",
                                                "trc_001": "no info",
                                                "oct": str(
                                                    datastructures[
                                                        "image_oct"
                                                    ].id
                                                ),
                                            },
                                            "info": {
                                                "voxel_size": {
                                                    "axial": 0,
                                                    "lateral": 0,
                                                    "transversal": 0,
                                                },
                                                "date": datastructures[
                                                    "study_oct"
                                                ].datetime.strftime(
                                                    "%Y/%m/%d %H:%M:%S"
                                                ),
                                                "registration": {
                                                    "obs": "Checked separately",
                                                    "trc": [0, 0, 0, 0],
                                                },
                                            },
                                        }
                                    },
                                    "name": datastructures["study_oct"].name,
                                    "id": str(datastructures["study_oct"].id),
                                    "subfolders": {},
                                },
                                datastructures["study"].name: {
                                    "info": "level 5",
                                    "images": {
                                        datastructures["image_cf"].name: str(
                                            datastructures["image_cf"].id
                                        )
                                    },
                                    "name": datastructures["study"].name,
                                    "id": str(datastructures["study"].id),
                                    "subfolders": {},
                                },
                            },
                            "info": "level 4",
                            "name": datastructures["patient"].name,
                            "id": str(datastructures["patient"].id),
                            "images": {},
                        }
                    },
                    "info": "level 3",
                    "name": datastructures["archive"].name,
                    "id": str(datastructures["archive"].id),
                    "images": {},
                },
                datastructures_aus["archive"].name: {
                    "subfolders": {
                        datastructures_aus["patient"].name: {
                            "subfolders": {},
                            "info": "level 4",
                            "name": datastructures_aus["patient"].name,
                            "id": str(datastructures_aus["patient"].id),
                            "images": {
                                datastructures_aus["image_oct"].name: {
                                    "images": {
                                        "trc_000": "no info",
                                        "obs_000": str(
                                            datastructures_aus["image_obs"].id
                                        ),
                                        "mot_comp": "no info",
                                        "trc_001": "no info",
                                        "oct": str(
                                            datastructures_aus["image_oct"].id
                                        ),
                                    },
                                    "info": {
                                        "voxel_size": {
                                            "axial": 0,
                                            "lateral": 0,
                                            "transversal": 0,
                                        },
                                        "date": datastructures_aus[
                                            "study_oct"
                                        ].datetime.strftime(
                                            "%Y/%m/%d %H:%M:%S"
                                        ),
                                        "registration": {
                                            "obs": "Checked separately",
                                            "trc": [0, 0, 0, 0],
                                        },
                                    },
                                },
                                datastructures_aus["image_cf"].name: str(
                                    datastructures_aus["image_cf"].id
                                ),
                            },
                        }
                    },
                    "info": "level 3",
                    "name": datastructures_aus["archive"].name,
                    "id": str(datastructures_aus["archive"].id),
                    "images": {},
                },
            },
            "info": "level 2",
            "name": "Archives",
            "id": "none",
            "images": {},
        }

        # Compare floats separately because of intricacies of floating-point arithmetic in python
        try:
            # Get info objects of both archives in response data
            response_archive_info = (
                response_data.get("subfolders")
                .get(datastructures["archive"].name)
                .get("subfolders")
                .get(datastructures["patient"].name)
                .get("subfolders")
                .get(datastructures["study_oct"].name)
                .get("images")
                .get(datastructures["image_oct"].name)
                .get("info")
            )
            response_archive_australia_info = (
                response_data.get("subfolders")
                .get(datastructures_aus["archive"].name)
                .get("subfolders")
                .get(datastructures_aus["patient"].name)
                .get("images")
                .get(datastructures_aus["image_oct"].name)
                .get("info")
            )

            floats_to_compare = []  # list of (response_float, expected_float, name) tuples
            for archive, response_info, ds, oor in (
                (
                    "Rotterdam",
                    response_archive_info,
                    datastructures,
                    oct_obs_registration,
                ),
                (
                    "Australia",
                    response_archive_australia_info,
                    datastructures_aus,
                    oct_obs_registration_aus,
                ),
            ):

                # oct obs registration
                response_obs = response_info.get("registration").get("obs")
                rv = oor.registration_values
                floats_to_compare.append(
                    (
                        response_obs[0],
                        rv[0][0],
                        archive + " obs oct registration top left x",
                    )
                )
                floats_to_compare.append(
                    (
                        response_obs[1],
                        rv[0][1],
                        archive + " obs oct registration top left y",
                    )
                )
                floats_to_compare.append(
                    (
                        response_obs[2],
                        rv[1][0],
                        archive + " obs oct registration bottom right x",
                    )
                )
                floats_to_compare.append(
                    (
                        response_obs[3],
                        rv[1][1],
                        archive + " obs oct registration bottom right y",
                    )
                )

            # Compare floats
            for result, expected, name in floats_to_compare:
                if result != pytest.approx(expected):
                    pytest.fail(name + " does not equal expected value")

            # Clear voxel and obs registration objects before response object to expected object comparison
            response_data["subfolders"][datastructures["archive"].name][
                "subfolders"
            ][datastructures["patient"].name]["subfolders"][
                datastructures["study_oct"].name
            ][
                "images"
            ][
                datastructures["image_oct"].name
            ][
                "info"
            ][
                "registration"
            ][
                "obs"
            ] = "Checked separately"

            response_data["subfolders"][datastructures_aus["archive"].name][
                "subfolders"
            ][datastructures_aus["patient"].name]["images"][
                datastructures_aus["image_oct"].name
            ][
                "info"
            ][
                "registration"
            ][
                "obs"
            ] = "Checked separately"

        except (AttributeError, KeyError, TypeError):
            pytest.fail("Response object structure is not correct")

        assert response_data == expected_response_data


@pytest.mark.django_db
class TestImageAPIEndpoint:
    # test methods are added dynamically
    pass


batch_test_image_endpoint_redirects(TestImageAPIEndpoint)


@pytest.mark.django_db
class TestDataAPIEndpoint:
    # test methods are added dynamically
    pass


batch_test_data_endpoints(TestDataAPIEndpoint)


class TestPolygonAPIListView(TestCase):
    def setUp(self):
        self.annotation_set = generate_annotation_set(retina_grader=True)
        self.kwargs = {
            "user_id": self.annotation_set.grader.id,
            "image_id": self.annotation_set.polygon.image.id,
        }
        self.url = reverse(
            "retina:api:annotation-api-view", kwargs=self.kwargs
        )
        self.view = PolygonListView.as_view()
        self.rf = APIRequestFactory()
        self.request = self.rf.get(self.url)
        self.serialized_data = PolygonAnnotationSetSerializer(
            instance=self.annotation_set.polygon
        )

    def test_polygon_list_api_view_non_authenticated(self):
        response = self.view(self.request, **self.kwargs)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_polygon_list_api_view_non_retina_user(self):
        self.annotation_set.grader.groups.clear()
        force_authenticate(self.request, user=self.annotation_set.grader)
        response = self.view(self.request, **self.kwargs)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_polygon_list_api_view_owner_authenticated(self):
        force_authenticate(self.request, user=self.annotation_set.grader)
        response = self.view(self.request, **self.kwargs)

        assert response.status_code == status.HTTP_200_OK
        assert response.data[0] == self.serialized_data.data

    def test_polygon_list_api_view_admin_authenticated(self):
        retina_admin = UserFactory()
        retina_admin.groups.add(
            Group.objects.get(name=settings.RETINA_ADMINS_GROUP_NAME)
        )
        force_authenticate(self.request, user=retina_admin)
        response = self.view(self.request, **self.kwargs)

        assert response.status_code == status.HTTP_200_OK
        assert response.data[0] == self.serialized_data.data


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type",
    [
        None,
        "normal_user",
        "retina_grader_non_allowed",
        "retina_grader",
        "retina_admin",
    ],
)
class TestPolygonAnnotationSetViewSet:
    namespace = "retina:api"
    basename = "polygonannotationset"

    def test_list_view(self, TwoRetinaPolygonAnnotationSets, rf, user_type):
        response = view_test(
            "list",
            user_type,
            self.namespace,
            self.basename,
            TwoRetinaPolygonAnnotationSets.grader1,
            TwoRetinaPolygonAnnotationSets.polygonset1,
            rf,
            PolygonAnnotationSetViewSet,
        )
        if user_type in ("retina_grader", "retina_admin"):
            serialized_data = PolygonAnnotationSetSerializer(
                TwoRetinaPolygonAnnotationSets.polygonset1
            ).data
            assert response.data[0] == serialized_data

    def test_create_view(self, TwoRetinaPolygonAnnotationSets, rf, user_type):
        model_build = PolygonAnnotationSetFactory.build()
        model_serialized = PolygonAnnotationSetSerializer(model_build).data
        image = ImageFactory()
        model_serialized["image"] = str(image.id)
        model_serialized["grader"] = TwoRetinaPolygonAnnotationSets.grader1.id
        model_json = json.dumps(model_serialized)

        response = view_test(
            "create",
            user_type,
            self.namespace,
            self.basename,
            TwoRetinaPolygonAnnotationSets.grader1,
            TwoRetinaPolygonAnnotationSets.polygonset1,
            rf,
            PolygonAnnotationSetViewSet,
            model_json,
        )
        if user_type in ("retina_grader", "retina_admin"):
            model_serialized["id"] = response.data["id"]
            response.data["image"] = str(response.data["image"])
            assert response.data == model_serialized

    def test_create_view_wrong_user_id(
        self, TwoRetinaPolygonAnnotationSets, rf, user_type
    ):
        model_build = PolygonAnnotationSetFactory.build()
        model_serialized = PolygonAnnotationSetSerializer(model_build).data
        image = ImageFactory()
        model_serialized["image"] = str(image.id)
        other_user = UserFactory()
        model_serialized["grader"] = other_user.id
        model_json = json.dumps(model_serialized)

        response = view_test(
            "create",
            user_type,
            self.namespace,
            self.basename,
            TwoRetinaPolygonAnnotationSets.grader1,
            TwoRetinaPolygonAnnotationSets.polygonset1,
            rf,
            PolygonAnnotationSetViewSet,
            model_json,
            check_response_status_code=False,
        )
        if user_type == "retina_admin":
            model_serialized["id"] = response.data["id"]
            response.data["image"] = str(response.data["image"])
            assert response.data == model_serialized
        elif user_type == "retina_grader":
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert (
                str(response.data["grader"][0])
                == "User is not allowed to create annotation for other grader"
            )
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_view(
        self, TwoRetinaPolygonAnnotationSets, rf, user_type
    ):
        response = view_test(
            "retrieve",
            user_type,
            self.namespace,
            self.basename,
            TwoRetinaPolygonAnnotationSets.grader1,
            TwoRetinaPolygonAnnotationSets.polygonset1,
            rf,
            PolygonAnnotationSetViewSet,
        )
        if user_type == "retina_grader" or user_type == "retina_admin":
            model_serialized = PolygonAnnotationSetSerializer(
                instance=TwoRetinaPolygonAnnotationSets.polygonset1
            ).data
            assert response.data == model_serialized

    def test_update_view(self, TwoRetinaPolygonAnnotationSets, rf, user_type):
        model_serialized = PolygonAnnotationSetSerializer(
            instance=TwoRetinaPolygonAnnotationSets.polygonset1
        ).data
        image = ImageFactory()
        model_serialized["image"] = str(image.id)
        model_serialized["singlepolygonannotation_set"] = []
        model_json = json.dumps(model_serialized)

        response = view_test(
            "update",
            user_type,
            self.namespace,
            self.basename,
            TwoRetinaPolygonAnnotationSets.grader1,
            TwoRetinaPolygonAnnotationSets.polygonset1,
            rf,
            PolygonAnnotationSetViewSet,
            model_json,
        )

        if user_type in ("retina_grader", "retina_admin"):
            response.data["image"] = str(response.data["image"])
            response.data["singlepolygonannotation_set"] = []
            assert response.data == model_serialized

    def test_partial_update_view(
        self, TwoRetinaPolygonAnnotationSets, rf, user_type
    ):
        model_serialized = PolygonAnnotationSetSerializer(
            instance=TwoRetinaPolygonAnnotationSets.polygonset1
        ).data
        image = ImageFactory()
        model_serialized["image"] = str(image.id)
        model_serialized["singlepolygonannotation_set"] = []
        model_json = json.dumps(model_serialized)

        response = view_test(
            "partial_update",
            user_type,
            self.namespace,
            self.basename,
            TwoRetinaPolygonAnnotationSets.grader1,
            TwoRetinaPolygonAnnotationSets.polygonset1,
            rf,
            PolygonAnnotationSetViewSet,
            model_json,
        )

        if user_type in ("retina_grader", "retina_admin"):
            response.data["image"] = str(response.data["image"])
            response.data["singlepolygonannotation_set"] = []
            assert response.data == model_serialized

    def test_destroy_view(self, TwoRetinaPolygonAnnotationSets, rf, user_type):
        view_test(
            "destroy",
            user_type,
            self.namespace,
            self.basename,
            TwoRetinaPolygonAnnotationSets.grader1,
            TwoRetinaPolygonAnnotationSets.polygonset1,
            rf,
            PolygonAnnotationSetViewSet,
        )
        if user_type in ("retina_grader", "retina_admin"):
            assert not PolygonAnnotationSet.objects.filter(
                id=TwoRetinaPolygonAnnotationSets.polygonset1.id
            ).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type",
    [
        None,
        "normal_user",
        "retina_grader_non_allowed",
        "retina_grader",
        "retina_admin",
    ],
)
class TestSinglePolygonAnnotationViewSet:
    namespace = "retina:api"
    basename = "singlepolygonannotation"

    def test_list_view(self, TwoRetinaPolygonAnnotationSets, rf, user_type):
        response = view_test(
            "list",
            user_type,
            self.namespace,
            self.basename,
            TwoRetinaPolygonAnnotationSets.grader1,
            None,
            rf,
            SinglePolygonViewSet,
        )
        if user_type == "retina_grader":
            serialized_data = SinglePolygonAnnotationSerializer(
                TwoRetinaPolygonAnnotationSets.polygonset1.singlepolygonannotation_set.all(),
                many=True,
            ).data
            assert response.data == serialized_data
        elif user_type == "retina_admin":
            serialized_data = SinglePolygonAnnotationSerializer(
                TwoRetinaPolygonAnnotationSets.polygonset1.singlepolygonannotation_set.all()
                | TwoRetinaPolygonAnnotationSets.polygonset2.singlepolygonannotation_set.all(),
                many=True,
            ).data
            assert response.data == serialized_data

    def test_create_view(self, TwoRetinaPolygonAnnotationSets, rf, user_type):
        model_build = SinglePolygonAnnotationFactory.build()
        model_serialized = SinglePolygonAnnotationSerializer(model_build).data
        annotation_set = PolygonAnnotationSetFactory(grader=TwoRetinaPolygonAnnotationSets.grader1)
        model_serialized["annotation_set"] = str(annotation_set.id)
        model_json = json.dumps(model_serialized)

        response = view_test(
            "create",
            user_type,
            self.namespace,
            self.basename,
            TwoRetinaPolygonAnnotationSets.grader1,
            None,
            rf,
            SinglePolygonViewSet,
            model_json,
        )
        if user_type in ("retina_grader", "retina_admin"):
            model_serialized["id"] = response.data["id"]
            response.data["annotation_set"] = str(
                response.data["annotation_set"]
            )
            assert response.data == model_serialized

    def test_retrieve_view(self, TwoPolygonAnnotationSets, rf, user_type):
        response = view_test(
            "retrieve",
            user_type,
            self.namespace,
            self.basename,
            TwoRetinaPolygonAnnotationSets.grader1,
            TwoRetinaPolygonAnnotationSets.polygonset1.singlepolygonannotation_set.first(),
            rf,
            SinglePolygonViewSet,
        )
        if user_type == "retina_grader" or user_type == "retina_admin":
            model_serialized = SinglePolygonAnnotationSerializer(
                TwoRetinaPolygonAnnotationSets.polygonset1.singlepolygonannotation_set.first()
            ).data
            assert response.data == model_serialized

    def test_update_view(self, TwoRetinaPolygonAnnotationSets, rf, user_type):
        model_serialized = SinglePolygonAnnotationSerializer(
            TwoRetinaPolygonAnnotationSets.polygonset1.singlepolygonannotation_set.first()
        ).data
        annotation_set = PolygonAnnotationSetFactory(grader=TwoRetinaPolygonAnnotationSets.grader1)
        model_serialized["annotation_set"] = str(annotation_set.id)
        model_json = json.dumps(model_serialized)

        response = view_test(
            "update",
            user_type,
            self.namespace,
            self.basename,
            TwoRetinaPolygonAnnotationSets.grader1,
            TwoRetinaPolygonAnnotationSets.polygonset1.singlepolygonannotation_set.first(),
            rf,
            SinglePolygonViewSet,
            model_json,
        )

        if user_type in ("retina_grader", "retina_admin"):
            response.data["annotation_set"] = str(
                response.data["annotation_set"]
            )
            assert response.data == model_serialized

    def test_partial_update_view(
        self, TwoRetinaPolygonAnnotationSets, rf, user_type
    ):
        model_serialized = SinglePolygonAnnotationSerializer(
            TwoRetinaPolygonAnnotationSets.polygonset1.singlepolygonannotation_set.first()
        ).data
        annotation_set = PolygonAnnotationSetFactory(grader=TwoRetinaPolygonAnnotationSets.grader1)
        model_serialized["annotation_set"] = str(annotation_set.id)
        model_json = json.dumps(model_serialized)

        response = view_test(
            "partial_update",
            user_type,
            self.namespace,
            self.basename,
            TwoRetinaPolygonAnnotationSets.grader1,
            TwoRetinaPolygonAnnotationSets.polygonset1.singlepolygonannotation_set.first(),
            rf,
            SinglePolygonViewSet,
            model_json,
        )

        if user_type in ("retina_grader", "retina_admin"):
            response.data["annotation_set"] = str(
                response.data["annotation_set"]
            )
            assert response.data == model_serialized

    def test_destroy_view(self, TwoRetinaPolygonAnnotationSets, rf, user_type):
        view_test(
            "destroy",
            user_type,
            self.namespace,
            self.basename,
            TwoRetinaPolygonAnnotationSets.grader1,
            TwoRetinaPolygonAnnotationSets.polygonset1.singlepolygonannotation_set.first(),
            rf,
            SinglePolygonViewSet,
        )
        if user_type in ("retina_grader", "retina_admin"):
            assert not PolygonAnnotationSet.objects.filter(
                id=TwoRetinaPolygonAnnotationSets.polygonset1.singlepolygonannotation_set.first().id
            ).exists()
