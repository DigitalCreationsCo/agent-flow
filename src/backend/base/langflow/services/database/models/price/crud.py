from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from langflow.schema.product import PriceCreate, PriceRead, PriceUpdate
from langflow.services.database.models.price.model import PriceTable


async def get_prices(session: AsyncSession, active: bool | None = None) -> list[PriceRead]:
    """Get all prices."""
    stmt = select(PriceTable)
    if active is not None:
        stmt = stmt.where(PriceTable.is_active == active)
    result = await session.exec(stmt)
    prices = result.all()

    # Convert each price to a dictionary and ensure metadata is a dict
    return [
        PriceRead.model_validate(
            {**price.__dict__, "stripe_metadata": {} if price.stripe_metadata is None else dict(price.stripe_metadata)}
        )
        for price in prices
    ]


async def get_price(session: AsyncSession, price_id: str) -> PriceTable | None:
    """Get a price by ID."""
    return await session.get(PriceTable, price_id)


async def create_price(session: AsyncSession, price: PriceCreate) -> PriceTable:
    """Create a new price."""
    db_price = PriceTable(**price.model_dump())
    session.add(db_price)
    await session.commit()
    await session.refresh(db_price)
    print(f"Created price: {db_price.id}")
    return db_price


async def update_price(session: AsyncSession, price_id: str, price_update: PriceUpdate) -> PriceTable | None:
    """Update a price."""
    db_price = await session.get(PriceTable, price_id)
    if not db_price:
        return None

    price_data = price_update.model_dump(exclude_unset=True)
    for key, value in price_data.items():
        setattr(db_price, key, value)

    session.add(db_price)
    await session.commit()
    await session.refresh(db_price)
    print(f"Updated price: {db_price.id}")
    return db_price


async def delete_price(session: AsyncSession, price_id: str) -> bool:
    """Delete a price."""
    price = await session.get(PriceTable, price_id)
    if not price:
        return False

    await session.delete(price)
    await session.commit()
    print(f"Deleted price: {price_id}")
    return True


async def get_product_prices(session: AsyncSession, product_id: str, active: bool | None = None) -> list[PriceTable]:
    """Get all prices for a specific product."""
    query = select(PriceTable).where(PriceTable.product_id == product_id)
    if active is not None:
        query = query.where(PriceTable.is_active == active)
    prices = (await session.exec(query)).all()
    return prices
