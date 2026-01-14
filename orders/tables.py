from piccolo.table import Table
from piccolo.columns import Integer, Timestamp, ForeignKey, Varchar, Text

from inventory.tables import Inventory

from enum import Enum
class ReservationStatus(str, Enum):
    Reserved = 'reserved'
    Confirmed = 'confirmed'
    Cancelled = 'cancelled'
    Completed = 'completed'

class OrderStatus(str, Enum):
    Draft = 'draft'
    Reserved = 'reserved'
    Confirmed = 'confirmed'
    Cancelled = 'cancelled'
    Completed = 'completed'

class ExtensionStatus(str, Enum):
    Requested = 'requested'
    Approved = 'approved'
    Rejected = 'rejected'


class TimeSlot(Table, tablename='time_slots'):
    inventory = ForeignKey(Inventory)
    start_at = Timestamp()
    end_at = Timestamp()
    quantity = Integer()
    status = Varchar(choices=ReservationStatus)
    created_at = Timestamp()


class Order(Table, tablename='orders'):
    user_id = Integer()
    status = Varchar(choices=OrderStatus)
    created_at = Timestamp()
    confirmed_at = Timestamp(null=True)
    cancelled_at = Timestamp(null=True)


class OrderItem(Table, tablename='order_items'):
    order_id = ForeignKey(Order)
    inventory = ForeignKey(Inventory)
    quantity = Integer()
    start_at = Timestamp()
    end_at = Timestamp()


class Allocation(Table, tablename='allocations'):
    order_item = ForeignKey(OrderItem)
    time_slot = ForeignKey(TimeSlot)


class RentalExtension(Table, tablename='rental_extensions'):
    order_item = ForeignKey(OrderItem)
    old_end_at = Timestamp()
    new_end_at = Timestamp()
    status = Varchar(choices=ExtensionStatus)
    created_at = Timestamp()


class RentalReturn(Table, tablename='rental_returns'):
    order_item = ForeignKey(OrderItem)
    returned_at = Timestamp()
    condition_notes = Text(null=True)


class ReservationExpiry(Table, tablename='reservation_expiries'):
    order_id = ForeignKey(Order)
    expires_at = Timestamp()