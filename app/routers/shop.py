import sqlite3
import pathlib

from fastapi import APIRouter

router = APIRouter(tags=["shop"])

router.db_path = str(pathlib.Path(__file__).parent.parent) + "/northwind.db"


# router.db_path = "app/db/northwind.db"

@router.on_event("startup")
async def startup():
    router.db_connection = sqlite3.connect(router.db_path)
    router.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific


@router.on_event("shutdown")
async def shutdown():
    router.db_connection.close()


# Ex1
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
    # router.db_connection = sqlite3.connect(router.db_path)
    cursor = router.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    customers = cursor.execute(
        "SELECT CustomerID, CompanyName, Address, PostalCode, City, Country FROM Customers").fetchall()
    return {
        "customers":
            [{"id": col_name['CustomerID'], "name": col_name['CompanyName'], "full_address":
                f"{col_name['Address']} {col_name['PostalCode']} {col_name['City']} {col_name['Country']}"}
             for col_name in customers]
    }
