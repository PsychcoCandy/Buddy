from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Shop(db.Model):
    __tablename__ = "shops"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subdomain = db.Column(db.String(50), nullable=False, unique=True)
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False
    )


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(
        db.Integer,
        db.ForeignKey("shops.id"),
        nullable=False
    )
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    image = db.Column(db.String(255))
    created_at = db.Column(
        db.DateTime,
        nullable=False
    )

    @property
    def price_per_kg(self):
        return float(self.price)


def get_products_by_shop(shop_id):

    return Product.query.filter_by(
        shop_id=shop_id,
        active=True
    ).all()


def get_shop_by_subdomain(subdomain):

    shop = Shop.query.filter_by(
        subdomain=subdomain,
        active=True
    ).first()

    if shop is None:
        return None

    return {
        "shop_id": shop.id,
        "shop_name": shop.name,
        "subdomain": shop.subdomain,
        "phone": shop.phone,
        "address": shop.address,
        "active": shop.active,
        "created_at": shop.created_at
    }