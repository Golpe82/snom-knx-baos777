from django import forms

from knx.models import AlsStatus

class AmbientlightSensor(forms.ModelForm):
    ip_address = forms.CharField(disabled=True)
    value = forms.CharField(disabled=True)

    class Meta:
        model = AlsStatus
        fields = [
            "device_name",
            "ip_address",
            "mac_address",
            "value"
        ]

AlsFormSet = forms.modelformset_factory(AlsStatus,form=AmbientlightSensor)