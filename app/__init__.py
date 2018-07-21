from sanic import Sanic

from . import settings
from .routes import main


app = Sanic()
app.config.from_object(settings)

# routes
app.add_route(main, '/')

__all__ = ['app']
