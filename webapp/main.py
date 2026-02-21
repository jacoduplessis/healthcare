"""Entry point for the IES 2022/23 Data Explorer web app."""
from app import app

if __name__ == "__main__":
    app.run(debug=True, port=5001)
