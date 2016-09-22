from featuretrak.views import app
from featuretrak import config

if __name__ == "__main__":
    app.run(debug=config.DEBUG)
