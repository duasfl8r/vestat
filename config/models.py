from decimal import Decimal
from django.db import models

class VestatConfiguration(models.Model):
    saldo_inicial_gorjetas = models.DecimalField("Saldo inicial dos 10%", max_digits=10, decimal_places=2, default=0)
