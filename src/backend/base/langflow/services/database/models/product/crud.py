from typing import TYPE_CHECKING
import logging
from langflow.api.utils import DbSession
from langflow.schema.product import ProductCreate, ProductRead
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from langflow.services.database.models.product.model import ProductTable, ProductType
from sqlalchemy.orm import selectinload

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from sqlmodel.sql.expression import SelectOfScalar

async def get_products(session: AsyncSession) -> list[ProductRead]:
    """Get all products with their associated prices."""
    stmt = (
        select(ProductTable)
        .options(selectinload(ProductTable.prices))  # This eagerly loads the prices
    )
    
    products = (await session.exec(stmt)).all()
    
    return [
        ProductRead.model_validate({
            **product.__dict__,
            'prices': [price.__dict__ for price in product.prices],
            'stripe_metadata': {} if not product.stripe_metadata else dict(product.stripe_metadata)
        })
        for product in products
    ]

async def get_product(session: AsyncSession, product_id: str) -> ProductTable | None:
    """Get a product by ID."""
    logger.debug(f"Fetching product with ID: {product_id}")
    product = await session.get(ProductTable, product_id)
    logger.debug(f"Found product: {product}")
    return product

async def get_product_by_type(session: AsyncSession, product_type: ProductType) -> ProductTable | None:
    """Get a product by type."""
    logger.debug(f"Fetching product with type: {product_type}")
    query = select(ProductTable).where(ProductTable.type == product_type)
    product = (await session.exec(query)).first()
    logger.debug(f"Found product: {product}")
    return product

async def create_product(
    session: DbSession, 
    product: ProductCreate
) -> ProductTable:
    """Create a new product."""
    logger.debug("=== Starting Product Creation ===")
    logger.debug(f"Session type: {type(session)}")
    logger.debug(f"Session details: {session}")
    logger.debug("Input parameters:")
    logger.debug(f"- ID: {product.id}")

    try:
        # all args
        print(f"all args: {locals()}")

        db_product = ProductTable(**product.model_dump())
        logger.debug("Adding product to session...")
        session.add(db_product)
        
        logger.debug("Committing session...")
        await session.commit()
        
        logger.debug("Refreshing product...")
        await session.refresh(db_product)
        
        logger.debug(f"Product successfully created with ID: {db_product.id}")
        return db_product   
        
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}", exc_info=True)
        raise

async def update_product(
    session: AsyncSession,
    product_id: str,
    **update_data
) -> ProductTable | None:
    """Update a product."""
    logger.debug("=== Starting Product Update ===")
    logger.debug(f"Product ID: {product_id}")
    logger.debug(f"Update data: {update_data}")
    logger.debug(f"Session: {session}")

    try:
        product = await session.get(ProductTable, product_id)
        if product is None:
            logger.warning(f"No product found with ID: {product_id}")
            return None
        
        logger.debug(f"Found existing product: {product}")
        
        for key, value in update_data.items():
            logger.debug(f"Updating {key} to {value}")
            setattr(product, key, value)
        
        session.add(product)
        logger.debug("Committing changes...")
        await session.commit()
        await session.refresh(product)
        
        logger.debug(f"Product updated successfully: {product}")
        return product
        
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}", exc_info=True)
        raise

async def delete_product(session: AsyncSession, product_id: str) -> bool:
    """Delete a product."""
    logger.debug(f"Attempting to delete product with ID: {product_id}")
    
    try:
        product = await session.get(ProductTable, product_id)
        if product is None:
            logger.warning(f"No product found with ID: {product_id}")
            return False
        
        logger.debug(f"Found product to delete: {product}")
        await session.delete(product)
        logger.debug("Committing deletion...")
        await session.commit()
        
        logger.debug("Product deleted successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}", exc_info=True)
        raise

async def get_active_products(session: AsyncSession) -> list[ProductTable]:
    """Get all active products."""
    query = select(ProductTable).where(ProductTable.is_active == True)  # noqa: E712
    products = (await session.exec(query)).all()
    return products 