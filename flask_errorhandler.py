# -*- coding: utf-8 -*-
"""
    flask.ext.errorhandler
    ~~~~~~~~~~~~~~~~~~~~~~

    This module provides a generic error handler for blueprints.

    :copyright: (c) 2014 by Su Yeol Jeon.
    :license: BSD, see LICENSE for more details.
"""

__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)
__author__ = 'Su Yeol Jeon'
__license__ = 'MSD'
__copyright__ = '(c) 2014 by Su Yeol Jeon'
__all__ = ['ErrorHandler']

from flask import Blueprint, request
from werkzeug.exceptions import HTTPException
import traceback


class FakeHandler(dict):
    """A class for replacement of `app`'s `error_handler_spec[None]`.
    """

    def __init__(self, errorhandler):
        self.errorhandler = errorhandler

    def get(self, code, default=None):
        """Returns an predefined error handler instead of handler spec.
        """
        if code is None:
            return ()
        return self.errorhandler


class ErrorHandler(object):
    """Flask error handler extension. It provides a generic error handler for
    blueprints. Each blueprint can have different generic error handler.

    Example::

            from flask import Flask, Blueprint
            from flask.ext.errorhandler import ErrorHandler
            import json

            app = Flask(__name__)
            api_blueprint = Blueprint('api', 'api')
            web_blueprint = Blueprint('web', 'web')

            errorhandler = ErrorHandler()
            errorhandler.init_app(app)

            @errorhandler.errorhandler(api_blueprint)
            def handle_error(e):
                data = {
                    'error': {
                        'code': e.code,
                        'message': e.description
                    }
                }
                response = Response(json.dumps(data),
                                    mimetype='application/json',
                                    status=e.code)
                return response

            @errorhandler.errorhandler(web_blueprint)
            def handle_error(e):
                body = '<h1>%d</h1><p>%s</p>' % (e.code, e.description)
                response = Response(body, mimetype='text/html', status=e.code)
                return response
    """

    #: An Flask app instance
    _app = None

    #:Defined error handlers. {blueprint.name: function}
    _errorhandlers = {}

    #: Custom exception loader callback.
    _error_loader_callback = None

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self._app = app
        app.error_handler_spec[None] = FakeHandler(self._handle_error)

    def _handle_error(self, e):
        """Returns handled excpetion. Detects blueprint from global
        :class:`~flask.wrappers.Request` object, and passes exception object to
        its `registered_errorhandler`.
        """
        blueprint = self._detect_blueprint()

        if isinstance(e, HTTPException):
            if self._error_loader_callback is not None:
                e = self._error_loader_callback(e)  # load custom exception
        else:
            print traceback.format_exc()
            e = HTTPException()

        if blueprint and blueprint.name in self._errorhandlers:
            return self._errorhandlers[blueprint.name](e)
        return e

    def _detect_blueprint(self):
        """Detects and returns blueprint from the request.
        """
        subdomain = request.host.split(self._app.config['SERVER_NAME'])[0][:-1]
        paths = request.path.split('/', 1)

        blueprint = None
        max_len = 0
        for name, bp in self._app.blueprints.iteritems():
            if not isinstance(bp, Blueprint):
                continue

            if (blueprint, bp.subdomain, bp.url_prefix) == (None, None, None):
                blueprint = bp
                continue

            if subdomain != bp.subdomain:
                continue

            if bp.url_prefix is None:
                blueprint = bp
                break

            # detects blueprint with `subdomain` and `url_prefix`.
            blueprint_paths = bp.url_prefix.split('/', 1)
            l = len([i for i, j in zip(paths, blueprint_paths) if i == j])
            if l > max_len:
                blueprint = bp
                max_len = l

        return blueprint

    def errorhandler(self, blueprint):
        """Registers an error handler for blueprint.

        :param blueprint: a blueprint whose errors are handled by this handler.
        """
        def decorator(f):
            self._errorhandlers[blueprint.name] = f
            return f
        return decorator

    def error_loader(self, f):
        """Registers a custom error loader::

            @errorhandler.error_loader
            def load_error(e):
                if e.code == 401:
                    e = NotAuthorizedError()
                elif e.code == 404:
                    e = PageNotFoundError()
                return e

        You can easily implement your custom HTTP exceptions using this.
        """
        self._error_loader_callback = f
        return f


