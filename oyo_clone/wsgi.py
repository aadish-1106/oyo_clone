import os

try:
    import pymysql
    pymysql.version_info = (2, 2, 4, "final", 0)
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oyo_clone.settings')

application = get_wsgi_application()
