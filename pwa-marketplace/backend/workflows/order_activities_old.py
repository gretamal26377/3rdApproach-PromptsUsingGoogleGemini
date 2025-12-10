from temporalio import activity
from temporalio.exceptions import ApplicationError
from pydantic import BaseModel
from ..app.shared.database import db
from ..app.shared.models import Orders, OrderStatuses
# from datetime import datetime
import logging

class UpdateOrderStatusResult(BaseModel):
    order_id: int
    new_status: str
    # updated_at: datetime
    success: bool = True

@activity.defn
# This function definition uses type hints (a standard feature in modern Python) to communicate expected input and output types.
# UpdateOrderStatusResult is a Pydantic model defined above to structure the output result
def update_order_status_in_db(order_id: int, new_status_code: str) -> UpdateOrderStatusResult:
    """
    Activity that updates an order's status in the DB using full Temporal best practices:
    - Business logic errors → ApplicationError(non_retryable=True)
    - DB/commit errors → regular exception (retryable)
    - Returns a clean object on success
    """

    try:
        # 1. Load Order
        order = Orders.query.get(order_id)
        if not order:
            logging.error(f"Order {order_id} not found")
            # Non-retryable business failure
            raise ApplicationError(
                f"Order {order_id} not found",
                type="ORDER_NOT_FOUND",
                non_retryable=True
            )

        # 2. Load Status
        new_status = OrderStatuses.query.filter_by(status_code=new_status_code).first()
        if not new_status:
            logging.error(f"Invalid status code: {new_status_code}")
            # Non-retryable business failure
            raise ApplicationError(
                f"Invalid status code '{new_status_code}'",
                type="INVALID_STATUS",
                non_retryable=True
            )

        # 3. Update Order
        order.order_status_id = new_status.status_id
        # order.updated_at = datetime.utcnow() ## Orders model has no this field currently
        db.session.commit()

        # 4. Return clean structured result
        return UpdateOrderStatusResult(
            order_id=order_id,
            new_status=new_status_code,
            # updated_at=order.updated_at,
        )

    except ApplicationError:
        # rollback put here just in case DB session is dirty, if it's clean and rollback is called, nothing happens
        db.session.rollback()
        raise

    except Exception as e:
        # DB/commit/connection errors → retryable failure
        db.session.rollback()
        logging.exception(
            f"DB failure updating Order {order_id} to Status {new_status_code}"
        )
        raise RuntimeError(
            f"DB failure Updating Order {order_id}"
        ) from e
    