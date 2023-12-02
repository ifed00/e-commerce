# Sending AJAX POST requests

To prevent [cross-site request forgery attack](https://en.wikipedia.org/wiki/Cross-site_request_forgery)
django uses CSRF-tokens system. 
AJAX POST requests without `"X-CSRFToken"` cookie with correct value will be blocked with `status=403` HTTP-code. 
GET-requests do not require this cookie.

You can get CSRF-token for this page using following JS-snippet:
```
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
```
or using [JavaScript cookie library](https://github.com/js-cookie/js-cookie/):
```
const csrftoken = Cookies.get('csrftoken');
```
See [source](https://docs.djangoproject.com/en/4.2/howto/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false)
for more information.

Then requests can be sent e.g. with following snippet:
```
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
```

# AJAX-Endpoints

## order/add
*method: POST*

This endpoint adds product to current user's basket.

Accepts JSON objects with at most 2 keys:
```
{
    product_id: *positive int*
    amount: *positive int*
}
```
By default `amount=1`, you can omit this key.

Response is JSON object with at most 2 keys:
```
{
    success: *bool*
    error: *string* or *object*
}
```

### Possible responses
1. `success=True` with `status=200`. Item successfully added to user's basket. No `error` key included.
1. `success=False` with `status=403`. Request came from unauthorized user. Appropriate `error` key is set.

1. `success=False` with `status=400`. Either request's body is not valid JSON-string or request data invalid.
   - If request body is not valid JSON, `error='request malformed: use JSON format'`.
   - if request data is invalid, `error` is auto-generated object with keys for each request-key with errors and value is array of strings (possibly with single element) describing the error.
1. `success=False` with `status=422`. Requested amount is more than available to sell. Appropriate `error` key is set.


## order/delete
*method: POST*

This endpoint deletes product from current user's basket.

See request/response format in endpoint above.

If `amount` is more than there are given products in user's basket all of them are removed without special warning.

### Possible responses
See in endpoint above, except `status=422`.

## products/random
*method: GET*

This endpoint returns up to 10 random products.

Accepts following GET-keys:
```
   page=*int*
   reset
```
Key `page` sets 1-based number of page to retrieve. By default `page=1`, you can omit this key.

Key `reset` shuffles products, omit this key if this is not what you want.

Response is JSON object with at most 2 keys:
```
{
    has_next_page: *bool*
    products: *array of at most 10 products, see below*
}
```
`product` is JSON object with following keys:
```
{
   pk: *int*
   name: *string*
   picture: *string*, URL for this picture is: MEDIA_URL/picture
   category__name: *string*
   category__slug: *string*
}
```

*Note*: if the page is last (`has_next_page=False`) length of `products` may be less than 10.

This endpoint is deterministic *for given session*: 
it will return same products for same `page` number 
until it gets `reset` key.

E.g. two sequential `products/random?page=2` will yield same result.
But `products/random?page=2&reset` will usually yield different result.

### Possible responses
1. `status=200`. Ok.
2. `status=400` and empty JSON-object. Either `page` value is not a number or requested page does not exits.