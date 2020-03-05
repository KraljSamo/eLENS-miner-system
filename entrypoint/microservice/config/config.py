# Configuration script
# Retrieves the hidden variables from the .env
# file and creates the configuration objects -
# one for each environment.

import os
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    DEBUG = False
    TESTING = False
    CORS = {
        'origins': os.getenv('CORS_ORIGINS').split(',') if os.getenv('CORS_ORIGINS') else None
    }

class ProductionConfig(Config):
    """Production configuration"""
    # TODO: add required secret configurations
    ENV='production'
    SECRET_KEY=os.getenv('PROD_SECRET_KEY')
    DB_USER = os.getenv('PROD_DATABASE_USER')
    DB_HOST = os.getenv('PROD_DATABASE_HOST')
    DB_PORT = os.getenv('PROD_DATABASE_PORT')
    DB_PASSWORD = os.getenv('PROD_DATABASE_PASSWORD')
    DB_NAME = os.getenv('PROD_DATABASE_NAME')
    SERVICE_ENRICHMENT_HOST = os.getenv('PROD_ENRICHMENT_HOST')
    SERVICE_ENRICHMENT_PORT = os.getenv('PROD_ENRICHMENT_PORT')

class DevelopmentConfig(Config):
    """Development configuration"""
    # TODO: add required secret configurations
    ENV='development'
    DEBUG = True
    SECRET_KEY=os.getenv('DEV_SECRET_KEY')
    DB_USER = os.getenv('DEV_DATABASE_USER')
    DB_HOST = os.getenv('DEV_DATABASE_HOST')
    DB_PORT = os.getenv('DEV_DATABASE_PORT')
    DB_PASSWORD = os.getenv('DEV_DATABASE_PASSWORD')
    DB_NAME = os.getenv('DEV_DATABASE_NAME')
    SERVICE_ENRICHMENT_HOST = os.getenv('DEV_ENRICHMENT_HOST')
    SERVICE_ENRICHMENT_PORT = os.getenv('DEV_ENRICHMENT_PORT')

class TestingConfig(Config):
    """Testing configuration"""
    # TODO: add required secret configurations
    ENV='testing'
    TESTING = True
    SECRET_KEY=os.getenv('TEST_SECRET_KEY')
