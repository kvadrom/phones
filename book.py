# -*- coding: utf-8 -*-
from flask import flash, redirect, url_for, render_template, Flask, request, jsonify, abort
from flaskext.sqlalchemy import SQLAlchemy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://localhost/phones?user=book'

db = SQLAlchemy(app)

class Entry(db.Model):
    __tablename__ = 'entries'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    desc = db.Column(db.String(400))
    phones = db.relation("Phone", backref="entry", cascade="all, delete, delete-orphan")
    comments = db.relation("Comment", backref="entry", cascade="all, delete")


class Phone(db.Model):
    __tablename__ = 'phones'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(60))
    desc = db.Column(db.String(400))
    entry_id = db.Column(db.Integer, db.ForeignKey('entries.id'))


class Comment(db.Model):

    __tablename__ = 'comments'
    __table_args__ = {'mysql_engine':'MyIsam'}

    relation_name = 'children'

    id = db.Column(db.Integer(unsigned=True), primary_key=True, autoincrement=True)
    text = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='CASCADE', onupdate='CASCADE'))
    entry_id = db.Column(db.Integer, db.ForeignKey('entries.id'))
    children = db.relation('Comment', cascade='all, delete', backref=db.backref('parent', remote_side=[id]))

@app.route('/')
def index():
    entries = Entry.query.all()
    return render_template('index.html', entries=entries)
   

@app.route('/commentform')
def commentform():
    return """<div class="r">
              <textarea id="response" name=text>Ваш коментар</textarea><br>
              <a class="respond_comment" href="javascript: void(0);">послати</a><br>
              </div>"""

def render_comment(c, x=0):
    if c.active:
    	return """<div class="comment layer%d" id="comment%s">
                  <a href="javascript: void(0);" style="float: right" id="dcomment">x</a>
                  <p>%s</p>
                  <a class="respond" href="javascript: void(0);">Відповісти</a><br>
                  </div>
               """ % (x, c.id, c.text)
    else:
    	return """<div class="comment layer%d" id="comment%s">
                  <p>Коментар було видалено</p>
                  <br>
                  </div>
               """ % (x, c.id)
    	

@app.route('/submitcomment')
def submit_comment():
    entry_id = request.args.get('entry', '')
    comment = request.args.get('comment', '')
    if comment and entry_id:
    	entry = Entry.query.filter(Entry.id==int(entry_id)).first()
    	c = Comment(text=comment)
    	c.entry = entry
    	db.session.add(c)
    	db.session.commit()
    	return render_comment(c, 0)
    return ""

@app.route('/deletecomment')
def delete_comment():
    comment = request.args.get('comment', '').replace('comment', '')
    if comment:
    	c = Comment.query.filter(Comment.id==int(comment)).first()
    	if c.children:
    	    c.active = False
    	else:
    	    db.session.delete(c)
    	db.session.commit()
    	return "<p>Коментар видалено</p>"
    return ""

@app.route('/respondcomment')
def respond_comment():
    entry_id = request.args.get('entry', '')
    comment_text = request.args.get('comment', '')
    parent_id = request.args.get('parent', '').replace('comment', '')
    layer = request.args.get('layer', '').split()[1].replace('layer', '')
    if comment_text and entry_id and parent_id:
    	parent = Comment.query.filter(Comment.id==int(parent_id)).first()
    	if parent.active:
    	    entry = Entry.query.filter(Entry.id==int(entry_id)).first()
    	    c = Comment(text=comment_text)
    	    c.parent_id = int(parent_id)
    	    db.session.add(c)
    	    db.session.commit()
    	    return render_comment(c, int(layer)+1)
    	else:
    	    return "<p>Не можна відповідати на видалений коментар</p>"
    return ""

@app.route('/search', methods=['POST'])
def search():
    query = "%" + request.form['search'] + "%"
    print query
    
    select = db.text('SELECT entries.id FROM entries \
                        LEFT JOIN phones ON entries.id=phones.entry_id \
                        WHERE entries.title LIKE "'+query+'" \
                        OR entries.desc LIKE "'+query+'" \
                        OR phones.number LIKE "'+query+'" \
                        OR phones.desc LIKE "'+query+'" \
                        GROUP BY entries.id;')
    print select
    ids = db.session.execute(select).fetchall()
    ids = [x[0] for x in ids]
    print ids
    
    entries = db.session.query(Entry).filter(Entry.id.in_(ids)).all()
    return render_template('index.html', entries=entries)

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
    	title = request.form['title']
    	desc = request.form['desc']
    	e = Entry(title=title, desc=desc)
    	db.session.add(e)
    	db.session.commit()
    	return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/phones/<int:entry_id>')
def ajax_load_phones(entry_id):
    entry = Entry.query.filter(Entry.id==entry_id).first()
    return render_template('phones.html', context=entry)

@app.route('/_add_phone')
def add_phone():
    number = request.args.get('number', '')
    desc = request.args.get('desc', '')
    entry_id = request.args.get('entry', '')
    entry = Entry.query.filter(Entry.id==entry_id).first()
    if number:
    	if not Phone.query.filter(Phone.number == number).filter(Phone.entry_id==entry.id).all():
    	    phone = Phone(number=number, desc=desc)
    	    phone.entry = entry
    	    db.session.add(phone)
    	    db.session.commit()
    return jsonify()

def sort_comments(comments, x):
    res = []
    for comment in comments:
    	res.append(render_comment(comment, x))
    	if comment.children:
    	    x += 1
    	    res.extend(sort_comments(comment.children, x))
    	    x -= 1
    return res

@app.route('/entry/<int:entry_id>')
def entry(entry_id):
    entry = Entry.query.filter(Entry.id==entry_id).first()
    comments = sort_comments(entry.comments, 0)
    return render_template('entry.html', context=entry, comments=comments)

@app.route('/entry/show/<int:entry_id>')
def show_entry(entry_id):
    entry = Entry.query.filter(Entry.id==entry_id).first()
    return render_template('showentry.html', context=entry)

@app.route('/_delete_phone')
def delete_phone():
    phone = request.args.get('phone')
    entry_id = request.args.get('entry')
    phone = Phone.query.filter(Phone.id == phone).first()
    db.session.delete(phone)
    db.session.commit()
    return jsonify()

@app.route('/_update_entry')
def update_entry():
    entry_id = request.args.get('entry')
    title = request.args.get('title')
    desc = request.args.get('desc')
    entry = Entry.query.filter(Entry.id==entry_id).first()
    if title != entry.title or desc != entry.desc:
    	if title:
    	    entry.title = title
    	entry.desc = desc
    	db.session.commit()
    return jsonify()

@app.route('/delete_entry/<int:entry_id>')
def delete_entry(entry_id):
    entry = Entry.query.filter(Entry.id==entry_id).first()
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/entry/edit/<entry_id>')
def edit_entry(entry_id):
    entry = Entry.query.filter(Entry.id==entry_id).first()
    return render_template('edit.html', context=entry)


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
