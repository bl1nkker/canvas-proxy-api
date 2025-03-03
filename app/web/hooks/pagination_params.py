def pagination_params(
    page: int = 1, page_size: int = 10, order_by: str = "id", asc: str = True
):
    return {"page": page, "page_size": page_size, "order_by": order_by, "asc": asc}
