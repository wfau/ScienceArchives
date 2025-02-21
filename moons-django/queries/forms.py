from django import forms
from django.forms.widgets import HiddenInput

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import ExecuteSQL

class SQLQueryForm(forms.ModelForm):

    class Meta:
        model = ExecuteSQL
        fields = ('query', 'timeout', 'format', )
        labels = {
            'timeout': 'Timeout (seconds)'
        }
        help_texts = {
            'timeout': 'Your query will be halted after this time (max 10800)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['query'] = forms.Field(widget=HiddenInput())
        choices=(
            ('html', 'HTML table summary (results are not saved to a file)'),
            ('fits', 'FITS FILE (downloadable with HTML table summary on-screen)'),
            ('votable', 'VOTable FILE (downloadable with HTML table summary on-screen)'),
        )

        self.fields['timeout'].initial = 3600
        self.fields['format'] = forms.ChoiceField(
            choices=choices,
            required=True,
            help_text='The number of rows written to the downloadable files is subject to an upper limit',
        )

        self.helper = FormHelper()
        self.helper.form_tag = False

