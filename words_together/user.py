from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from words_together.auth import login_required, get_user_by_name
from words_together.db import get_db


bp = Blueprint('user', __name__)

def get_partner_by_id(id):
    return get_db().execute(
        'SELECT username, id'
        ' FROM user'
        ' WHERE id = ('
        '  SELECT partner FROM user'
        '   WHERE id = :id )',
        {'id': id}
    ).fetchone()

def get_partner_by_name(name):
    return get_db().execute(
        'SELECT username, id'
        ' FROM user'
        ' WHERE id = ('
        '  SELECT partner FROM user'
        '   WHERE username = :name )',
        {'name': name}
    ).fetchone()

@bp.route('/user/<string:name>', methods=('GET', 'POST'))
def user(name):
    db = get_db()
    partner = get_partner_by_name(name)
    posts = []

    if user is None:
        abort(403)

    if name == g.user['username']:
        posts = db.execute(
            'SELECT date(created) as created, body, id'
            ' FROM post WHERE author_id = :id',
            {'id': g.user['id']}
        ).fetchall()

    if request.method == "POST":
        new_partner = get_user_by_name(request.form['name'])

        if new_partner is not None:
            db.execute(
                'UPDATE user SET partner = :pid WHERE id = :id',
                {'id': g.user['id'], 'pid':new_partner['id']})
            db.commit()
            flash('Added {} as a friend!'.format(new_partner['username']))
            partner = new_partner
        else:
            flash('Failed to add {} as a friend'.format(request.form['name']))

    return render_template('user/index.html', user=name, partner=partner, posts=posts)

