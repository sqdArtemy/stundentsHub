import json
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


class FilterMixin:
    def get_filtered_query(self, query, model, filters, filter_mappings={}):
        filters_dict = json.loads(filters)

        for key, value in filters_dict.items():
            if key in filter_mappings.keys():
                filter_nested_field, filter_field = filter_mappings[key]
                query = query.filter(filter_nested_field.has(filter_field == value))
            else:
                query = query.filter(getattr(model, key) == value)

        return query
