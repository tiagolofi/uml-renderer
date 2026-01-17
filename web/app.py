

from flask import Flask

class UmlAppRenderer():
    def __init__(self):
        pass

    def _create_app(self):
        app = Flask(__name__, static_folder='web/static', template_folder='web/templates')
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

        from web import bp
        app.register_blueprint(bp)

        return app
    
    def run(self, debug=True, port=5000):
        app = self._create_app()
        app.run(debug=debug, port=port)
