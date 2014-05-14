Flask-ErrorHandler
==================

Flask-ErrorHandler provides a generic error handler for blueprints.

Sample::

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


