import plotly.express as px


class PriceChart:
    def create(self, price_history, cabin_type=None):
        """
        Create a price history chart with the lowest price highlighted.

        Args:
            price_history (pd.DataFrame): Price history data.
            cabin_type (str, optional): Type of cabin (e.g., Economy, Business). Defaults to None.
        """
        # Find the lowest price
        lowest_price = price_history["price"].min()
        lowest_timestamp = price_history.loc[price_history["price"].idxmin(), "timestamp"]

        # Create the line chart
        fig = px.line(price_history, x="timestamp", y="price", title=None)
        fig.update_layout(
            xaxis_title=None,
            yaxis_title="Price ($)",
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            height=300,
        )
        fig.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickangle=45)
        fig.update_yaxes(tickprefix="$", tickformat=".2f")

        # Highlight the lowest price
        fig.add_annotation(
            x=lowest_timestamp,
            y=lowest_price,
            text=f"Lowest: ${lowest_price:.2f}",
            showarrow=True,
            arrowhead=1,
            bgcolor="red",
            font=dict(color="white"),
        )

        # Add cabin type to the title (if available)
        if cabin_type:
            fig.update_layout(title=f"Cabin Type: {cabin_type}")

        return fig