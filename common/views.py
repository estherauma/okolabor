from django.views.generic import CreateView
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.contrib import messages

class BaseCreateView(CreateView):
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)
    
