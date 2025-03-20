from application import create_app

# Создаем экземпляр приложения через фабрику
app, celery = create_app()

if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
