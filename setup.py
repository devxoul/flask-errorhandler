from distutils.core import setup
import os

module_path = os.path.join(os.path.dirname(__file__), 'flask_errorhandler.py')
version_line = [line for line in open(module_path)
                if line.startswith('__version_info__')][0]

__version__ = '.'.join(eval(version_line.split('__version_info__ = ')[-1]))

setup(
    name='Flask-ErrorHandler',
    py_modules=['flask_errorhandler'],
    version=__version__,
    description='Generic error handlers for Flask blueprints.',
    long_description=open('README.rst').read(),
    license='BSD',
    author='Su Yeol Jeon',
    author_email='devxoul@gmail.com',
    url='https://github.com/devxoul/flask-errorhandler',
    download_url='https://pypi.python.org/packages/source/F/Flask-ErrorHandler/Flask-ErrorHandler-%s.tar.gz' % __version__,
    keywords=['Flask', 'Blueprint', 'Error', 'Handler'],
    classifiers=[]
)
