from .models import Post, Comment, Vote


def get_all_posts():
    return Post.objects.all()


def get_post(post_id):
    return Post.objects.get(id=view_id)


def add_post(user, location, description):
    post = Post.objects.create(
        user=user,
        location=location,
        description=description
    )
    return post


def delete_post(post_id):
    post = Post.objects.get(id=post_id)
    post.delete()


def add_comment(user, post, content):
    comment = Comment.objects.create(
        user=user,
        post=post,
        content=content
    )
    return comment


def get_comments(view):
    return Comment.objects.filter(view=view)


def upvote_post(user, post):
    vote = Vote.objects.create(
        user=user,
        post=post,
        upvote=True
    )
    return vote


def downvote_post(user, post):
    vote = Vote.objects.create(
        user=user,
        post=post,
        downvote=True
    )
    return vote