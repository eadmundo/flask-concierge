# -*- coding: utf-8 -*-

"""
.. module:: flask_concierge
    :synopsis: ties together various services to provide a standard
        user system.
"""
from flask import (
    Blueprint, render_template, current_app, abort, request, url_for
)
from flask.views import MethodView
from flask_wtf import Form
from wtforms import (
    TextField, PasswordField, HiddenField, validators
)
from itsdangerous import URLSafeSerializer, BadSignature

__all__ = [
    'SignUpForm',
    'LoginForm',
    'PassphraseResetRequestForm',
    'Concierge',
    'PassphraseResetForm'
]

CONFIG_DEFAULTS = {
    'CONCIERGE_LOGIN_TEMPLATE': 'login.html'
}

DEFAULT_CONCIERGE_LOGIN_TEMPLATE = 'login.html'
DEFAULT_CONCIERGE_PWD_RESET_REQUEST_TEMPLATE = 'pwd_reset_request.html'
DEFAULT_CONCIERGE_SIGNUP_CONFIRMATION_TEMPLATE = 'signup_confirmation.html'
DEFAULT_CONCIERGE_SIGNUP_TEMPLATE = 'signup.html'
DEFAULT_CONCIERGE_ACTIVATION_EMAIL_TEMPLATE = 'activation.txt'
DEFAULT_CONCIERGE_RESET_EMAIL_TEMPLATE = 'reset.html'
DEFAULT_CONCIERGE_ACTIVATION_ROUTE = '/activation/<code>'
DEFAULT_CONCIERGE_ACTIVATION_TEMPLATE = 'concierge/activation.html'
DEFAULT_CONCIERGE_RESET_ROUTE = '/reset/<code>'


class ActivateEmailField(TextField):

    def post_validate(self, form, validation_stopped):
        if len(self.errors) == 0:
            self.activation_code = current_app.concierge.\
                activation_serializer.dumps(
                    self.data, salt='activate')


class SignUpForm(Form):
    email = ActivateEmailField(
        u'Email address', validators=[validators.Email()])
    username = TextField(u'Username', validators=[validators.InputRequired()])
    passphrase = PasswordField(u'Passphrase', validators=[
        validators.InputRequired()])


class LoginForm(Form):
    username = TextField(u'Username', validators=[validators.InputRequired()])
    passphrase = PasswordField(
        u'Passphrase', validators=[validators.InputRequired()])
    next = HiddenField(validators=[validators.Optional()])


class PassphraseResetRequestForm(Form):
    email = TextField(
        u'Email address', validators=[validators.Email()]
    )


class PassphraseResetForm(Form):
    passphrase = PasswordField(u'Passphrase', validators=[
        validators.InputRequired()
    ])
    confirm_passphrase = PasswordField(u'Confirm Passphrase', validators=[
        validators.InputRequired(),
        validators.EqualTo(
            'passphrase', message=u'Passphrases must match')
    ])


class LogIn(MethodView):

    def login_form(self, data=None):
        return LoginForm(data)

    def get(self):
        return render_template(
            current_app.config.get(
                'CONCIERGE_LOGIN_TEMPLATE',
                DEFAULT_CONCIERGE_LOGIN_TEMPLATE
            ),
            form=self.login_form()
        )

    def post(self):
        form = self.login_form(request.form)
        if form.validate_on_submit():
            return 'hooray'
        return 'boooo'


class SignUp(MethodView):

    def queue_confirmation_email(self, msg):
        raise NotImplementedError('override queue_confirmation_email method')

    def signup_form(self, data=None):
        return SignUpForm(data)

    def get(self):
        return render_template(
            current_app.config.get(
                'CONCIERGE_SIGNUP_TEMPLATE',
                DEFAULT_CONCIERGE_SIGNUP_TEMPLATE
            ),
            form=self.signup_form())

    def post(self):
        form = self.signup_form(request.form)
        if form.validate_on_submit():
            confirmation_url = url_for(
                'concierge.activate',
                code=form.email.activation_code
            )
            confirmation_email = current_app.jinja_env.get_template(
                current_app.config.get(
                    'CONCIERGE_ACTIVATION_EMAIL_TEMPLATE',
                    DEFAULT_CONCIERGE_ACTIVATION_EMAIL_TEMPLATE
                )
            ).render(confirmation_url=confirmation_url)
            self.queue_confirmation_email(confirmation_email)
            return render_template(
                current_app.config.get(
                    'CONCIERGE_SIGNUP_CONFIRMATION_TEMPLATE',
                    DEFAULT_CONCIERGE_SIGNUP_CONFIRMATION_TEMPLATE
                ))


class PassphraseResetRequest(MethodView):

    def queue_reset_email(self, msg):
        raise NotImplementedError('override queue_reset_email method')

    def password_reset_url(self, email):
        return url_for(
            'concierge.reset',
            code=current_app.concierge.reset_serializer.dumps(email)
        )

    def password_reset_request_form(self, data=None):
        return PassphraseResetRequestForm(data)

    def get(self):
        return render_template(
            current_app.config.get(
                'CONCIERGE_PWD_RESET_REQUEST_TEMPLATE',
                DEFAULT_CONCIERGE_PWD_RESET_REQUEST_TEMPLATE
            ),
            form=self.password_reset_request_form()
        )

    def post(self):
        form = self.password_reset_request_form(request.form)
        if form.validate_on_submit():
            reset_email = current_app.jinja_env.get_template(
                current_app.config.get(
                    'CONCIERGE_RESET_EMAIL_TEMPLATE',
                    DEFAULT_CONCIERGE_RESET_EMAIL_TEMPLATE
                )
            ).render(
                reset_url=self.password_reset_url(
                    form.email.data
                )
            )
            print reset_email
            self.queue_reset_email(reset_email)
            return 'an email has been sent'


class PassphraseReset(MethodView):

    def password_reset_form(self, data=None):
        return PassphraseResetForm(data)

    def get(self, code):
        try:
            email = current_app.concierge.reset_serializer.loads(code)
            return render_template(
                'concierge/reset.html',
                email=email,
                form=self.password_reset_form()
            )
        except BadSignature:
            return abort(404)

    def post(self, code):
        form = self.password_reset_form(request.form)
        if form.validate_on_submit():
            return form.passphrase.data


class Concierge:

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    @property
    def activation_serializer(self):
        if not hasattr(self, '_activation_serializer'):
            self._activation_serializer = URLSafeSerializer(
                self.app.config['ITSDANGEROUS_SECRET_KEY'], salt='activate')
        return self._activation_serializer

    @property
    def reset_serializer(self):
        if not hasattr(self, '_reset_serializer'):
            self._reset_serializer = URLSafeSerializer(
                self.app.config['ITSDANGEROUS_SECRET_KEY'], salt='reset')
        return self._reset_serializer

    @property
    def blueprint(self):
        concierge = Blueprint(
            'concierge',
            __name__,
            template_folder='templates'
        )

        @concierge.route(
            self.app.config.get(
                'CONCIERGE_ACTIVATION_ROUTE',
                DEFAULT_CONCIERGE_ACTIVATION_ROUTE
            )
        )
        def activate(code):
            try:
                email = self.activation_serializer.loads(code)
                return render_template(self.app.config.get(
                    'CONCIERGE_ACTIVATION_TEMPLATE',
                    DEFAULT_CONCIERGE_ACTIVATION_TEMPLATE
                ), email=email)
            except BadSignature:
                return abort(404)

        concierge.add_url_rule(
            self.app.config.get(
                'CONCIERGE_RESET_ROUTE',
                DEFAULT_CONCIERGE_RESET_ROUTE
            ),
            'reset',
            view_func=PassphraseReset.as_view('passphrase_reset')
        )

        return concierge

    def init_app(self, app):
        if self.app is None:
            self.app = app
        app.concierge = self
        app.register_blueprint(self.blueprint)
