import json
import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__, static_folder="../static", template_folder="../templates")
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # Custom Jinja2 filter for safe percentage values
    @app.template_filter("safe_percent")
    def safe_percent_filter(value):
        """Ensure a value is a valid percentage between 0-100"""
        try:
            num = float(value)
            return max(0.0, min(100.0, num))
        except (ValueError, TypeError):
            return 0.0

    # Custom Jinja2 filter for entry type labels
    @app.template_filter("entry_type_label")
    def entry_type_label_filter(entry_type_value):
        """Convert entry_type waarde naar Nederlands label"""
        from app.constants import EntryType

        return EntryType.get_label(entry_type_value)

    # Game layer: mastery filters and a lazily computed player profile
    from app import game

    app.add_template_filter(game.mastery, "mastery")
    app.add_template_filter(game.mastery_label, "mastery_label")

    @app.context_processor
    def game_helpers():
        from flask import g

        def game_profile():
            if "game_profile" not in g:
                try:
                    g.game_profile = game.build_profile()
                except Exception as e:  # never break page rendering
                    print(f"Error building game profile: {e}")
                    g.game_profile = None
            return g.game_profile

        def smart_practice_ready(list_id=None):
            """Smart practice needs words that were practised at least twice."""
            from app.services import QuizService

            cache = g.setdefault("smart_practice_ready", {})
            if list_id not in cache:
                cache[list_id] = QuizService().has_difficult_entries(list_id=list_id)
            return cache[list_id]

        return dict(
            game_profile=game_profile,
            smart_practice_ready=smart_practice_ready,
            XP_CORRECT=game.XP_CORRECT,
        )

    # Vite manifest helpers
    @app.context_processor
    def vite_helpers():
        def get_vite_asset(entry):
            manifest_path = os.path.join(
                app.static_folder, "dist", ".vite", "manifest.json"
            )
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                    if entry in manifest:
                        return f"/static/dist/{manifest[entry]['file']}"
            # Fallback for development
            return f"/static/dist/assets/{entry}"

        def get_vite_css(entry):
            manifest_path = os.path.join(
                app.static_folder, "dist", ".vite", "manifest.json"
            )
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                    if entry in manifest and "css" in manifest[entry]:
                        return [f"/static/dist/{css}" for css in manifest[entry]["css"]]
            return []

        return dict(vite_asset=get_vite_asset, vite_css=get_vite_css)

    from app import models, routes

    app.register_blueprint(routes.bp)

    return app
