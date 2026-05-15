from flask import Blueprint, jsonify, request
from flask import g
import app.service.portfolio_service as portfolio_service
from app.service.portfolio_service import ensure_can_manage_portfolio
from app.auth import require_auth
from app.db import db
from app.routes.domain.trade_schema import BuyTradeRequest, SellTradeRequest
from app.service import trade_service

trade_bp = Blueprint("trade", __name__)


@trade_bp.route("/buy", methods=["POST"])
@require_auth
def execute_purchase_order():
    data = BuyTradeRequest(**request.get_json())

    portfolio = portfolio_service.get_portfolio_by_id(data.portfolio_id)

    if portfolio is None:
        return jsonify({"error": f"Portfolio {data.portfolio_id} not found"}), 404

    ensure_can_manage_portfolio(portfolio, g.current_user)

    try:
        trade_service.execute_purchase_order(
            portfolio_id=data.portfolio_id,
            ticker=data.ticker,
            quantity=data.quantity,
        )

        db.session.commit()

        return jsonify({"message": "Purchase order executed successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Bad Request",
            "detail": str(e),
        }), 400


@trade_bp.route("/sell", methods=["POST"])
@require_auth
def liquidate_investment():
    data = SellTradeRequest(**request.get_json())

    portfolio = portfolio_service.get_portfolio_by_id(data.portfolio_id)

    if portfolio is None:
        return jsonify({"error": f"Portfolio {data.portfolio_id} not found"}), 404

    ensure_can_manage_portfolio(portfolio, g.current_user)

    try:
        trade_service.liquidate_investment(
            portfolio_id=data.portfolio_id,
            ticker=data.ticker,
            quantity=data.quantity,
        )

        db.session.commit()

        return jsonify({"message": "Investment liquidated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Bad Request",
            "detail": str(e),
        }), 400