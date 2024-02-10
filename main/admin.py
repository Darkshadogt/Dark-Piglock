from django.contrib import admin
from .models import Profile, PasswordModel, CardModel, NoteModel

# Register your models here.
admin.site.register(Profile)
admin.site.register(PasswordModel)
admin.site.register(CardModel)
admin.site.register(NoteModel)
