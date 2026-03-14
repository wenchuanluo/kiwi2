from flask import Flask, jsonify
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from app.db import db
from app.routes import portfolio_bp, security_bp, trade_bp, user_bp
from app.service.portfolio_service import UnsupportedPortfolioOperationError
from app.service.trade_service import InsufficientFundsError, TradeExecutionException
from app.service.user_service import UnsupportedUserOperationError


def create_app(config):
    # CHANGED: removed outer try/except from app factory
    app = Flask(__name__)
    app.config.from_object(config)

    # register extensions
    db.init_app(app)

    # register blueprints
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(portfolio_bp, url_prefix="/portfolios")
    app.register_blueprint(security_bp, url_prefix="/securities")
    app.register_blueprint(trade_bp, url_prefix="/trade")

    # CHANGED: added centralized error handler for user-related business errors
    @app.errorhandler(UnsupportedUserOperationError)
    def handle_user_operation_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Bad Request",
            "detail": str(error),
        }), 400

    # CHANGED: added centralized error handler for portfolio-related business errors
    @app.errorhandler(UnsupportedPortfolioOperationError)
    def handle_portfolio_operation_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Bad Request",
            "detail": str(error),
        }), 400

    # CHANGED: added centralized error handler for trade-related business errors
    @app.errorhandler(TradeExecutionException)
    def handle_trade_execution_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Bad Request",
            "detail": str(error),
        }), 400

    # CHANGED: added centralized error handler for insufficient funds
    @app.errorhandler(InsufficientFundsError)
    def handle_insufficient_funds_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Bad Request",
            "detail": str(error),
        }), 400

    # CHANGED: added centralized error handler for Pydantic validation errors
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Validation Error",
            "detail": error.errors(),
        }), 422

    # CHANGED: added fallback global error handler for unexpected exceptions
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

    return app
