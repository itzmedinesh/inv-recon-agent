from app import create_app

service = create_app()

if __name__ == '__main__':
    service.run(debug=True, host="0.0.0.0", port=5000)