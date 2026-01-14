from products.tables import Warehouse, Address
from datetime import datetime 


async def seed_warehouses():
    addresses = [
        Address(
            line1="Plot 21, MIDC Industrial Area",
            city="Pune",
            state="Maharashtra",
            postal_code="411019",
            latitude=18.6510,
            longitute=73.7560,
        ),
        Address(
            line1="Sector 5, Salt Lake",
            line2="Near Tech Park",
            city="Kolkata",
            state="West Bengal",
            postal_code="700091",
            latitude=22.5867,
            longitute=88.4171,
        ),
        Address(
            line1="Electronic City Phase 1",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560100",
            latitude=12.8399,
            longitute=77.6770,
        ),
        Address(
            line1="Masjid Banda, Kondapur",
            city="Hyderabad",
            state="Telangana",
            postal_code="543109",
            latitude=17.6785,
            longitute=56.8973,
        ),
        Address(
            line1="Madison Square Garden, KPHB",
            city="Hyderabad",
            state="Andhra Pradesh",
            postal_code="545601",
            latitude=87.5643,
            longitute=12.8643,
        )
    ]

    # Save addresses
    await Address.insert(*addresses)

    # Fetch saved addresses (to get IDs)
    saved_addresses = await Address.objects().run()

    warehouses = [
        Warehouse(
            name="Makali Warehouse",
            address=saved_addresses[0]
        ),
        Warehouse(
            name="Mumbai warehouse",
            address=saved_addresses[1]
        ),
        Warehouse(
            name="Jalahalli warehouse",
            address=saved_addresses[2]
        ),
        Warehouse(
            name="Sahakarnagar warehouse",
            address = saved_addresses[3]
        ),
        Warehouse(
            name="Rajajinagar warehouse",
            address = saved_addresses[4]
        )
    ]

    await Warehouse.insert(*warehouses)
