Convert orca output to html


```python
! chem_to_html example.out example.html
```

The data can be extracted as .csv, .json, .html and excel

Lets extract the data as in the basic example


```python
! chem_parse example.out example_data.html --raw_data_substring "My value"
```

As it extracts the additional data we were not looking for, let's add more conditions


```python
! chem_parse example.out example_data.html --raw_data_substring "My value" --readable_name "My data"
```

Or


```python
! chem_parse example.out example_data.html --raw_data_substring "My value" --raw_data_not_substring "Not my match"
```

Or


```python
! chem_parse example.out example_data.html --raw_data_substring "My value" --raw_data_substring "My data"
```
