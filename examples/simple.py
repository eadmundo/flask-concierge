from flask import Flask
# , render_template, redirect, url_for
from flask_concierge import (
    Concierge, SignUp, LogIn, PassphraseResetRequest
)


class SimpleSignUp(SignUp):

    def queue_confirmation_email(self, msg):
        print msg


class SimplePassphraseResetRequest(PassphraseResetRequest):

    def queue_reset_email(self, msg):
        print msg


concierge = Concierge()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretsauce'
app.config['ITSDANGEROUS_SECRET_KEY'] = 'secretsauce'

app.config['CONCIERGE_LOGIN_TEMPLATE'] = 'different_login.html'
app.config['CONCIERGE_ACTIVATION_ROUTE'] = '/activate/<code>'

app.add_url_rule('/', view_func=LogIn.as_view('login'))
app.add_url_rule('/signup', view_func=SimpleSignUp.as_view('signup'))
app.add_url_rule(
    '/password-reset-request',
    view_func=SimplePassphraseResetRequest.as_view(
        'password_reset_request')
)

concierge.init_app(app)

if __name__ == "__main__":
    # import pdb; pdb.set_trace()
    app.run(debug=True)
