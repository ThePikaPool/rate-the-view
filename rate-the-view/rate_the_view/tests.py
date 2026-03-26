import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from rate_the_view.models import Comment, Follow, Post


# Temporary media folder for tests so uploaded test images
# do not get saved into the real media directory.
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


def get_test_image():
    """
    Returns a tiny valid GIF image for upload tests.
    This avoids Pillow/django-resized errors during testing.
    """
    return SimpleUploadedFile(
        name='test.gif',
        content=(
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
            b'\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00'
            b'\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01'
            b'\x00\x3b'
        ),
        content_type='image/gif'
    )


# --------------------------------------------------
# Signup view tests
# --------------------------------------------------

class SignupViewTests(TestCase):
    def test_signup_creates_user_logs_them_in_and_redirects(self):
        """
        Test that a valid signup request:
        - creates a new user
        - logs the user in
        - redirects to the home page
        """
        response = self.client.post(reverse('rate_the_view:signup'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
        })

        self.assertRedirects(response, reverse('rate_the_view:home'))
        self.assertTrue(User.objects.filter(username='testuser').exists())

        user = User.objects.get(username='testuser')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)

    def test_signup_fails_if_passwords_do_not_match(self):
        """
        Test that signup fails when the two passwords do not match.
        No user should be created.
        """
        response = self.client.post(reverse('rate_the_view:signup'), {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password1': 'Password123',
            'password2': 'DifferentPassword123',
        })

        self.assertFalse(User.objects.filter(username='testuser2').exists())
        self.assertEqual(response.status_code, 302)


# --------------------------------------------------
# Upload view tests
# --------------------------------------------------

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UploadViewTests(TestCase):
    def setUp(self):
        """
        Create a test user for upload view tests.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )

    def test_upload_creates_post_for_logged_in_user(self):
        """
        Test that a logged-in user can upload a valid post
        and that the post is stored correctly in the database.
        """
        self.client.login(username='testuser', password='TestPassword123')

        response = self.client.post(reverse('rate_the_view:upload'), {
            'title': 'My Test Post',
            'location': 'Tokyo',
            'description': 'Nice view',
            'image': get_test_image(),
        })

        self.assertRedirects(response, reverse('rate_the_view:home'))
        self.assertEqual(Post.objects.count(), 1)

        post = Post.objects.first()
        self.assertEqual(post.title, 'My Test Post')
        self.assertEqual(post.location, 'Tokyo')
        self.assertEqual(post.description, 'Nice view')
        self.assertEqual(post.created_by, self.user)

    def test_upload_does_not_create_post_if_title_or_image_missing(self):
        """
        Test that a post is not created if required upload data
        such as the title or image is missing.
        """
        self.client.login(username='testuser', password='TestPassword123')

        response = self.client.post(reverse('rate_the_view:upload'), {
            'title': '',
            'location': 'Tokyo',
            'description': 'Nice view',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 0)


# --------------------------------------------------
# Comment view tests
# --------------------------------------------------

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CommentViewTests(TestCase):
    def setUp(self):
        """
        Create a test user and a post for comment tests.
        """
        self.user = User.objects.create_user(
            username='commentuser',
            email='comment@example.com',
            password='TestPassword123'
        )

        self.post = Post.objects.create(
            title='Test Post',
            location='Tokyo',
            description='Nice place',
            image=get_test_image(),
            created_by=self.user
        )

    def test_authenticated_user_can_add_comment_to_post(self):
        """
        Test that a logged-in user can add a comment to a post
        and that the comment is linked correctly.
        """
        self.client.login(username='commentuser', password='TestPassword123')

        response = self.client.post(
            reverse('rate_the_view:view_post_detail', kwargs={'slug': self.post.slug}),
            {'comment': 'Great post!'}
        )

        self.assertRedirects(
            response,
            reverse('rate_the_view:view_post_detail', kwargs={'slug': self.post.slug})
        )

        self.assertEqual(Comment.objects.count(), 1)

        comment = Comment.objects.first()
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.text, 'Great post!')

    def test_blank_comment_is_not_saved(self):
        """
        Test that an empty comment is not saved to the database.
        """
        self.client.login(username='commentuser', password='TestPassword123')

        response = self.client.post(
            reverse('rate_the_view:view_post_detail', kwargs={'slug': self.post.slug}),
            {'comment': ''}
        )

        self.assertEqual(Comment.objects.count(), 0)
        self.assertIn(response.status_code, [200, 302])


# --------------------------------------------------
# Vote view tests
# --------------------------------------------------

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class VoteViewTests(TestCase):
    def setUp(self):
        """
        Create a user and post for upvote/downvote tests.
        """
        self.user = User.objects.create_user(
            username='voteuser',
            email='vote@example.com',
            password='TestPassword123'
        )

        self.post = Post.objects.create(
            title='Vote Test Post',
            location='Tokyo',
            description='Nice place',
            image=get_test_image(),
            created_by=self.user
        )

    def test_upvote_and_downvote_toggle_correctly(self):
        """
        Test that:
        - upvoting adds an upvote
        - upvoting again removes it
        - downvoting adds a downvote
        - upvoting after downvoting removes the downvote and adds an upvote
        """
        self.client.login(username='voteuser', password='TestPassword123')

        # Add upvote
        response = self.client.post(
            reverse('rate_the_view:upvote', kwargs={'slug': self.post.slug})
        )
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertTrue(self.post.upvotes.filter(id=self.user.id).exists())
        self.assertFalse(self.post.downvotes.filter(id=self.user.id).exists())

        # Remove upvote
        response = self.client.post(
            reverse('rate_the_view:upvote', kwargs={'slug': self.post.slug})
        )
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertFalse(self.post.upvotes.filter(id=self.user.id).exists())

        # Add downvote
        response = self.client.post(
            reverse('rate_the_view:downvote', kwargs={'slug': self.post.slug})
        )
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertTrue(self.post.downvotes.filter(id=self.user.id).exists())
        self.assertFalse(self.post.upvotes.filter(id=self.user.id).exists())

        # Switch from downvote to upvote
        response = self.client.post(
            reverse('rate_the_view:upvote', kwargs={'slug': self.post.slug})
        )
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertTrue(self.post.upvotes.filter(id=self.user.id).exists())
        self.assertFalse(self.post.downvotes.filter(id=self.user.id).exists())


# --------------------------------------------------
# Follow / unfollow view tests
# --------------------------------------------------

class FollowViewTests(TestCase):
    def setUp(self):
        """
        Create two users for follow/unfollow tests.
        """
        self.user1 = User.objects.create_user(
            username='user1',
            password='TestPassword123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='TestPassword123'
        )

    def test_follow_and_unfollow_toggle(self):
        """
        Test that following a user creates a Follow object
        and using the same action again removes it.
        """
        self.client.login(username='user1', password='TestPassword123')

        # Follow user2
        response = self.client.post(
            reverse('rate_the_view:toggle_follow', kwargs={'username': 'user2'})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Follow.objects.count(), 1)

        follow = Follow.objects.first()
        self.assertEqual(follow.follower, self.user1)
        self.assertEqual(follow.following, self.user2)

        # Unfollow user2
        response = self.client.post(
            reverse('rate_the_view:toggle_follow', kwargs={'username': 'user2'})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Follow.objects.count(), 0)


# --------------------------------------------------
# Edit / delete permission tests
# --------------------------------------------------

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPermissionTests(TestCase):
    def setUp(self):
        """
        Create an owner, a second user, and a post
        for edit/delete permission tests.
        """
        self.owner = User.objects.create_user(
            username='owner',
            password='TestPassword123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='TestPassword123'
        )

        self.post = Post.objects.create(
            title='Owner Post',
            location='Tokyo',
            description='Original description',
            image=get_test_image(),
            created_by=self.owner
        )

    def test_post_owner_can_edit_post(self):
        """
        Test that the owner of a post can edit it successfully.
        """
        self.client.login(username='owner', password='TestPassword123')

        response = self.client.post(
            reverse('rate_the_view:edit_post', kwargs={'slug': self.post.slug}),
            {
                'title': 'Updated Title',
                'location': 'Kyoto',
                'description': 'Updated description',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')
        self.assertEqual(self.post.location, 'Kyoto')
        self.assertEqual(self.post.description, 'Updated description')

    def test_non_owner_cannot_edit_post(self):
        """
        Test that a user who does not own the post
        cannot edit it.
        """
        self.client.login(username='otheruser', password='TestPassword123')

        response = self.client.post(
            reverse('rate_the_view:edit_post', kwargs={'slug': self.post.slug}),
            {
                'title': 'Hacked Title',
                'location': 'Fake Place',
                'description': 'Should not be allowed',
            }
        )

        self.assertEqual(response.status_code, 404)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Owner Post')
        self.assertEqual(self.post.location, 'Tokyo')
        self.assertEqual(self.post.description, 'Original description')

    def test_post_owner_can_delete_post(self):
        """
        Test that the owner of a post can delete it.
        """
        self.client.login(username='owner', password='TestPassword123')

        response = self.client.post(
            reverse('rate_the_view:delete_post', kwargs={'slug': self.post.slug})
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_non_owner_cannot_delete_post(self):
        """
        Test that a user who does not own the post
        cannot delete it.
        """
        self.client.login(username='otheruser', password='TestPassword123')

        response = self.client.post(
            reverse('rate_the_view:delete_post', kwargs={'slug': self.post.slug})
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())