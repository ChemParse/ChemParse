```python
import chemparse as chp
from IPython.display import HTML
```

The main class is File


```python
orca_file = chp.File("example.out")
display(orca_file)
```


    <chemparse.file.File at 0x75c2fd715450>


You can convert orca output to HTML

It is better not to insert ccs and js for jupyter view


```python
HTML(orca_file.create_html(insert_css=False, insert_js=False))
```




<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ORCA</title>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <!-- Left sidebar content (TOC) -->
            <div class="toc">
    <!-- JavaScript will populate this area -->
</div>        </div>
        <div class="comment-sidebar">
            <!-- comment sidebar for color-comment sections -->
            <!-- JavaScript will populate this area -->
        </div>
        <div class="content">
            <div class="element" python-class-name="Spacer" start-line=1 finish-line=2 is-block="False">
<br></div><div class="element block" python-class-name="BlockUnknown" readable-name="My start of the message messag..." start-line=3 finish-line=5 specified-class-name="BlockUnknown"data_available=False><div class="data">
<pre>My start of the message: message1
message2
</pre></div></div><hr class = "hr-between-blocks"></hr><div class="element" python-class-name="Spacer" start-line=6 finish-line=7 is-block="False">
<br></div><div class="element block" python-class-name="BlockOrcaUnrecognizedWithSingeLineHeader" readable-name="My data" start-line=6 finish-line=12 specified-class-name="BlockOrcaUnrecognizedWithSingeLineHeader"data_available=False><div class="header"><h7>
<pre>--------------------
My data
--------------------
</pre></h7></div><hr class="hr-in-block"></hr><div class="data">
<pre> 
My value: 1.234 eV

</pre></div></div><hr class = "hr-between-blocks"></hr><div class="element block" python-class-name="BlockOrcaUnrecognizedWithSingeLineHeader" readable-name="Another data" start-line=13 finish-line=19 specified-class-name="BlockOrcaUnrecognizedWithSingeLineHeader"data_available=False><div class="header"><h7>
<pre>                            ***************************************
                            *            Another data             *
                            ***************************************
</pre></h7></div><hr class="hr-in-block"></hr><div class="data">
<pre>Not my match
My value: 9.876 eV

</pre></div></div><hr class = "hr-between-blocks"></hr><div class="element block" python-class-name="BlockOrcaFinalSinglePointEnergy" readable-name="FINAL SINGLE POINT ENERGY" start-line=18 finish-line=21 specified-class-name="BlockOrcaFinalSinglePointEnergy"data_available=True><div class="data">
<pre>-------------------------   --------------------
FINAL SINGLE POINT ENERGY      -440.508559636589
-------------------------   --------------------
</pre></div></div><hr class = "hr-between-blocks"></hr><div class="element" python-class-name="Spacer" start-line=22 finish-line=24 is-block="False">
<br><br></div><div class="element block" python-class-name="BlockOrcaTerminatedNormally" readable-name="ORCA TERMINATED NORMALLY" start-line=23 finish-line=24 specified-class-name="BlockOrcaTerminatedNormally"data_available=True><div class="data">
<pre>                             ****ORCA TERMINATED NORMALLY****
</pre></div></div><hr class = "hr-between-blocks"></hr><div class="element block" python-class-name="BlockOrcaTotalRunTime" readable-name="TOTAL RUN TIME" start-line=24 finish-line=25 specified-class-name="BlockOrcaTotalRunTime"data_available=True><div class="data">
<pre>TOTAL RUN TIME: 0 days 0 hours 0 minutes 26 seconds 139 msec
</pre></div></div><hr class = "hr-between-blocks"></hr>
        </div>
    </div>
</body>
</html>



CSS and JS can give way more information


```python
orca_file.save_as_html("example.html", insert_css=True, insert_js=True)
```

Let's look at the blocks in the file

Position stands for the begging and final lines of the block. Positions of the spacers are not identified


```python
orca_file.get_blocks()
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
      <th>8092521010537</th>
      <td>Block</td>
      <td>BlockOrcaTotalRunTime</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaTotalRunTime...</td>
      <td>(565, 625)</td>
      <td>(24, 25)</td>
    </tr>
    <tr>
      <th>8092521010777</th>
      <td>Block</td>
      <td>BlockOrcaTerminatedNormally</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaTerminatedNo...</td>
      <td>(503, 564)</td>
      <td>(23, 24)</td>
    </tr>
    <tr>
      <th>8092521010588</th>
      <td>Block</td>
      <td>BlockOrcaFinalSinglePointEnergy</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaFinalSingleP...</td>
      <td>(354, 500)</td>
      <td>(18, 21)</td>
    </tr>
    <tr>
      <th>8092521010894</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(45, 116)</td>
      <td>(6, 12)</td>
    </tr>
    <tr>
      <th>8092521010864</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(117, 353)</td>
      <td>(13, 19)</td>
    </tr>
    <tr>
      <th>8092521010996</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;chemparse.elements.Spacer object at 0x75c2fd7...</td>
      <td>(0, 0)</td>
      <td>(1, 2)</td>
    </tr>
    <tr>
      <th>8092521010879</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;chemparse.elements.Spacer object at 0x75c2fd7...</td>
      <td>(44, 44)</td>
      <td>(6, 7)</td>
    </tr>
    <tr>
      <th>8092521011128</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;chemparse.elements.Spacer object at 0x75c2fd7...</td>
      <td>(501, 502)</td>
      <td>(22, 24)</td>
    </tr>
    <tr>
      <th>8092521010819</th>
      <td>Block</td>
      <td>BlockUnknown</td>
      <td>&lt;chemparse.elements.BlockUnknown object at 0x7...</td>
      <td>(1, 43)</td>
      <td>(3, 5)</td>
    </tr>
  </tbody>
</table>
</div>



Let's extract the raw data. `get_data` returns pandas DataFrame


```python
orca_file.get_data(extract_only_raw=True)
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
      <th>ReadableName</th>
      <th>RawData</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>8092521010537</th>
      <td>Block</td>
      <td>BlockOrcaTotalRunTime</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaTotalRunTime...</td>
      <td>(565, 625)</td>
      <td>(24, 25)</td>
      <td>TOTAL RUN TIME</td>
      <td>TOTAL RUN TIME: 0 days 0 hours 0 minutes 26 se...</td>
    </tr>
    <tr>
      <th>8092521010777</th>
      <td>Block</td>
      <td>BlockOrcaTerminatedNormally</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaTerminatedNo...</td>
      <td>(503, 564)</td>
      <td>(23, 24)</td>
      <td>ORCA TERMINATED NORMALLY</td>
      <td>****ORCA TERMINAT...</td>
    </tr>
    <tr>
      <th>8092521010588</th>
      <td>Block</td>
      <td>BlockOrcaFinalSinglePointEnergy</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaFinalSingleP...</td>
      <td>(354, 500)</td>
      <td>(18, 21)</td>
      <td>FINAL SINGLE POINT ENERGY</td>
      <td>-------------------------   ------------------...</td>
    </tr>
    <tr>
      <th>8092521010894</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(45, 116)</td>
      <td>(6, 12)</td>
      <td>My data</td>
      <td>--------------------\nMy data\n---------------...</td>
    </tr>
    <tr>
      <th>8092521010864</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(117, 353)</td>
      <td>(13, 19)</td>
      <td>Another data</td>
      <td>******************...</td>
    </tr>
    <tr>
      <th>8092521010996</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;chemparse.elements.Spacer object at 0x75c2fd7...</td>
      <td>(0, 0)</td>
      <td>(1, 2)</td>
      <td>None</td>
      <td>\n</td>
    </tr>
    <tr>
      <th>8092521010879</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;chemparse.elements.Spacer object at 0x75c2fd7...</td>
      <td>(44, 44)</td>
      <td>(6, 7)</td>
      <td>None</td>
      <td>\n</td>
    </tr>
    <tr>
      <th>8092521011128</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;chemparse.elements.Spacer object at 0x75c2fd7...</td>
      <td>(501, 502)</td>
      <td>(22, 24)</td>
      <td>None</td>
      <td>\n\n</td>
    </tr>
    <tr>
      <th>8092521010819</th>
      <td>Block</td>
      <td>BlockUnknown</td>
      <td>&lt;chemparse.elements.BlockUnknown object at 0x7...</td>
      <td>(1, 43)</td>
      <td>(3, 5)</td>
      <td>My start of the message messag...</td>
      <td>My start of the message: message1\nmessage2\n</td>
    </tr>
  </tbody>
</table>
</div>



Let's extract the processed data

You will get warnings about the unrecognized blocks. ExtractedData type is None or orcaparser.data.Data


```python
orca_file.get_data()
```

    2024-10-11 14:47:07,100 - chemparse - WARNING - No procedure for analyzing the data found in type `BlockOrcaUnrecognizedWithSingeLineHeader`, returning the raw data:
    --------------------
    My data
    --------------------
     
    My value: 1.234 eV
    
    
    2024-10-11 14:47:07,101 - chemparse - WARNING - No procedure for analyzing the data found in type `BlockOrcaUnrecognizedWithSingeLineHeader`, returning the raw data:
                                ***************************************
                                *            Another data             *
                                ***************************************
    Not my match
    My value: 9.876 eV
    
    
    2024-10-11 14:47:07,102 - chemparse - WARNING - The block looks unstructured. Please contribute to the project if you have knowledge on how to extract data from it.





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
      <th>ReadableName</th>
      <th>RawData</th>
      <th>ExtractedData</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>8092521010537</th>
      <td>Block</td>
      <td>BlockOrcaTotalRunTime</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaTotalRunTime...</td>
      <td>(565, 625)</td>
      <td>(24, 25)</td>
      <td>TOTAL RUN TIME</td>
      <td>TOTAL RUN TIME: 0 days 0 hours 0 minutes 26 se...</td>
      <td>[Run Time]</td>
    </tr>
    <tr>
      <th>8092521010777</th>
      <td>Block</td>
      <td>BlockOrcaTerminatedNormally</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaTerminatedNo...</td>
      <td>(503, 564)</td>
      <td>(23, 24)</td>
      <td>ORCA TERMINATED NORMALLY</td>
      <td>****ORCA TERMINAT...</td>
      <td>[Termination status]</td>
    </tr>
    <tr>
      <th>8092521010588</th>
      <td>Block</td>
      <td>BlockOrcaFinalSinglePointEnergy</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaFinalSingleP...</td>
      <td>(354, 500)</td>
      <td>(18, 21)</td>
      <td>FINAL SINGLE POINT ENERGY</td>
      <td>-------------------------   ------------------...</td>
      <td>[Energy]</td>
    </tr>
    <tr>
      <th>8092521010894</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(45, 116)</td>
      <td>(6, 12)</td>
      <td>My data</td>
      <td>--------------------\nMy data\n---------------...</td>
      <td>[raw data]</td>
    </tr>
    <tr>
      <th>8092521010864</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(117, 353)</td>
      <td>(13, 19)</td>
      <td>Another data</td>
      <td>******************...</td>
      <td>[raw data]</td>
    </tr>
    <tr>
      <th>8092521010996</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;chemparse.elements.Spacer object at 0x75c2fd7...</td>
      <td>(0, 0)</td>
      <td>(1, 2)</td>
      <td>None</td>
      <td>\n</td>
      <td>None</td>
    </tr>
    <tr>
      <th>8092521010879</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;chemparse.elements.Spacer object at 0x75c2fd7...</td>
      <td>(44, 44)</td>
      <td>(6, 7)</td>
      <td>None</td>
      <td>\n</td>
      <td>None</td>
    </tr>
    <tr>
      <th>8092521011128</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;chemparse.elements.Spacer object at 0x75c2fd7...</td>
      <td>(501, 502)</td>
      <td>(22, 24)</td>
      <td>None</td>
      <td>\n\n</td>
      <td>None</td>
    </tr>
    <tr>
      <th>8092521010819</th>
      <td>Block</td>
      <td>BlockUnknown</td>
      <td>&lt;chemparse.elements.BlockUnknown object at 0x7...</td>
      <td>(1, 43)</td>
      <td>(3, 5)</td>
      <td>My start of the message messag...</td>
      <td>My start of the message: message1\nmessage2\n</td>
      <td>[raw data]</td>
    </tr>
  </tbody>
</table>
</div>



Let's extract the specific block that has "My value" in it

The same text may occur in different blocks


```python
orca_file.get_data(raw_data_substring="My value")
```

    2024-10-11 14:47:07,112 - chemparse - WARNING - No procedure for analyzing the data found in type `BlockOrcaUnrecognizedWithSingeLineHeader`, returning the raw data:
    --------------------
    My data
    --------------------
     
    My value: 1.234 eV
    
    
    2024-10-11 14:47:07,112 - chemparse - WARNING - No procedure for analyzing the data found in type `BlockOrcaUnrecognizedWithSingeLineHeader`, returning the raw data:
                                ***************************************
                                *            Another data             *
                                ***************************************
    Not my match
    My value: 9.876 eV
    
    





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
      <th>ReadableName</th>
      <th>RawData</th>
      <th>ExtractedData</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>8092521010894</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(45, 116)</td>
      <td>(6, 12)</td>
      <td>My data</td>
      <td>--------------------\nMy data\n---------------...</td>
      <td>[raw data]</td>
    </tr>
    <tr>
      <th>8092521010864</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(117, 353)</td>
      <td>(13, 19)</td>
      <td>Another data</td>
      <td>******************...</td>
      <td>[raw data]</td>
    </tr>
  </tbody>
</table>
</div>



The easiest way to extract the needed data in this case is to add some other text that is present in the block


```python
orca_file.get_data(raw_data_substring=("My value", "My data"))
```

    2024-10-11 14:47:07,119 - chemparse - WARNING - No procedure for analyzing the data found in type `BlockOrcaUnrecognizedWithSingeLineHeader`, returning the raw data:
    --------------------
    My data
    --------------------
     
    My value: 1.234 eV
    
    





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
      <th>ReadableName</th>
      <th>RawData</th>
      <th>ExtractedData</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>8092521010894</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(45, 116)</td>
      <td>(6, 12)</td>
      <td>My data</td>
      <td>--------------------\nMy data\n---------------...</td>
      <td>[raw data]</td>
    </tr>
  </tbody>
</table>
</div>



Or to exclude the ones that are not yours


```python
orca_file.get_data(raw_data_substring="My value",
                   raw_data_not_substring="Not my match")
```

    2024-10-11 14:47:07,127 - chemparse - WARNING - No procedure for analyzing the data found in type `BlockOrcaUnrecognizedWithSingeLineHeader`, returning the raw data:
    --------------------
    My data
    --------------------
     
    My value: 1.234 eV
    
    





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
      <th>ReadableName</th>
      <th>RawData</th>
      <th>ExtractedData</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>8092521010894</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(45, 116)</td>
      <td>(6, 12)</td>
      <td>My data</td>
      <td>--------------------\nMy data\n---------------...</td>
      <td>[raw data]</td>
    </tr>
  </tbody>
</table>
</div>



or we can extract the one we need by the readable name (you can find it in html file TOC)


```python
orca_file.get_data(readable_name="My data")
```

    2024-10-11 14:47:07,133 - chemparse - WARNING - No procedure for analyzing the data found in type `BlockOrcaUnrecognizedWithSingeLineHeader`, returning the raw data:
    --------------------
    My data
    --------------------
     
    My value: 1.234 eV
    
    





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
      <th>ReadableName</th>
      <th>RawData</th>
      <th>ExtractedData</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>8092521010894</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(45, 116)</td>
      <td>(6, 12)</td>
      <td>My data</td>
      <td>--------------------\nMy data\n---------------...</td>
      <td>[raw data]</td>
    </tr>
  </tbody>
</table>
</div>



You can ask for more than one parameter of search


```python
orca_file.get_data(raw_data_substring=(
    "My value", "My data"), readable_name="My data")
```

    2024-10-11 14:47:07,140 - chemparse - WARNING - No procedure for analyzing the data found in type `BlockOrcaUnrecognizedWithSingeLineHeader`, returning the raw data:
    --------------------
    My data
    --------------------
     
    My value: 1.234 eV
    
    





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
      <th>ReadableName</th>
      <th>RawData</th>
      <th>ExtractedData</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>8092521010894</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;chemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(45, 116)</td>
      <td>(6, 12)</td>
      <td>My data</td>
      <td>--------------------\nMy data\n---------------...</td>
      <td>[raw data]</td>
    </tr>
  </tbody>
</table>
</div>



Lets extract the data and have a look on what it contains


```python
df = orca_file.get_data(readable_name="My data")
```

    2024-10-11 14:47:07,147 - chemparse - WARNING - No procedure for analyzing the data found in type `BlockOrcaUnrecognizedWithSingeLineHeader`, returning the raw data:
    --------------------
    My data
    --------------------
     
    My value: 1.234 eV
    
    



```python
data = df.iloc[0].ExtractedData
print(f"{type(data) = }")
print(f"{str(data) = }")
```

    type(data) = <class 'chemparse.data.Data'>
    str(data) = 'Data with items: `raw data`. Comment: No procedure for analyzing the data found, `raw data` collected.\nPlease contribute to the project if you have knowledge on how to extract data from it.'


Even though no method for the extraction was found, the data can be extracted as text


```python
data["raw data"]
```




    '--------------------\nMy data\n--------------------\n \nMy value: 1.234 eV\n\n'



Lets extract the data that is known

Time is stored as timedelta, tables as pandas Dataframes, values with units as pint Quantity


```python
df = orca_file.get_data(readable_name="TOTAL RUN TIME")
data = df.iloc[0].ExtractedData
print(f"{str(data) = }")
print(f'{data["Run Time"] = }')
```

    str(data) = 'Data with items: `Run Time`. Comment: `Run Time` is timedelta object'
    data["Run Time"] = datetime.timedelta(seconds=26, microseconds=139000)



```python
df = orca_file.get_data(readable_name="FINAL SINGLE POINT ENERGY")
data = df.iloc[0].ExtractedData
print(f"{str(data) = }")
print(f'{data["Energy"] = }')
print(f'{data["Energy"].magnitude = }')
print(f'{data["Energy"].units = }')
```

    str(data) = 'Data with items: `Energy`. Comment: `Energy` in pint format, to extract the value in Eh, use property .magnitude'
    data["Energy"] = <Quantity(-440.50856, 'hartree')>
    data["Energy"].magnitude = -440.508559636589
    data["Energy"].units = <Unit('hartree')>



```python

```
