from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django_resized import ResizedImageField


class Post(models.Model):
    title = models.CharField(max_length=200)
    post_id = models.AutoField(primary_key=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    image = ResizedImageField(size=[800, 600], upload_to='posts/', blank=True, null=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_posts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    upvotes = models.ManyToManyField(
        User,
        related_name='upvoted_posts',
        blank=True,
        verbose_name="Users who upvoted"
    )

    downvotes = models.ManyToManyField(
        User,
        related_name='downvoted_posts',
        blank=True,
        verbose_name="Users who downvoted"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('rate_the_view:view_post_detail', kwargs={'slug': self.slug})

    @property
    def upvote_count(self):
        return self.upvotes.count()

    @property
    def downvote_count(self):
        return self.downvotes.count()

    @property
    def net_score(self):
        return self.upvote_count - self.downvote_count


class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_relationships'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower_relationships'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"