from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time, nullable=True)
    location = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Event {self.title}>'


with app.app_context():
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

        if not title or not event_date_str:
            flash('Название и дата обязательны!', 'error')
            return redirect(url_for('add_event'))

        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
            event_time = None
            if event_time_str:
                event_time = datetime.strptime(event_time_str, '%H:%M').time()
        except ValueError:
            flash('Неверный формат даты или времени!', 'error')
            return redirect(url_for('add_event'))

        new_event = Event(
            title=title,
            description=description,
            event_date=event_date,
            event_time=event_time,
            location=location
        )

        db.session.add(new_event)
        db.session.commit()
        flash('Мероприятие успешно добавлено!', 'success')
        return redirect(url_for('index'))

    return render_template('add_event.html')


@app.route('/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event_date_str = request.form.get('event_date')
        event_time_str = request.form.get('event_time')
        event.location = request.form.get('location')

        if not event.title or not event_date_str:
            flash('Название и дата обязательны!', 'error')
            return redirect(url_for('edit_event', event_id=event_id))

        try:
            event.event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
            if event_time_str:
                event.event_time = datetime.strptime(event_time_str, '%H:%M').time()
            else:
                event.event_time = None
        except ValueError:
            flash('Неверный формат даты или времени!', 'error')
            return redirect(url_for('edit_event', event_id=event_id))

        db.session.commit()
        flash('Мероприятие обновлено!', 'success')
        return redirect(url_for('index'))

    return render_template('edit_event.html', event=event)


@app.route('/delete/<int:event_id>')
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Мероприятие удалено!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
