> Historical Week 4 document. Current Phase 2 instructions and execution status are in the root README.

# Estructura de los datos

```text
dimensions/
├── locations/locations.json       Id → sucursal
├── revenue_centers/revenueCenters.json  Id → canal / centro de ingresos
├── items/items.json               Id → producto
└── employees/employees.json       Id → empleado (contenido privado)
facts/checks/brand=rmh/dt=YYYY-MM-DD/checks.json
└── Ticket
    ├── Id, LocationId, BusinessDate, RevenueCenterId
    ├── OpenTime, CloseTime, TableName, TrafficCount, LoyaltyId, ServiceCharge
    ├── Discounts[]
    │   └── Amount, DiscountId, DiscountName, EmployeeId, ManagerId
    ├── ItemsSold[]
    │   ├── ItemId, ItemName, ItemPLU, Quantity, GrossPrice, SoldPrice
    │   ├── EmployeeId, OrderTime, RevenueCenterId, PosSourceId
    │   ├── Sequence, ParentSequence, Seat
    │   ├── ItemMajorCatId, ItemMajorCatName, ItemSubCatId, ItemSubCatName
    │   └── Discounts[]
    │       └── Amount, DiscountId, DiscountName, EmployeeId, ManagerId
    ├── Payments[]
    │   ├── Amount, Gratuity, EmployeeId, PaymentCategoryId
    │   ├── PayCatName, PayCatNo, PosSourceId
    │   └── IsCashDebit, IsCreditCard, IsGiftCard, IsGiftCert,
    │       IsNonPOS, IsPettyCash
    ├── Tax[]
    │   └── Amount, TaxCategoryId, TaxCategoryName
    └── Voids[]
        └── Amount, Quantity, ItemId, ItemName, ItemPLU,
            EmployeeId, ManagerId, VoidCategoryId, VoidCategoryName
```

`source_file` es una columna añadida en la lectura. `business_date` es la conversión de BusinessDate a fecha. Los nombres de dimensiones se usan para contextualizar, sin publicar datos personales. `RevenueCenterId` se usa para agrupar canales; `PayCatName` identifica la categoría registrada del pago. No confundir ambos.
