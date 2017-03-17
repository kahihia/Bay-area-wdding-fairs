from django.core.wsgi import get_wsgi_application
from dj_static import Cling

import newrelic.agent
newrelic.agent.initialize('newrelic.ini')

application = Cling(get_wsgi_application())