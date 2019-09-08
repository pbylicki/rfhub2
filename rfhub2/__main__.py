import uvicorn

from rfhub2 import config

# for now we import here this instance of app to have db initialized and populated for development purposes
# later we should just create app instance here
from rfhub2.main import app


def main():
    uvicorn.run(
        app,
        host=config.APP_INTERFACE,
        port=config.APP_PORT,
        log_level=config.APP_LOG_LEVEL,
    )


if __name__ == "__main__":
    main()
