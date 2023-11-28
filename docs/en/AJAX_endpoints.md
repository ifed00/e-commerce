# Sending AJAX POST requests

To prevent [cross-site request forgery attack](https://en.wikipedia.org/wiki/Cross-site_request_forgery)
django uses CSRF-tokens system. 
AJAX POST requests without `"X-CSRFToken"` cookie with correct value will be blocked with `status=403` HTTP-code. 
GET-requests do not require this cookie.

You can get CSRF-token for this page using following JS-snippet:
`````
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');
`````
or using [JavaScript cookie library](https://github.com/js-cookie/js-cookie/):
``````
const csrftoken = Cookies.get('csrftoken');
``````
See [source](https://docs.djangoproject.com/en/4.2/howto/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false)
for more information.

Then requests can be sent e.g. with following snippet:
`````
fetch(
  *URL*, 
  {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify(*payload*)
  }
)
`````

# AJAX-Endpoints

## order/add
*method: POST*

This endpoint adds product to current user's basket.

Accepts JSON-serialized objects with at most 2 keys:
``````
{
    product_id: *positive int*
    amount: *positive int*
}
``````
By default `amount=1`, you can omit this key.

Response is JSON-serialized object with at most 2 keys:
```````
{
    success: *bool*
    error: *string* or *object*
}
```````

### Possible responses
1. `success=True` with `status=200`. Item successfully added to user's basket. No `error` key included.
1. `success=False` with `status=403`. Request came from unauthorized user. Appropriate `error` key is set.

1. `success=False` with `status=400`. Either request's body is not valid JSON-string or request data invalid.
   - If request body is not JSON, `error='request malformed: use JSON format'`.
   - if request data is invalid, `error` is auto-generated object with keys for each request-key with errors and value is array of strings (possibly with single element) describing the error.
1. `success=False` with `status=422`. Requested amount is more than available to sell. Appropriate `error` key is set.


## order/delete
*method: POST*

This endpoint deletes product from current user's basket.

See request/response format in endpoint above.

If `amount` is more than there are given products in user's basket all of them are removed without special warning.

### Possible responses
See in endpoint above, except `status=422`.