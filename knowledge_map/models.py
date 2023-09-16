from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    topic = models.TextField(null=True, blank=True)


class CategoryRelation(models.Model):
    parent = models.ForeignKey(Category, related_name='children', on_delete=models.CASCADE)
    child = models.ForeignKey(Category, related_name='parents', on_delete=models.CASCADE)
    context = models.TextField(null=True, blank=True)

