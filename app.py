from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'

db = SQLAlchemy(app)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time, nullable=True)
    location = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


db.create_all()


@app.route('/')
def index():
    today = datetime.today().date()
    events = Event.query.order_by(Event.event_date, Event.event_time).all()
    return render_template('index.html', events=events, today=today)


@app.route('/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_date_str = request.form.get('event_date')
        event_time_str = request.form.get('event_time')
        location = request.form.get('location')

        if title == None or title == '':
            flash('Надо название!', 'error')
            return redirect(url_for('add_event'))
        
        if event_date_str == None or event_date_str == '':
            flash('Дата нужна!', 'error')
            return redirect(url_for('add_event'))

        try:
            year = int(event_date_str.split('-')[0])
            month = int(event_date_str.split('-')[1])
            day = int(event_date_str.split('-')[2])
            event_date = datetime(year, month, day).date()
            
            event_time = None
            if event_time_str != None and event_time_str != '':
                hour = int(event_time_str.split(':')[0])
                minute = int(event_time_str.split(':')[1])
                from datetime import time
                event_time = time(hour, minute)
        except:
            flash('Ошибка с датой!', 'error')
            return redirect(url_for('add_event'))

        new_event = Event()
        new_event.title = title
        new_event.description = description
        new_event.event_date = event_date
        new_event.event_time = event_time
        new_event.location = location

        db.session.add(new_event)
        db.session.commit()
        flash('Добавлено!', 'success')
        return redirect(url_for('index'))

    return render_template('add_event.html')


@app.route('/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get(event_id)
    if event == None:
        return 'Нет такого', 404

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_date_str = request.form.get('event_date')
        event_time_str = request.form.get('event_time')
        location = request.form.get('location')

        if title == None or title == '':
            flash('Название надо!', 'error')
            return redirect(url_for('edit_event', event_id=event_id))
        
        if event_date_str == None or event_date_str == '':
            flash('Дата нужна!', 'error')
            return redirect(url_for('edit_event', event_id=event_id))

        try:
            parts = event_date_str.split('-')
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            event.event_date = datetime(year, month, day).date()
            
            if event_time_str != None and event_time_str != '':
                time_parts = event_time_str.split(':')
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                from datetime import time
                event.event_time = time(hour, minute)
            else:
                event.event_time = None
        except:
            flash('Ошибка даты!', 'error')
            return redirect(url_for('edit_event', event_id=event_id))

        event.title = title
        event.description = description
        event.location = location

        db.session.commit()
        flash('Обновлено!', 'success')
        return redirect(url_for('index'))

    return render_template('edit_event.html', event=event)


@app.route('/delete/<int:event_id>')
def delete_event(event_id):
    event = Event.query.get(event_id)
    if event != None:
        db.session.delete(event)
        db.session.commit()
    flash('Удалено!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
