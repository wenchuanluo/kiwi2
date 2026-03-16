from flask import Flask, jsonify
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException
import logging
import sys
from logging.handlers import RotatingFileHandler
from app.db import db
from flask_caching import Cache

cache = Cache()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    
    db.init_app(app)
    cache.init_app(app, config={
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
    })
    from app.routes import portfolio_bp, security_bp, trade_bp, user_bp
    from app.service.portfolio_service import (
    UnsupportedPortfolioOperationError,
    PortfolioAuthorizationError,)
    from app.service.trade_service import InsufficientFundsError, TradeExecutionException
    from app.service.user_service import UnsupportedUserOperationError
    
    if app.debug or app.testing:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
    else:
        handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=10)
        handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(module)s:%(lineno)d]'
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(portfolio_bp, url_prefix="/portfolios")
    app.register_blueprint(security_bp, url_prefix="/securities")
    app.register_blueprint(trade_bp, url_prefix="/trade")

    
    @app.errorhandler(UnsupportedUserOperationError)
    def handle_user_operation_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Bad Request",
            "detail": str(error),
        }), 400

    
    @app.errorhandler(UnsupportedPortfolioOperationError)
    def handle_portfolio_operation_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Bad Request",
            "detail": str(error),
        }), 400

    
    @app.errorhandler(TradeExecutionException)
    def handle_trade_execution_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Bad Request",
            "detail": str(error),
        }), 400

    
    @app.errorhandler(InsufficientFundsError)
    def handle_insufficient_funds_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Bad Request",
            "detail": str(error),
        }), 400

    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Validation Error",
            "detail": error.errors(),
        }), 422

    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        db.session.rollback()
        return jsonify({
            "error": error.name,
            "detail": error.description,
        }), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Internal Server Error",
            "detail": str(error),
        }), 500
        
    @app.errorhandler(PortfolioAuthorizationError)
    def handle_portfolio_authorization_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Forbidden",
            "detail": str(error),
        }), 403

    return app
