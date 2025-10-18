from django.db import models

class Category(models.Model):
    class Type(models.TextChoices):
        REPLENISHMENT = ("replenishment","Пополнение")
        WRITEOFF = ("writeoff","Списание")
    
    category = models.CharField(max_length=30)
    type = models.CharField(
        max_length=100,
        choices=Type.choices,
        null=True,
        blank=True
    )

class SubCategory(models.Model):
    subcategory = models.CharField(max_length=30)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, related_name="subcategories")

class Recording(models.Model):
    class Status(models.TextChoices):
        BUSINESS = ("business","Бизнес")
        PERSONAL = ("personal","Личное")
        TAX = ("tax","Налог")

    creation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=100,
        choices=Status.choices,
        null=True
    )
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(to=SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    sum = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comment = models.TextField(null=True)