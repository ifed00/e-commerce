# Using filters:
Filters are utilized by means of GET-request to the category page.

Suppose we have *Illuminations* category under `/category/illuminations` URL. 
This category has a boolean property `is_candle`.

To filter only candles `BOOLEAN_CHOICES` **filter type** 
with the same name `is_candle` is utilized, by requesting corresponding `GET-key`:

```
/category/illuminations?is_candle=1
```

Which GET-keys are available and which values they can have is depends on **filter type**, described below.

Not including GET-key at all simply produces no filtering.

# Filter types
There are total of 4 filter types, at least for now:
- BOUND
- DYNAMIC_CHOICES
- STATIC_CHOICES
- BOOL_CHOICES

They are described below.

## BOUND 
Filters by a numeric field, checking whether it is in user-provided and available range.
The available range is determined dynamically by a request to DB.

### GET-Keys
There are 2 get keys for this filter: _min and _max.
They are derived from `field_name` by corresponding suffixes.

### Example
Consider `price` field. Suppose we have 4 products with given prices:
- A - 1000$
- B - 600$
- C - 800$
- D - 200$

You can set min and max bounds to filter, they can only be in a range, provided by DB, in our case: 200 <= price_min <= price_max <= 1000.

Suppose we set:
- `price_min=200`, `price_max=700` => only D and B will be included.
- `price_min=500`, `price_max` - unset => A, B and C.
- `price_min=300`, `price_min` - unset => only D.
- `price_min=700`, `price_max=5000` => only A. `_max` is above possible range so it is considered as maximum possible value.
- `price_min=0`, `price_max=300` => only D. See above case but for `_min`.
- `price_min=500`, `price_max=300` => A, B, C and D. This time `_min` > `_max` so values are ignored.

## DYNAMIC_CHOICES & STATIC_CHOICES
These two share a lot so they are described together.

`STATIC_CHOICES` filters by a static set of variants (e.g. there are only so many types of coffee: 
cappicino, espresso, etc, the important thing here is that is a finite and predefined set of *choices*)

`DYNAMIC_CHOICES` filters by field with arbitrary variants (e.g. we can have a product with some new manufacturer any time soon!), 
available variants determined by a DB request.

Provided multiple variants both filters return objects with any of these variants.

### GET-Keys
Only one `GET-key` which is the same as `field_name`.

### Example
Consider category *Coffees* under `/category/coffees/` URL with `coffee_type` field, with the following DB data:
- A - cappucino
- B - espresso
- C - makkiato
- D - cappucino

Suppose we set:
-`coffee_type=cappucino` => A and D.
- `coffee_type=cappucino,espresso` => A, B and D.
- `coffee_type=notAType` => A, B, C and D.
- `coffee_type=makkiato,WRONG+COFFEE` => only C.

As you can see wrong options are ignored.

## BOOL_CHOICES
Filters by a boolean field. Multiple choices are forbidden.

### GET-Keys
Only one `GET-key` which is the same as `field_name`.

### Example
Consider *Illuminations* category under `/category/illuminations` URL. 
This category has a boolean property `is_candle` and DB data is:
- A - candle
- B - candle
- C - not a candle

Suppose we set:
- `is_candle=1` => A and B
- `is_candle=0` => only C
- `is_candle=AnyWrongOption` => A, B and C
- `is_candle=2` => A, B and C
- not include `is_candle` at all => A, B and C
