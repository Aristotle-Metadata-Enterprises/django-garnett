from drf_yasg.generators import OpenAPISchemaGenerator


class LibrarySchemaGenerator(OpenAPISchemaGenerator):
    """
    This is required due to how the api urls are setup
    and should be removed in future
    """

    prefix = "/api"

    def get_endpoints(self, request):
        endpoints = super().get_endpoints(request)
        fixed_endpoints = {}
        for key in endpoints.keys():
            new_key = self.prefix + key
            fixed_endpoints[new_key] = endpoints[key]

        return fixed_endpoints
