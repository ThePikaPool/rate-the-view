from .models import View, Comment, Vote


def get_all_views():
    return View.objects.all()


def get_view(view_id):
    return View.objects.get(id=view_id)


def add_view(user, location, description):
    view = View.objects.create(
        user=user,
        location=location,
        description=description
    )
    return view


def delete_view(view_id):
    view = View.objects.get(id=view_id)
    view.delete()


def add_comment(user, view, content):
    comment = Comment.objects.create(
        user=user,
        view=view,
        content=content
    )
    return comment


def get_comments(view):
    return Comment.objects.filter(view=view)


def upvote_view(user, view):
    vote = Vote.objects.create(
        user=user,
        view=view,
        upvote=True
    )
    return vote


def downvote_view(user, view):
    vote = Vote.objects.create(
        user=user,
        view=view,
        downvote=True
    )
    return vote