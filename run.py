from app_index.app import create_app
from app_index import config

app = create_app('app', config=config.DevelopmentConfig)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=5000)
