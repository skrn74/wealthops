from database.database import db
from models.portfolio import Portfolio
from models.transaction import Transaction


class PortfolioService:

    @staticmethod
    def get_all_assets():
        return Portfolio.query.all()

    @staticmethod
    def get_asset(asset_id):
        return Portfolio.query.get_or_404(asset_id)

    @staticmethod
    def create_asset(form):

        asset = Portfolio(
            asset_name=form["asset_name"],
            asset_type=form["asset_type"],
            quantity=float(form["quantity"]),
            average_price=float(form["average_price"]),
            current_price=float(form["current_price"])
        )

        db.session.add(asset)
        
        transaction = Transaction(
            asset_name=asset.asset_name,
            transaction_type="BUY",
            quantity=asset.quantity,
            price=asset.average_price
        )

        db.session.add(transaction)
        db.session.commit()

    @staticmethod
    def update_asset(asset_id, form):

        asset = Portfolio.query.get_or_404(asset_id)

        asset.asset_name = form["asset_name"]
        asset.asset_type = form["asset_type"]
        asset.quantity = float(form["quantity"])
        asset.average_price = float(form["average_price"])
        asset.current_price = float(form["current_price"])

        db.session.commit()

    @staticmethod
    def delete_asset(asset_id):

        asset = Portfolio.query.get_or_404(asset_id)

        db.session.delete(asset)
        db.session.commit()

    @staticmethod
    def sync_holdings(holdings):
        for holding in holdings:

            portfolio = Portfolio.query.filter_by(
                isin=holding["isin"]
            ).first()

            market_value = holding["quantity"] * holding["last_price"]

            if portfolio:

                portfolio.asset_name = holding["company_name"]
                portfolio.symbol = holding["trading_symbol"]
                portfolio.quantity = holding["quantity"]
                portfolio.average_price = holding["average_price"]
                portfolio.current_price = holding["last_price"]
                portfolio.market_value = market_value
                portfolio.pnl = holding["pnl"]
                portfolio.source = "Upstox"

            else:

                portfolio = Portfolio(

                    asset_name=holding["company_name"],

                    symbol=holding["trading_symbol"],

                    isin=holding["isin"],

                    asset_type="Stock",

                    quantity=holding["quantity"],

                    average_price=holding["average_price"],

                    current_price=holding["last_price"],

                    market_value=market_value,

                    pnl=holding["pnl"],

                    source="Upstox"

                )

                db.session.add(portfolio)

        db.session.commit()