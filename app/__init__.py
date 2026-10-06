from sqlalchemy import text

from app.database import engine


def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price NUMERIC(10, 2) NOT NULL
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                product_id INTEGER REFERENCES products(id),
                quantity INTEGER NOT NULL,
                amount NUMERIC(10, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        user_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar_one()
        if user_count < 10000:
            users = [
                {"name": f"User {index}", "email": f"user{index}@example.com"}
                for index in range(1, 10001)
            ]
            conn.execute(
                text("INSERT INTO users (name, email) VALUES (:name, :email)"),
                users,
            )

        product_count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar_one()
        if product_count < 100:
            products = [
                {"name": f"Product {index}", "price": float(index * 12.5)}
                for index in range(1, 101)
            ]
            conn.execute(
                text("INSERT INTO products (name, price) VALUES (:name, :price)"),
                products,
            )

        order_count = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar_one()
        if order_count < 10000:
            user_ids = conn.execute(text("SELECT id FROM users ORDER BY id")).scalars().all()
            product_ids = conn.execute(text("SELECT id FROM products ORDER BY id")).scalars().all()
            product_prices = {
                product_id: price
                for product_id, price in conn.execute(
                    text("SELECT id, price FROM products ORDER BY id")
                )
            }

            orders = []
            for index in range(10000):
                user_id = user_ids[index % len(user_ids)]
                product_id = product_ids[(index * 7) % len(product_ids)]
                quantity = (index % 5) + 1
                amount = float(quantity * product_prices[product_id])
                orders.append(
                    {
                        "user_id": user_id,
                        "product_id": product_id,
                        "quantity": quantity,
                        "amount": amount,
                    }
                )

            conn.execute(
                text(
                    "INSERT INTO orders (user_id, product_id, quantity, amount) "
                    "VALUES (:user_id, :product_id, :quantity, :amount)"
                ),
                orders,
            )


if __name__ == "__main__":
    init_db()
    print("Database initialized with demo data.")