from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name=_("Номер телефона")
    )

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return self.email or self.username