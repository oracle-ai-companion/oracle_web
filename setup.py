from setuptools import setup, find_packages

setup(
    name='oracle_dashboard',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'Flask-Discord',
        'Flask-Login',
        'Flask-WTF',
        'SQLAlchemy',
        'Flask-Migrate',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'run-dashboard=app:main',
        ],
    },
)