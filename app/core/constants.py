# app/core/constants.py

USER_TYPE_EMPLOYEE = "employee"
USER_TYPE_USER = "user"

ROUTE_PREFIX_USERS = "/users"
ROUTE_PREFIX_EMPLOYEES = "/employees"
ROUTE_PREFIX_COUNTRIES = "/countries"

ACCESS_RULES = {
    USER_TYPE_USER: [ROUTE_PREFIX_USERS],
    USER_TYPE_EMPLOYEE: [ROUTE_PREFIX_USERS, ROUTE_PREFIX_EMPLOYEES, ROUTE_PREFIX_COUNTRIES],
    # Add more user types and route prefixes as needed
}