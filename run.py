import sys
from app import create_app
from config import Config

app = create_app()

if __name__ == '__main__':
    print(f"\n{'=' * 55}")
    print(f"  Lab Inventory Management Tool")
    print(f"  Running on http://localhost:{Config.PORT}")
    print(f"  Admin NT ID: {Config.ADMIN_NT_ID}")
    print(f"{'=' * 55}\n")

    if hasattr(sys, '_MEIPASS'):
        # Running as compiled exe — use waitress (production WSGI, Windows-native)
        from waitress import serve
        serve(app, host=Config.HOST, port=Config.PORT, threads=4)
    else:
        app.run(host=Config.HOST, port=Config.PORT, debug=True)
