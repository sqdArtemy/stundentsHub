from flask import request, url_for


class PaginationMixin:
    def get_paginated_response(self, query, items_schema, model_plural_name, count_field_name):
        page = request.args.get("page", default=1, type=int)
        page_size = request.args.get("page_size", default=10, type=int)
        paginated_items = query.paginate(page=page, per_page=page_size)

        items = paginated_items.items
        count = paginated_items.total

        links = {}
        if paginated_items.has_prev:
            links["prev"] = url_for(request.endpoint, page=paginated_items.prev_num, _external=True)
        if paginated_items.has_next:
            links["next"] = url_for(request.endpoint, page=paginated_items.next_num, _external=True)

        response = {
            model_plural_name: items_schema.dump(items),
            count_field_name: count,
            "links": links
        }

        return response
