from crispy_forms.helper import FormHelper
from django.conf import settings
from django.forms import (
    ChoiceField,
    ModelForm,
)

from grandchallenge.core.forms import SaveFormInitMixin
from grandchallenge.core.validators import ExtensionValidator
from grandchallenge.jqfileupload.widgets import uploader
from grandchallenge.workstations.models import (
    Session,
    Workstation,
    WorkstationImage,
)


class WorkstationForm(SaveFormInitMixin, ModelForm):
    class Meta:
        model = Workstation
        fields = ("title", "logo", "description", "public")


class WorkstationImageForm(ModelForm):
    chunked_upload = uploader.UploadedAjaxFileList(
        widget=uploader.AjaxUploadWidget(multifile=False),
        label="Workstation Image",
        validators=[
            ExtensionValidator(allowed_extensions=(".tar", ".tar.gz"))
        ],
        help_text=(
            ".tar.gz archive of the container image produced from the command "
            "'docker save IMAGE | gzip -c > IMAGE.tar.gz'. See "
            "https://docs.docker.com/engine/reference/commandline/save/"
        ),
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields["chunked_upload"].widget.user = user

    class Meta:
        model = WorkstationImage
        fields = (
            "initial_path",
            "http_port",
            "websocket_port",
            "chunked_upload",
        )


class SessionForm(ModelForm):
    region = ChoiceField(
        required=True,
        choices=[
            c
            for c in Session.Region.choices
            if c[0] in settings.WORKSTATIONS_ACTIVE_REGIONS
        ],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.attrs.update({"class": "d-none"})

        self.fields["ping_times"].required = False

    class Meta:
        model = Session
        fields = (
            "region",
            "ping_times",
        )
