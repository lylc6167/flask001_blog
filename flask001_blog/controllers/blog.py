from flask import render_template, Blueprint
from sqlalchemy import func

from uuid import uuid4
import datetime
from os import path

from flask001_blog.models import db, User, Post, Tag, Comment, posts_tags
from flask001_blog.forms import CommentForm


blog_blueprint = Blueprint(
    'blog',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'blog'),
    url_prefix='/blog')  # 最后一个参数为路由前缀，localhost/blog/<ID>


def sidebar_data():

    recent = db.session.query(Post).order_by(
        Post.created_date.desc()
    ).limit(5).all()

    top_tags = db.session.query(
        Tag, func.count(posts_tags.c.post_id).label('total')
    ).join(posts_tags).group_by(Tag).order_by('total DESC').limit(5).all()

    return recent, top_tags


@blog_blueprint.route('/')
@blog_blueprint.route('/<int:page>')
def home(page=1):
    posts = Post.query.order_by(
        Post.created_date.desc()
    ).paginate(page, 10)

    recent, top_tags = sidebar_data()

    return render_template('home.html',
                           posts=posts,
                           recent=recent,
                           top_tags=top_tags)


@blog_blueprint.route('/post/<string:post_id>', methods=('GET', 'POST'))
def post(post_id):

    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(id=str(uuid4()),
                              name=form.name.data)
        new_comment.text = form.text.data
        new_comment.created_time = datetime.datetime.now()
        new_comment.post_id = post_id
        db.session.add(new_comment)
        db.session.commit()

    post = Post.query.get_or_404(post_id)
    tags = post.tags
    comments = post.comments.order_by(Comment.created_time.desc()).all()
    recent, top_tags = sidebar_data()
    return render_template('post.html',
                           post=post,
                           tags=tags,
                           comments=comments,
                           form=form,
                           recent=recent,
                           top_tags=top_tags)


@blog_blueprint.route('/tag/<string:tag_name>')
def tag(tag_name):

    tag = db.session.query(Tag).filter_by(name=tag_name).first_or_404()
    posts = tag.posts.order_by(Post.created_date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template('tag.html',
                           tag=tag,
                           posts=posts,
                           recent=recent,
                           top_tags=top_tags)


@blog_blueprint.route('/user/<string:username>')
def user(username):

    user = db.session.query(User).filter_by(username=username).first_or_404()
    posts = user.posts.prder_by(Post.created_date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template('user.html',
                           user=user,
                           posts=posts,
                           recent=recent,
                           top_tags=top_tags)
