

from flask import Flask

def create_app():
    app = Flask(__name__, static_folder='web/static', template_folder='web/templates')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    from web import bp
    app.register_blueprint(bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)