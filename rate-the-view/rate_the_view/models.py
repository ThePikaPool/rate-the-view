from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django_resized import ResizedImageField

class ViewLocation(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    # rating = models.PositiveSmallIntegerField(default = 0)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_view_locations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [-'created_at']
        verbose_name = "View Location"
        verbose_name_plural = "View Locations"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            counter = 1
            while ViewLocation.objects.filter(slug = slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('view_location_detail', kwargs={'slug' : self.slug})

