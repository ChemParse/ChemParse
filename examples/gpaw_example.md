```python
import chemparse as chp
```

Use `mode` argument to change the extraction mode in `File`

For now, `ORCA` and `GPAW` are available


```python
gpaw_file = chp.File("example_gpaw.txt", mode="GPAW")
```


```python
gpaw_file.get_blocks()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Type</th>
      <th>Subtype</th>
      <th>Element</th>
      <th>CharPosition</th>
      <th>LinePosition</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>8749855079965</th>
      <td>Block</td>
      <td>BlockGpawIcon</td>
      <td>&lt;chemparse.gpaw_elements.BlockGpawIcon object ...</td>
      <td>(1, 109)</td>
      <td>(3, 8)</td>
    </tr>
    <tr>
      <th>8749855080007</th>
      <td>Block</td>
      <td>BlockGpawDipole</td>
      <td>&lt;chemparse.gpaw_elements.BlockGpawDipole objec...</td>
      <td>(111, 166)</td>
      <td>(11, 12)</td>
    </tr>
    <tr>
      <th>8749855079905</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;chemparse.elements.Spacer object at 0x7f53c00...</td>
      <td>(0, 0)</td>
      <td>(1, 2)</td>
    </tr>
    <tr>
      <th>8749855079983</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;chemparse.elements.Spacer object at 0x7f53c00...</td>
      <td>(110, 110)</td>
      <td>(9, 10)</td>
    </tr>
  </tbody>
</table>
</div>



Scripts support `mode` as well


```python
! chem_to_html example_gpaw.txt example_gpaw.html --mode GPAW
```

Available blocks are stores as


```python
chp.gpaw_elements.AvailableBlocksGpaw.blocks
```




    {'BlockGpawIcon': chemparse.gpaw_elements.BlockGpawIcon,
     'BlockGpawDipole': chemparse.gpaw_elements.BlockGpawDipole,
     'BlockGpawEnergyContributions': chemparse.gpaw_elements.BlockGpawEnergyContributions,
     'BlockGpawConvergedAfter': chemparse.gpaw_elements.BlockGpawConvergedAfter,
     'BlockGpawOrbitalEnergies': chemparse.gpaw_elements.BlockGpawOrbitalEnergies,
     'BlockGpawTiming': chemparse.gpaw_elements.BlockGpawTiming}


