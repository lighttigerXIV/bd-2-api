from flask import Flask
from routes.person import person_blueprint
from routes.events import events_blueprint
from routes.login import login_blueprint
from routes.balance import balance_blueprint
from routes.subscriptions import subscriptions_blueprint
from routes.comments import comments_blueprint
from routes.reservations import reservations_blueprint

app = Flask(__name__)
app.register_blueprint(person_blueprint)
app.register_blueprint(events_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(balance_blueprint)
app.register_blueprint(subscriptions_blueprint)
app.register_blueprint(comments_blueprint)
app.register_blueprint(reservations_blueprint)

app.debug = True

if __name__ == "__main__":
    app.run()
