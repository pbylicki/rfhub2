from setuptools import setup

filename = 'rfhub2/version.py'
exec(open(filename).read())

setup(
    name='rfhub2',
    version=version,
    author='Pawel Bylicki, Maciej Wiczk',
    author_email='pawelkbylicki@gmail.com, maciejwiczk@gmail.com',
    url='https://github.com/pbylicki/rfhub2/',
    keywords='robotframework',
    license='Apache License 2.0',
    description='Webserver for robot framework and python assets documentation',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    zip_safe=True,
    include_package_data=True,
    install_requires=[
        'alembic>=1.2.0',
        'aiofiles>=0.4.0',
        'Click>=7.0',
        'fastapi>=0.46.0',
        'pydantic>=1.0',
        'robotframework>=3.0.0',
        'SQLAlchemy>=1.2.0',
        'requests>=2.10.0',
        'uvicorn>=0.7.1',
        'progress>=1.4'
    ],
    extras_require={
        "postgresql": ["psycopg2-binary>=2.7.4"]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Unix",
        "Framework :: Robot Framework",
        "Framework :: Robot Framework :: Tool",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Intended Audience :: Developers",
    ],
    packages=[
        'rfhub2',
        'rfhub2.alembic',
        'rfhub2.alembic.versions',
        'rfhub2.api',
        'rfhub2.api.endpoints',
        'rfhub2.api.middleware',
        'rfhub2.api.utils',
        'rfhub2.cli',
        'rfhub2.cli.keywords',
        'rfhub2.cli.statistics',
        'rfhub2.db',
        'rfhub2.db.model',
        'rfhub2.db.repository',
        'rfhub2.model',
        'rfhub2.ui',
        'rfhub2.utils',
    ],
    scripts=[],
    entry_points={
        'console_scripts': [
            "rfhub2 = rfhub2.__main__:main",
            "rfhub2-cli = rfhub2.cli.__main__:main",
        ]
    }
)
