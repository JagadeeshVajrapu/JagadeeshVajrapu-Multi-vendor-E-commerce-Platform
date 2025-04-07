from app import app

if __name__ == '__main__':
    print("Starting Flask application...")
    print(f"Static folder: {app.static_folder}")
    print(f"Template folder: {app.template_folder}")
    app.run(debug=True, port=5001)





    