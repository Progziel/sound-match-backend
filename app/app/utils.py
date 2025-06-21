# In your settings.py or utils.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    NotAcceptable,
    UnsupportedMediaType,
    Throttled,
    ParseError
)
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """Custom exception handler for consistent error responses across all exception types."""
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Get request info for logging
    request = context.get('request')
    view = context.get('view')

    if response is not None:
        # Handle different types of exceptions
        if isinstance(exc, ValidationError):
            # Handle validation errors (400)
            if isinstance(response.data, dict):
                # Get the first error for main error message
                first_field = next(iter(response.data))
                first_error = response.data[first_field][0] if isinstance(response.data[first_field], list) else response.data[first_field]

                custom_response_data = {
                    'success': False,
                    'error': f'{first_field}: {str(first_error)}',
                    'error_code': 'VALIDATION_ERROR',
                    'field': first_field,
                    'details': response.data,
                    'status_code': response.status_code
                }
            else:
                # Handle non-field errors
                custom_response_data = {
                    'success': False,
                    'error': str(response.data[0]) if isinstance(response.data, list) else str(response.data),
                    'error_code': 'VALIDATION_ERROR',
                    'details': response.data,
                    'status_code': response.status_code
                }

        elif isinstance(exc, AuthenticationFailed):
            # Handle authentication errors (401)
            custom_response_data = {
                'success': False,
                'error': 'Authentication failed. Please provide valid credentials.',
                'error_code': 'AUTHENTICATION_FAILED',
                'details': str(exc),
                'status_code': response.status_code
            }

        elif isinstance(exc, PermissionDenied):
            # Handle permission errors (403)
            custom_response_data = {
                'success': False,
                'error': 'You do not have permission to perform this action.',
                'error_code': 'PERMISSION_DENIED',
                'details': str(exc),
                'status_code': response.status_code
            }

        elif isinstance(exc, NotFound):
            # Handle not found errors (404)
            custom_response_data = {
                'success': False,
                'error': 'The requested resource was not found.',
                'error_code': 'NOT_FOUND',
                'details': str(exc),
                'status_code': response.status_code
            }

        elif isinstance(exc, MethodNotAllowed):
            # Handle method not allowed errors (405)
            custom_response_data = {
                'success': False,
                'error': f'Method "{request.method}" not allowed for this endpoint.',
                'error_code': 'METHOD_NOT_ALLOWED',
                'allowed_methods': response.data.get('detail', ''),
                'status_code': response.status_code
            }

        elif isinstance(exc, NotAcceptable):
            # Handle not acceptable errors (406)
            custom_response_data = {
                'success': False,
                'error': 'Not acceptable. The server cannot produce a response matching the list of acceptable values.',
                'error_code': 'NOT_ACCEPTABLE',
                'details': str(exc),
                'status_code': response.status_code
            }

        elif isinstance(exc, UnsupportedMediaType):
            # Handle unsupported media type errors (415)
            custom_response_data = {
                'success': False,
                'error': 'Unsupported media type in request.',
                'error_code': 'UNSUPPORTED_MEDIA_TYPE',
                'details': str(exc),
                'status_code': response.status_code
            }

        elif isinstance(exc, Throttled):
            # Handle throttled errors (429)
            custom_response_data = {
                'success': False,
                'error': 'Rate limit exceeded. Please try again later.',
                'error_code': 'THROTTLED',
                'retry_after': getattr(exc, 'wait', None),
                'details': str(exc),
                'status_code': response.status_code
            }

        elif isinstance(exc, ParseError):
            # Handle parse errors (400)
            custom_response_data = {
                'success': False,
                'error': 'Malformed request data.',
                'error_code': 'PARSE_ERROR',
                'details': str(exc),
                'status_code': response.status_code
            }

        else:
            # Handle any other DRF exceptions
            custom_response_data = {
                'success': False,
                'error': str(response.data.get('detail', 'An error occurred.')),
                'error_code': 'API_ERROR',
                'details': response.data,
                'status_code': response.status_code
            }

        response.data = custom_response_data

    else:
        # Handle exceptions not caught by DRF (like Django's built-in exceptions)
        if isinstance(exc, ObjectDoesNotExist):
            # Handle Django's ObjectDoesNotExist (404)
            custom_response_data = {
                'success': False,
                'error': 'The requested resource does not exist.',
                'error_code': 'OBJECT_NOT_FOUND',
                'details': str(exc),
                'status_code': 404
            }
            response = Response(custom_response_data, status=status.HTTP_404_NOT_FOUND)

        elif isinstance(exc, Http404):
            # Handle Django's Http404 (404)
            custom_response_data = {
                'success': False,
                'error': 'Page not found.',
                'error_code': 'PAGE_NOT_FOUND',
                'details': str(exc),
                'status_code': 404
            }
            response = Response(custom_response_data, status=status.HTTP_404_NOT_FOUND)

        elif isinstance(exc, PermissionError):
            # Handle Python's PermissionError (403)
            custom_response_data = {
                'success': False,
                'error': 'Permission denied.',
                'error_code': 'PERMISSION_ERROR',
                'details': str(exc),
                'status_code': 403
            }
            response = Response(custom_response_data, status=status.HTTP_403_FORBIDDEN)

        elif isinstance(exc, ValueError):
            # Handle ValueError (400)
            custom_response_data = {
                'success': False,
                'error': 'Invalid value provided.',
                'error_code': 'VALUE_ERROR',
                'details': str(exc),
                'status_code': 400
            }
            response = Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)

        elif isinstance(exc, KeyError):
            # Handle KeyError (400)
            custom_response_data = {
                'success': False,
                'error': 'Required field is missing.',
                'error_code': 'KEY_ERROR',
                'details': f'Missing key: {str(exc)}',
                'status_code': 400
            }
            response = Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)

        elif isinstance(exc, TypeError):
            # Handle TypeError (400)
            custom_response_data = {
                'success': False,
                'error': 'Invalid data type provided.',
                'error_code': 'TYPE_ERROR',
                'details': str(exc),
                'status_code': 400
            }
            response = Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)

        else:
            # Handle any other unexpected exceptions (500)
            logger.error(f"Unhandled exception: {exc}", exc_info=True)
            custom_response_data = {
                'success': False,
                'error': 'An internal server error occurred.',
                'error_code': 'INTERNAL_SERVER_ERROR',
                'details': 'Please contact support if this issue persists.',
                'status_code': 500
            }
            response = Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Log the error for debugging (optional)
    if response and response.status_code >= 400:
        logger.warning(f"API Error {response.status_code}: {exc} - Request: {request.method} {request.path}")

    return response
