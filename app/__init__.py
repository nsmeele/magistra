from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import json
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../static')
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # Vite manifest helpers
    @app.context_processor
    def vite_helpers():
        def get_vite_asset(entry):
            manifest_path = os.path.join(app.static_folder, 'dist', '.vite', 'manifest.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                    if entry in manifest:
                        return f"/static/dist/{manifest[entry]['file']}"
            # Fallback for development
            return f"/static/dist/assets/{entry}"

        def get_vite_css(entry):
            manifest_path = os.path.join(app.static_folder, 'dist', '.vite', 'manifest.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                    if entry in manifest and 'css' in manifest[entry]:
                        return [f"/static/dist/{css}" for css in manifest[entry]['css']]
            return []

        return dict(vite_asset=get_vite_asset, vite_css=get_vite_css)

    from app import routes, models
    app.register_blueprint(routes.bp)

    return app