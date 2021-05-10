import sqlite3
import pathlib
from typing import Optional

from fastapi import APIRouter, HTTPException, status

router = APIRouter(tags=["shop"])
# router.db_path = "app/db/northwind.db"
router.db_path = str(pathlib.Path(__file__).parent.parent) + "/northwind.db"


@router.on_event("startup")
async def startup():
    router.db_connection = sqlite3.connect(router.db_path)
    router.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific


@router.on_event("shutdown")
async def shutdown():
    router.db_connection.close()


# Ex1 - selecting specific columns from "Categories" and "Customers" tables in db.
@router.get("/categories")
async def categories_view():
    cursor = router.db_connection.cursor()
    cursor.row_factory = sqlite3.Row  # Changes Query response from list of lists to list of dicts
    categories = cursor.execute("SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryId").fetchall()
    return {
        "categories":
            [{"id": col_name['CategoryID'], "name": col_name['CategoryName']} for col_name in categories]
    }


@router.get("/customers")
async def customers_view():
    cursor = router.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    customers = cursor.execute(
        "SELECT CustomerID id, COALESCE(CompanyName, '') name, "
        "COALESCE(Address , '') || ' ' || COALESCE(PostalCode, '') || ' ' || "
        "COALESCE(City , '') || ' ' || COALESCE(Country , '') full_address "
        "FROM Customers").fetchall()
    return {
        "customers": customers
    }


# Ex2 - Selecting product by id from "Products" table in db.
@router.get("/products/{product_id}")
async def product_id_view(product_id: int):
    cursor = router.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    product = cursor.execute("SELECT ProductID id, ProductName name FROM Products WHERE id = ?",
                             (product_id,)).fetchone()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return product


# Ex3 - Select employees from "Employees" table in db using parametric ORDER BY, LIMIT and OFFSET options.
@router.get("/employees")
async def employees_view(limit: Optional[int] = -1, offset: Optional[int] = 0, order: Optional[str] = None):
    cursor = router.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    if order not in ["first_name", "last_name", "city", None]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    if order is None:
        order = "id"

    sqlite3.paramstyle = "named"
    employees = cursor.execute("SELECT EmployeeID id, LastName last_name, FirstName first_name, "
                               f"City city FROM Employees ORDER BY {order} LIMIT :limit OFFSET :offset",
                               {"limit": limit, "offset": offset}).fetchall()
    return {"employees": employees}


# Ex4 - Select data from 3 tables in db using JOIN.
@router.get("/products_extended")
async def products_extended_view():
    cursor = router.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    products_extended = cursor.execute("SELECT Products.ProductID id, Products.ProductName name, "
                                       "Categories.CategoryName category, "
                                       "Suppliers.CompanyName supplier FROM Products "
                                       "JOIN Categories ON Products.CategoryID = Categories.CategoryID "
                                       "JOIN Suppliers ON Products.SupplierID = Suppliers.SupplierID").fetchall()
    return {"products_extended": products_extended}


# Ex5
@router.get("/products/{product_id}/order")
async def product_orders_view(product_id: int):
    cursor = router.db_connection.cursor()
    # Check if product exists before making Query about orders.
    product_exists = cursor.execute("SELECT EXISTS(SELECT 1 FROM Products WHERE ProductID = ?)",
                                    (product_id,)).fetchone()
    if not product_exists[0]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    cursor.row_factory = sqlite3.Row
    query = """
               SELECT 
                    od.OrderID AS id,
                    c.CompanyName AS customer,
                    od.Quantity AS quantity,
                    ROUND((od.UnitPrice * od.Quantity) - (od.Discount * (od.UnitPrice * od.Quantity)),2) AS total_price
                FROM 
                    'Order Details' od
                        JOIN Orders o ON od.OrderID = o.OrderID
                            JOIN Customers c ON o.CustomerID = c.CustomerID
                WHERE ProductID = ?;
               """
    orders = cursor.execute(query, (product_id,)).fetchall()
    return {"orders": orders}
