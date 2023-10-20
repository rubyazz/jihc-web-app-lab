from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from diller.models import Employee

class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        user = request.user  # Get the user associated with the request
        if user is None:
            return None

        try:
            employee = Employee.objects.get(user=user)
        except Employee.DoesNotExist:
            raise AuthenticationFailed('No employee associated with this user.')

        # Add the 'employee' attribute to the request
        request.employee = employee

        return (user, None)
