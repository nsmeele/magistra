import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Get port from environment or default to 5001
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
