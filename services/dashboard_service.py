from models.portfolio import Portfolio
from models.transaction import Transaction
from models.settings import Settings


class DashboardService:

    @staticmethod
    def get_dashboard_data():

        portfolio = Portfolio.query.all()

        stocks = [p for p in portfolio if p.asset_type == "Stock"]
        mutual_funds = [p for p in portfolio if p.asset_type == "Mutual Fund"]

        stock_current = sum(p.market_value for p in stocks)

        stock_investment = sum(
            p.quantity * p.average_price
        for p in stocks
        )

        stock_gain = stock_current - stock_investment

        mf_current = sum(p.market_value for p in mutual_funds)

        mf_investment = sum(
            p.quantity * p.average_price
            for p in mutual_funds
        )

        mf_gain = mf_current - mf_investment

        top_holdings = sorted(
            portfolio,
            key=lambda x: x.quantity * x.current_price,
            reverse=True
        )[:5]

        best_asset = None
        worst_asset = None

        if portfolio:

            portfolio_sorted = sorted(
                portfolio,
                key=lambda x: (
                    (x.current_price - x.average_price)
                    / x.average_price
                ) * 100,
                reverse=True
            )

            best_asset = portfolio_sorted[0]
            worst_asset = portfolio_sorted[-1]

        recent_transactions = (
            Transaction.query
            .order_by(Transaction.transaction_date.desc())
            .limit(5)
            .all()
        )

        holdings = len(portfolio)

        total_value = sum(
            p.quantity * p.current_price
            for p in portfolio
        )

        investment = sum(
            p.quantity * p.average_price
            for p in portfolio
        )

        gain = total_value - investment

        gain_percent = (
            gain / investment * 100
            if investment > 0 else 0
        )

        mf_value = sum(
            p.market_value
            for p in portfolio
            if p.asset_type == "Mutual Fund"
        )

        stock_value = sum(
            p.market_value
            for p in portfolio
            if p.asset_type == "Stock"
        )

        chart_labels = [
            "Mutual Funds",
            "Stocks"
        ]

        chart_values = [
            mf_value,
            stock_value
        ]

        growth_labels = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun"
        ]

        growth_values = [
            850000,
            910000,
            965000,
            1035000,
            1120000,
            total_value
        ]

        settings = Settings.query.first()

        last_sync = settings.last_sync if settings else None
        return {
            "portfolio": portfolio,
            "holdings": holdings,
            "total_value": round(total_value, 2),
            "investment": round(investment, 2),
            "gain": round(gain, 2),
            "gain_percent": round(gain_percent, 2),
            "mf_value": round(mf_value, 2),
            "stock_value": round(stock_value, 2),
            "chart_labels": chart_labels,
            "chart_values": chart_values,
            "growth_labels": growth_labels,
            "growth_values": growth_values,
            "top_holdings": top_holdings,
            "recent_transactions": recent_transactions,
            "best_asset": best_asset,
            "worst_asset": worst_asset,
            "last_sync": last_sync,
            "stock_current": stock_current,
            "stock_investment": stock_investment,
            "stock_gain": stock_gain,
            "stocks": stocks,
            "mutual_funds": mutual_funds,
            "mf_current": mf_current,
            "mf_investment": mf_investment,
            "mf_gain": mf_gain,
        }