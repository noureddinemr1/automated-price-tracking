from typing import List, Optional
from sqlalchemy.orm import Session
from .base import BaseRepository
from ..database.models import Product, PriceHistory


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: Session):
        self.session = session

    def add(self, entity: Product) -> Product:
        """Add a new product"""
        self.session.add(entity)
        self.session.commit()
        return entity

    def get(self, id: str) -> Optional[Product]:
        """Get a product by URL (our ID)"""
        return self.session.query(Product).filter_by(url=id).first()

    def get_all(self) -> List[Product]:
        """Get all products"""
        return self.session.query(Product).all()

    def delete(self, id: str) -> None:
        """Delete a product and its price history"""
        product = self.get(id)
        if product:
            # Delete price history first
            self.session.query(PriceHistory).filter_by(product_url=id).delete()
            # Then delete the product
            self.session.delete(product)
            self.session.commit()

    def get_price_history(self, product_url: str) -> List[PriceHistory]:
        """Get price history for a product"""
        return (
            self.session.query(PriceHistory)
            .filter_by(product_url=product_url)
            .order_by(PriceHistory.timestamp.desc())
            .all()
        )

    def add_price_history(self, price_history: PriceHistory) -> PriceHistory:
        """Add a new price history entry"""
        self.session.add(price_history)
        self.session.commit()
        return price_history
