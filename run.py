from app import create_app
from config import Config

app = create_app()

if __name__ == '__main__':
    print(f"\n{'=' * 55}")
    print(f"  Lab Inventory Management Tool")
    print(f"  Running on http://localhost:{Config.PORT}")
    print(f"  Admin NT ID: {Config.ADMIN_NT_ID}")
    print(f"{'=' * 55}\n")
    app.run(host=Config.HOST, port=Config.PORT, debug=True)
