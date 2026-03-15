from flask import Blueprint, jsonify, request, g
from app.auth import require_auth
from app.service.portfolio_service import (
    ensure_can_view_portfolio,
    ensure_can_manage_portfolio,
    ensure_is_portfolio_owner,
)

import app.service.portfolio_service as portfolio_service
import app.service.transaction_service as transaction_service
import app.service.user_service as user_service
from app.db import db
from app.routes.domain.portfolio_schema import CreatePortfolioRequest

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/', methods=['GET'])
@require_auth
def get_all_portfolios():
    portfolios = portfolio_service.get_all_portfolios()
    return jsonify([portfolio.__to_dict__() for portfolio in portfolios]), 200


@portfolio_bp.route('/<int:portfolio_id>', methods=['GET'])
@require_auth
def get_portfolio(portfolio_id):
    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)

    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404

    ensure_can_view_portfolio(portfolio, g.current_user)

    return jsonify(portfolio.__to_dict__()), 200


@portfolio_bp.route('/user/<username>', methods=['GET'])
@require_auth
def get_portfolios_by_user(username):
    user = user_service.get_user_by_username(username)
    if user is None:
        return jsonify({'error': f'User {username} not found'}), 404
    portfolios = portfolio_service.get_portfolios_by_user(user)
    return jsonify([portfolio.__to_dict__() for portfolio in portfolios]), 200


@portfolio_bp.route('/', methods=['POST'])
@require_auth
def create_portfolio():
    data = CreatePortfolioRequest(**request.get_json())

    user = user_service.get_user_by_username(data.username)
    if user is None:
        return jsonify({"error": f"User {data.username} not found"}), 404

    portfolio_id = portfolio_service.create_portfolio(
        name=data.name,
        description=data.description,
        user=user,
    )
    db.session.commit()
    return jsonify(
        {"message": "Portfolio created successfully", "portfolio_id": portfolio_id}
    ), 201


@portfolio_bp.route('/<int:portfolio_id>', methods=['DELETE'])
@require_auth
def delete_portfolio(portfolio_id):
    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)

    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404

    ensure_is_portfolio_owner(portfolio, g.current_user)

    portfolio_service.delete_portfolio(portfolio_id)
    db.session.commit()

    return jsonify({'message': 'Portfolio deleted successfully'}), 200


@portfolio_bp.route('/<int:portfolio_id>/transactions', methods=['GET'])
@require_auth
def get_portfolio_transactions(portfolio_id):
    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)

    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404

    ensure_can_view_portfolio(portfolio, g.current_user)

    transactions = transaction_service.get_transactions_by_portfolio_id(portfolio_id)
    return jsonify([transaction.__to_dict__() for transaction in transactions]), 200

@portfolio_bp.route('/<int:portfolio_id>/access', methods=['POST'])
@require_auth
def grant_portfolio_access(portfolio_id):
    data = request.get_json()

    username = data.get("username")
    role = data.get("role")

    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)

    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404

    ensure_is_portfolio_owner(portfolio, g.current_user)

    portfolio_service.grant_portfolio_access(
        portfolio_id=portfolio_id,
        username=username,
        role=role,
    )

    db.session.commit()

    return jsonify({"message": "Access granted successfully"}), 201

@portfolio_bp.route('/<int:portfolio_id>/access/<username>', methods=['DELETE'])
@require_auth
def revoke_portfolio_access(portfolio_id, username):

    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)

    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404

    ensure_is_portfolio_owner(portfolio, g.current_user)

    portfolio_service.revoke_portfolio_access(portfolio_id, username)

    db.session.commit()

    return jsonify({"message": "Access revoked successfully"}), 200