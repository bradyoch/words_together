from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from words_together.auth import login_required, get_user_by_name, get_user_by_id
from words_together.db import get_db
from words_together.user import get_partner_by_id

bp = Blueprint('journal', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    posts = []

    partner = get_partner_by_id(g.user['id'])

    if partner is not None:
        posts = db.execute(
            'SELECT up.id, date(up.created) as created,'
            ' up.body as ubody, pp.body as pbody'
            ' FROM post up JOIN post pp'
            ' ON up.created = pp.created AND up.id != pp.id'
            ' WHERE up.id = :id',
            {'id': g.user['id']}
        ).fetchall()
    else:
        if g.user['partner']:
            flash('Partner must select you as a partner too')
        else:
            flash('Must have a partner to view posts')


    return render_template('journal/index.html', posts=posts, partner=partner)

@bp.route('/')
def redir():
    redirect(url_for('auth.login'))

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    db = get_db()
    partner = get_partner_by_id(g.user['id'])

    if partner is None:
        flash('Need a partner to make posts')
        return redirect('/')
    elif request.method == 'POST':
        body = request.form['body']

        db.execute(
            'INSERT INTO post (body, author_id)'
            ' VALUES (?, ?)',
            (body, g.user['id'])
        )
        db.commit()
        return redirect(url_for('journal.index'))

    return render_template('journal/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT id, author_id, body, date(created) as created'
        ' FROM post'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Journal id {} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        body = request.form['body']
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET body = ?'
                ' WHERE id = ?',
                (body, id)
            )
            db.commit()
            return redirect(url_for('journal.index'))

    return render_template('journal/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('journal.index'))
