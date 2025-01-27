```python
import re

import pychemparse as chp
```

`My data` and `Another data` blocks were recognized as `BlockOrcaUnrecognizedWithHeader` and `My start of the message messag` block was recognized as `BlockUnknown`


```python
orca_file = chp.File("example.out")
orca_file.get_data()
```

    2024-10-11 14:46:14,058 - pychemparse - WARNING - No procedure for analyzing the data found in type `BlockOrcaUnrecognizedWithSingeLineHeader`, returning the raw data:
    --------------------
    My data
    --------------------
     
    My value: 1.234 eV
    
    
    2024-10-11 14:46:14,059 - pychemparse - WARNING - No procedure for analyzing the data found in type `BlockOrcaUnrecognizedWithSingeLineHeader`, returning the raw data:
                                ***************************************
                                *            Another data             *
                                ***************************************
    Not my match
    My value: 9.876 eV
    
    
    2024-10-11 14:46:14,059 - pychemparse - WARNING - The block looks unstructured. Please contribute to the project if you have knowledge on how to extract data from it.





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
      <th>8202901077302</th>
      <td>Block</td>
      <td>BlockOrcaTotalRunTime</td>
      <td>&lt;pychemparse.orca_elements.BlockOrcaTotalRunTime...</td>
      <td>(565, 625)</td>
      <td>(24, 25)</td>
      <td>TOTAL RUN TIME</td>
      <td>TOTAL RUN TIME: 0 days 0 hours 0 minutes 26 se...</td>
      <td>[Run Time]</td>
    </tr>
    <tr>
      <th>8202901077419</th>
      <td>Block</td>
      <td>BlockOrcaTerminatedNormally</td>
      <td>&lt;pychemparse.orca_elements.BlockOrcaTerminatedNo...</td>
      <td>(503, 564)</td>
      <td>(23, 24)</td>
      <td>ORCA TERMINATED NORMALLY</td>
      <td>****ORCA TERMINAT...</td>
      <td>[Termination status]</td>
    </tr>
    <tr>
      <th>8202901077344</th>
      <td>Block</td>
      <td>BlockOrcaFinalSinglePointEnergy</td>
      <td>&lt;pychemparse.orca_elements.BlockOrcaFinalSingleP...</td>
      <td>(354, 500)</td>
      <td>(18, 21)</td>
      <td>FINAL SINGLE POINT ENERGY</td>
      <td>-------------------------   ------------------...</td>
      <td>[Energy]</td>
    </tr>
    <tr>
      <th>8202901077494</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;pychemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(45, 116)</td>
      <td>(6, 12)</td>
      <td>My data</td>
      <td>--------------------\nMy data\n---------------...</td>
      <td>[raw data]</td>
    </tr>
    <tr>
      <th>8202901077275</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;pychemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(117, 353)</td>
      <td>(13, 19)</td>
      <td>Another data</td>
      <td>******************...</td>
      <td>[raw data]</td>
    </tr>
    <tr>
      <th>8202901077425</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;pychemparse.elements.Spacer object at 0x775e301...</td>
      <td>(0, 0)</td>
      <td>(1, 2)</td>
      <td>None</td>
      <td>\n</td>
      <td>None</td>
    </tr>
    <tr>
      <th>8202901077518</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;pychemparse.elements.Spacer object at 0x775e301...</td>
      <td>(44, 44)</td>
      <td>(6, 7)</td>
      <td>None</td>
      <td>\n</td>
      <td>None</td>
    </tr>
    <tr>
      <th>8202901077551</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;pychemparse.elements.Spacer object at 0x775e301...</td>
      <td>(501, 502)</td>
      <td>(22, 24)</td>
      <td>None</td>
      <td>\n\n</td>
      <td>None</td>
    </tr>
    <tr>
      <th>8202944310245</th>
      <td>Block</td>
      <td>BlockUnknown</td>
      <td>&lt;pychemparse.elements.BlockUnknown object at 0x7...</td>
      <td>(1, 43)</td>
      <td>(3, 5)</td>
      <td>My start of the message messag...</td>
      <td>My start of the message: message1\nmessage2\n</td>
      <td>[raw data]</td>
    </tr>
  </tbody>
</table>
</div>



Let's start with the simple ways of introducing your block, and later we will discuss the structure os the search and use the more advanced methods


```python
rs = chp.RegexSettings(chp.DEFAULT_ORCA_REGEX_FILE)
```

`My data` and `Another data` blocks have quite a standard pattern: Single Line Header

Lets add `My data` to the blueprint for this type of patterns
Use BlockNameOfBlock for the class name


```python
rs.items["TypeKnownBlocks"].items["BlueprintBlockWithSingeLineHeader"].add_item(
    name="BlockOrcaMyData", pattern_text="My data"
)
```

We will detect the first block as paragraph that starts with 'My start of the message'


```python
rs.items["TypeKnownBlocks"].items["BlueprintParagraphStartsWith"].add_item(
    name="BlockOrcaMyStart", pattern_text="My start of the message"
)
```

Let's look at the changes.

We should load our new regex settings file at the creation of `File` object


```python
orca_file = chp.File("example.out", regex_settings=rs)
orca_file.get_data()
```

    2024-10-11 14:46:14,088 - pychemparse - WARNING - Subtype `BlockOrcaMyStart` not recognized. Falling back to Block.
    2024-10-11 14:46:14,095 - pychemparse - WARNING - Subtype `BlockOrcaMyData` not recognized. Falling back to Block.
    2024-10-11 14:46:14,108 - pychemparse - WARNING - No procedure for analyzing the data found in type `Block`, returning the raw data:
    My start of the message: message1
    message2
    
    2024-10-11 14:46:14,109 - pychemparse - WARNING - No procedure for analyzing the data found in type `Block`, returning the raw data:
    --------------------
    My data
    --------------------
     
    My value: 1.234 eV
    
    
    2024-10-11 14:46:14,109 - pychemparse - WARNING - No procedure for analyzing the data found in type `BlockOrcaUnrecognizedWithSingeLineHeader`, returning the raw data:
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
      <th>8202901076482</th>
      <td>Block</td>
      <td>BlockOrcaTotalRunTime</td>
      <td>&lt;pychemparse.orca_elements.BlockOrcaTotalRunTime...</td>
      <td>(565, 625)</td>
      <td>(24, 25)</td>
      <td>TOTAL RUN TIME</td>
      <td>TOTAL RUN TIME: 0 days 0 hours 0 minutes 26 se...</td>
      <td>[Run Time]</td>
    </tr>
    <tr>
      <th>8202901076530</th>
      <td>Block</td>
      <td>BlockOrcaTerminatedNormally</td>
      <td>&lt;pychemparse.orca_elements.BlockOrcaTerminatedNo...</td>
      <td>(503, 564)</td>
      <td>(23, 24)</td>
      <td>ORCA TERMINATED NORMALLY</td>
      <td>****ORCA TERMINAT...</td>
      <td>[Termination status]</td>
    </tr>
    <tr>
      <th>8202901076488</th>
      <td>Block</td>
      <td>BlockOrcaFinalSinglePointEnergy</td>
      <td>&lt;pychemparse.orca_elements.BlockOrcaFinalSingleP...</td>
      <td>(354, 500)</td>
      <td>(18, 21)</td>
      <td>FINAL SINGLE POINT ENERGY</td>
      <td>-------------------------   ------------------...</td>
      <td>[Energy]</td>
    </tr>
    <tr>
      <th>8202901076566</th>
      <td>Block</td>
      <td>BlockOrcaMyStart</td>
      <td>&lt;pychemparse.elements.Block object at 0x775e3013...</td>
      <td>(1, 43)</td>
      <td>(3, 5)</td>
      <td>My start of the message messag...</td>
      <td>My start of the message: message1\nmessage2\n</td>
      <td>[raw data]</td>
    </tr>
    <tr>
      <th>8202901076785</th>
      <td>Block</td>
      <td>BlockOrcaMyData</td>
      <td>&lt;pychemparse.elements.Block object at 0x775e3013...</td>
      <td>(45, 116)</td>
      <td>(8, 14)</td>
      <td>My data My value eV</td>
      <td>--------------------\nMy data\n---------------...</td>
      <td>[raw data]</td>
    </tr>
    <tr>
      <th>8202901076629</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;pychemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(117, 353)</td>
      <td>(15, 21)</td>
      <td>Another data</td>
      <td>******************...</td>
      <td>[raw data]</td>
    </tr>
    <tr>
      <th>8202901076836</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;pychemparse.elements.Spacer object at 0x775e301...</td>
      <td>(0, 0)</td>
      <td>(1, 2)</td>
      <td>None</td>
      <td>\n</td>
      <td>None</td>
    </tr>
    <tr>
      <th>8202901076842</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;pychemparse.elements.Spacer object at 0x775e301...</td>
      <td>(44, 44)</td>
      <td>(6, 7)</td>
      <td>None</td>
      <td>\n</td>
      <td>None</td>
    </tr>
    <tr>
      <th>8202901076770</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;pychemparse.elements.Spacer object at 0x775e301...</td>
      <td>(501, 502)</td>
      <td>(22, 24)</td>
      <td>None</td>
      <td>\n\n</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>



The Blocks were recognized as `BlockOrcaMyStart` and `BlockOrcaMyData`

Now let's add the data recognition to `BlockOrcaMyData`

Note that I am using `BlockOrcaWithStandardHeader` instead of just `Block`, as I know that this block has a standard header that can be easily separated. But I could use `Block`, then `ReadableName` would be recognized as 'My data My value eV'  instead of 'My data'

Data extraction takes place only on a call, so you don't need to worry much about the performance of your code


```python
@chp.orca_elements.AvailableBlocksOrca.register_block
class BlockOrcaMyData(chp.orca_elements.BlockOrcaWithStandardHeader):

    def data(self):
        pattern = r"My value:\s*(\d+\.\d+)"
        match = re.search(pattern, self.raw_data)
        extracted_number = float(match.group(1)) if match else None
        value = extracted_number * chp.units_and_constants.ureg.eV
        return chp.Data(
            data={
                "My value": value,
                "Another Value": 42
            },
            comment=
            "Contains pint object of `My value`. The magnitude in eV can be extracted with property .magnitude\n`Another value` is 42.",
        )
```

Now lets add the `ReadableName` to `BlockOrcaMyStart`. Now it is 'My start of the message messag...' 


```python
@chp.orca_elements.AvailableBlocksOrca.register_block
class BlockOrcaMyStart(chp.elements.Block):

    def extract_name_header_and_body(self):
        return "My Start", None, self.raw_data
```

Do not forget to restart the orca file


```python
orca_file = chp.File("example.out", regex_settings=rs)
orca_file.get_data()
```

    2024-10-11 14:46:14,152 - pychemparse - WARNING - No procedure for analyzing the data found in type `BlockOrcaMyStart`, returning the raw data:
    My start of the message: message1
    message2
    
    2024-10-11 14:46:14,152 - pychemparse - WARNING - No procedure for analyzing the data found in type `BlockOrcaUnrecognizedWithSingeLineHeader`, returning the raw data:
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
      <th>8202901076800</th>
      <td>Block</td>
      <td>BlockOrcaTotalRunTime</td>
      <td>&lt;pychemparse.orca_elements.BlockOrcaTotalRunTime...</td>
      <td>(565, 625)</td>
      <td>(24, 25)</td>
      <td>TOTAL RUN TIME</td>
      <td>TOTAL RUN TIME: 0 days 0 hours 0 minutes 26 se...</td>
      <td>[Run Time]</td>
    </tr>
    <tr>
      <th>8202901076053</th>
      <td>Block</td>
      <td>BlockOrcaTerminatedNormally</td>
      <td>&lt;pychemparse.orca_elements.BlockOrcaTerminatedNo...</td>
      <td>(503, 564)</td>
      <td>(23, 24)</td>
      <td>ORCA TERMINATED NORMALLY</td>
      <td>****ORCA TERMINAT...</td>
      <td>[Termination status]</td>
    </tr>
    <tr>
      <th>8202901076002</th>
      <td>Block</td>
      <td>BlockOrcaFinalSinglePointEnergy</td>
      <td>&lt;pychemparse.orca_elements.BlockOrcaFinalSingleP...</td>
      <td>(354, 500)</td>
      <td>(18, 21)</td>
      <td>FINAL SINGLE POINT ENERGY</td>
      <td>-------------------------   ------------------...</td>
      <td>[Energy]</td>
    </tr>
    <tr>
      <th>8202901076929</th>
      <td>Block</td>
      <td>BlockOrcaMyStart</td>
      <td>&lt;__main__.BlockOrcaMyStart object at 0x775e301...</td>
      <td>(1, 43)</td>
      <td>(3, 5)</td>
      <td>My Start</td>
      <td>My start of the message: message1\nmessage2\n</td>
      <td>[raw data]</td>
    </tr>
    <tr>
      <th>8202901076968</th>
      <td>Block</td>
      <td>BlockOrcaMyData</td>
      <td>&lt;__main__.BlockOrcaMyData object at 0x775e3013...</td>
      <td>(45, 116)</td>
      <td>(8, 14)</td>
      <td>My data</td>
      <td>--------------------\nMy data\n---------------...</td>
      <td>[My value, Another Value]</td>
    </tr>
    <tr>
      <th>8202901773625</th>
      <td>Block</td>
      <td>BlockOrcaUnrecognizedWithSingeLineHeader</td>
      <td>&lt;pychemparse.orca_elements.BlockOrcaUnrecognized...</td>
      <td>(117, 353)</td>
      <td>(15, 21)</td>
      <td>Another data</td>
      <td>******************...</td>
      <td>[raw data]</td>
    </tr>
    <tr>
      <th>8202901773616</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;pychemparse.elements.Spacer object at 0x775e30b...</td>
      <td>(0, 0)</td>
      <td>(1, 2)</td>
      <td>None</td>
      <td>\n</td>
      <td>None</td>
    </tr>
    <tr>
      <th>8202901773553</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;pychemparse.elements.Spacer object at 0x775e30b...</td>
      <td>(44, 44)</td>
      <td>(6, 7)</td>
      <td>None</td>
      <td>\n</td>
      <td>None</td>
    </tr>
    <tr>
      <th>8202901773604</th>
      <td>Spacer</td>
      <td>Spacer</td>
      <td>&lt;pychemparse.elements.Spacer object at 0x775e30b...</td>
      <td>(501, 502)</td>
      <td>(22, 24)</td>
      <td>None</td>
      <td>\n\n</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>



Now our data is ready to be extracted:


```python
df = orca_file.get_data(element_type=BlockOrcaMyData)
display(df)
assert len(df) == 1, "More then 1 `BlockOrcaMyData` found"
data = df.iloc[0].ExtractedData
print(data)
print()
print(f"{data['My value'].magnitude = }")
print(f"{data['Another Value'] = }")
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
      <th>ExtractedData</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>8202901076968</th>
      <td>Block</td>
      <td>BlockOrcaMyData</td>
      <td>&lt;__main__.BlockOrcaMyData object at 0x775e3013...</td>
      <td>(45, 116)</td>
      <td>(8, 14)</td>
      <td>My data</td>
      <td>--------------------\nMy data\n---------------...</td>
      <td>[My value, Another Value]</td>
    </tr>
  </tbody>
</table>
</div>


    Data with items: `My value`, `Another Value`. Comment: Contains pint object of `My value`. The magnitude in eV can be extracted with property .magnitude
    `Another value` is 42.
    
    data['My value'].magnitude = 1.234
    data['Another Value'] = 42


Let's looks at the search algorithm structure

`RegexSettings` is a tree/'directory' object that contains  `RegexSettings`s, `RegexBlueprint`s and `RegexRequest`s. `RegexBlueprint` is a 'generator' object for `RegexRequest`s of the same type. They have `.items` that contains `RegexRequest`s as it was previously shown.


```python
rs = chp.RegexSettings(chp.DEFAULT_ORCA_REGEX_FILE)
print(rs)
```

    RegexGroup:
      TypeKnownBlocks:
        RegexGroup:
          BlockOrcaTotalRunTime: RegexRequest(p_type='Block', p_subtype='BlockOrcaTotalRunTime', pattern='^([ \t]*TOTAL RUN TIME...', flags=re.MULTILINE, comment='This pattern captures ...')
          BlockOrcaTerminatedNormally: RegexRequest(p_type='Block', p_subtype='BlockOrcaTerminatedNormally', pattern='^([ \t]*\*{4}ORCA TERM...', flags=re.MULTILINE, comment='This pattern captures ...')
          BlockOrcaFinalSinglePointEnergy: RegexRequest(p_type='Block', p_subtype='BlockOrcaFinalSinglePointEnergy', pattern='^((-{20,}\s+-{15,}\n)[...', flags=re.MULTILINE, comment='This pattern matches t...')
          BlockOrcaGeometryConvergence: RegexRequest(p_type='Block', p_subtype='BlockOrcaGeometryConvergence', pattern='((?:[ \t]*\.-{5,}\.[ \...', flags=re.MULTILINE, comment='Orca Geometry converge...')
          BlockOrcaDipoleMomentFromOrca6: RegexRequest(p_type='Block', p_subtype='BlockOrcaDipoleMoment', pattern='^(([ \t]*-{10,}[ \t]*\...', flags=re.MULTILINE, comment='Equal signs around the...')
          BlockOrcaDipoleMoment: RegexRequest(p_type='Block', p_subtype='BlockOrcaDipoleMoment', pattern='^(([ \t]*-{10,}[ \t]*\...', flags=re.MULTILINE, comment='Equal signs around the...')
          BlockOrcaInputFile: RegexRequest(p_type='Block', p_subtype='BlockOrcaInputFile', pattern='^((?:[ \t]*={10,}[ \t]...', flags=re.MULTILINE, comment='Equal signs around the...')
          BlockOrcaErrorMessage: RegexRequest(p_type='Block', p_subtype='BlockOrcaErrorMessage', pattern='^((?:[ \t]*[\-\*\#\=]{...', flags=re.MULTILINE, comment='Block with error messa...')
          BlockOrcaShark: RegexRequest(p_type='Block', p_subtype='BlockOrcaShark', pattern='^((?:[ \t]*-{50,}[ \t]...', flags=re.MULTILINE, comment='Starts with line of  -...')
          BlockOrcaWarnings: RegexRequest(p_type='Block', p_subtype='BlockOrcaWarnings', pattern='^((?:[ \t]*\={5,}[ \t]...', flags=re.MULTILINE, comment='WARNINGS, should captu...')
          BlueprintParagraphStartsWith:
            RegexBlueprint:
              BlockOrcaVersion: Pattern: ^([ \t]*Program Version.*?\n(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
              BlockOrcaContributions: Pattern: ^([ \t]*With contributions from.*?\n(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
              BlockOrcaAcknowledgement: Pattern: ^([ \t]*We gratefully acknowledge.*?\n(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
              BlockOrcaLibint2: Pattern: ^([ \t]*Your calculation uses the libint2.*?\n(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
              BlockOrcaLibXc: Pattern: ^([ \t]*Your ORCA version has been built with support for libXC.*?\n(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
              BlockOrcaUses: Pattern: ^([ \t]*This ORCA versions uses.*?\n(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
          BlueprintHurray:
            RegexBlueprint:
              BlockOrcaHurrayTS: Pattern: ^((?:[ \t]*\*{5,}[ \t]*H[ \t]*U[ \t]*R[ \t]*R[ \t]*A[ \t]*Y[ \t]*\*{5,}\*{5,}[ \t]*\n)(?:[ \t]*\*+[ \t]*THE TS OPTIMIZATION HAS CONVERGED[ \t]*\*+[ \t]*\n)(?:[ \t]*\*{5,}\n))
              BlockOrcaHurrayCI: Pattern: ^((?:[ \t]*\*{5,}[ \t]*H[ \t]*U[ \t]*R[ \t]*R[ \t]*A[ \t]*Y[ \t]*\*{5,}\*{5,}[ \t]*\n)(?:[ \t]*\*+[ \t]*THE N[Ee][Bb] OPTIMIZATION HAS CONVERGED[ \t]*\*+[ \t]*\n)(?:[ \t]*\*{5,}\n))
              BlockOrcaHurrayOptimization: Pattern: ^((?:[ \t]*\*{5,}[ \t]*H[ \t]*U[ \t]*R[ \t]*R[ \t]*A[ \t]*Y[ \t]*\*{5,}\*{5,}[ \t]*\n)(?:[ \t]*\*+[ \t]*THE OPTIMIZATION HAS CONVERGED[ \t]*\*+[ \t]*\n)(?:[ \t]*\*{5,}\n))
          BlueprintBlockWithSingeLineHeader:
            RegexBlueprint:
              BlockOrcaRotationalSpectrum: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*Rotational spectrum[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
              BlockOrcaOrbitalEnergies: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*ORBITAL ENERGIES[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
              BlockOrcaTotalScfEnergy: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*TOTAL SCF ENERGY[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
              BlockOrcaTddftExcitedStatesSinglets: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*TD-DFT EXCITED STATES \(SINGLETS\)[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
              BlockOrcaTddftTdaExcitedStates: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*TD-DFT\/TDA EXCITED STATES[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
              BlockOrcaPathSummaryForNebTs: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*PATH SUMMARY FOR N[Ee][Bb]-TS[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
              BlockOrcaPathSummaryForNebCi: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*PATH SUMMARY[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
              BlockOrcaVibrationalFrequencies: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*VIBRATIONAL FREQUENCIES[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
          BlueprintBlockWithSingeLineHeaderAndSubheader:
            RegexBlueprint:
              BlockOrcaAbsorptionSpectrumViaTransitionElectricDipoleMoments: Pattern: ^((?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:[ \t]*ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS[ \t]*\n)(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n){1,2}(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)+)
              BlockOrcaAbsorptionSpectrumViaTransitionVelocityDipoleMoments: Pattern: ^((?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:[ \t]*ABSORPTION SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS[ \t]*\n)(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n){1,2}(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)+)
              BlockOrcaCdSpectrumViaTransitionElectricDipoleMoments: Pattern: ^((?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:[ \t]*CD SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS[ \t]*\n)(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n){1,2}(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)+)
              BlockOrcaCdSpectrumViaTransitionVelocityDipoleMoments: Pattern: ^((?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:[ \t]*CD SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS[ \t]*\n)(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n){1,2}(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)+)
              BlockOrcaCdSpectrum: Pattern: ^((?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:[ \t]*CD SPECTRUM[ \t]*\n)(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n){1,2}(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)+)
          BlueprintBlockWithInlineHeader:
            RegexBlueprint:
              BlockOrcaOrbitalBasis: Pattern: ^((?:^[ \t]*([\-\*\#\=]+)[ \t]*Orbital basis set information[ \t]*\2[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
              BlockOrcaAuxJBasis: Pattern: ^((?:^[ \t]*([\-\*\#\=]+)[ \t]*AuxJ basis set information[ \t]*\2[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
          BlueprintBlockNote:
            RegexBlueprint:
              BlockOrcaAllRightsReserved: Pattern: ^((?:[ \t]*(([\-\*\#\=]){5,})[ \t]*\n)(?:^[ \t]*\3(?!\3).*\3[ \t]*\n)*?(^[ \t]*\3[ \t]*All rights reserved[ \t]*\3[ \t]*\n)(?:^[ \t]*\3(?!\3).*\3[ \t]*\n)*?(?:[ \t]*\2[ \t]*\n))
          BlueprintBlockSCF:
            RegexBlueprint:
              BlockOrcaScf: Pattern: ^((?:(?:[ \t]*([\-\*\#\=]){5,})[ \t]*S-C-F[ \t]*\2{7,}\n)(?:(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n){1,2}(?:\2*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
              BlockOrcaSoscf: Pattern: ^((?:(?:[ \t]*([\-\*\#\=]){5,})[ \t]*S-O-S-C-F[ \t]*\2{7,}\n)(?:(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n){1,2}(?:\2*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
          BlockOrcaScfConverged: RegexRequest(p_type='Block', p_subtype='BlockOrcaScfConverged', pattern='^((?:[ \t]*\*{5,}[ \t]...', flags=re.MULTILINE, comment='Note, but with CF CONV...')
          BlockOrcaTimingsForIndividualModules: RegexRequest(p_type='Block', p_subtype='BlockOrcaTimingsForIndividualModules', pattern='^((?:[ \t]*Timings for...', flags=re.MULTILINE, comment='Timings for individual...')
          BlockOrcaCiNebConvergence: RegexRequest(p_type='Block', p_subtype='BlockOrcaCiNebConvergence', pattern='^((?:[ \t]*\.\-{5,}\.[...', flags=re.MULTILINE, comment='CI-Neb convergence blo...')
          BlockOrcaIcon: RegexRequest(p_type='Block', p_subtype='BlockOrcaIcon', pattern='^((?:^[ \t]*#,[ \t]*\n...', flags=re.MULTILINE, comment='Unsafe as can ignore t...')
      TypeDefaultBlocks:
        RegexGroup:
          BlockOrcaUnrecognizedScf: RegexRequest(p_type='Block', p_subtype='BlockOrcaUnrecognizedScf', pattern='^((?:(?:[ \t]*([\-\*\#...', flags=re.MULTILINE, comment='SCF type of block: the...')
          BlockOrcaUnrecognizedHurray: RegexRequest(p_type='Block', p_subtype='BlockOrcaUnrecognizedHurray', pattern='((?:[ \t]*\*{5,}[ \t]*...', flags=re.MULTILINE, comment='Hurray type of block: ...')
          BlockOrcaUnrecognizedWithSingeLineHeaderAndSubheader: RegexRequest(p_type='Block', p_subtype='BlockOrcaUnrecognizedWithSingeLineHeaderAndSubheader', pattern='^((?:[ \t]*[\-\*\#\=]{...', flags=re.MULTILINE, comment='Block starts with a li...')
          BlockOrcaUnrecognizedWithSingeLineHeader: RegexRequest(p_type='Block', p_subtype='BlockOrcaUnrecognizedWithSingeLineHeader', pattern='^((?:^[ \t]*[\-\*\#\=]...', flags=re.MULTILINE, comment='Block starts with a li...')
          BlockOrcaUnrecognizedWithHeader: RegexRequest(p_type='Block', p_subtype='BlockOrcaUnrecognizedWithHeader', pattern='(([ \t]*[\-\*\#\=]{5,}...', flags=re.MULTILINE, comment='Special, from 1 to 3 n...')
      Spacer: RegexRequest(p_type='Spacer', p_subtype='Spacer', pattern='^(\s*\n)', flags=re.MULTILINE, comment='Just some empty lines,...')
    


You can create the new instance of `RegexSettings`, `RegexBlueprint` or `RegexRequest` and add it with .add_item.

`TypeKnownBlocks` is made for specific patterns for known blocks

`TypeDefaultBlocks` is made for the general patters to find some specific kinds of blocks, data extraction is not expected from the blocks in this section

`BlockOrcaUnknown` is the `RegexRequest` to collect everything that was not recognized before as a block and is not just a space

`Spacer` collects the spaces left in the document


```python
pattern = chp.regex_request.RegexRequest(
    p_type="Block",
    p_subtype="BlockOrcaDemonstration",
    pattern="^(aaa)$",
    flags=["MULTILINE"],
    comment=
    "Patterns should always start with ^, have at least 1 capturing group and end with $",
)
pattern
```




    RegexRequest(p_type='Block', p_subtype='BlockOrcaDemonstration', pattern='^(aaa)$', flags=re.MULTILINE, comment='Patterns should always...')



Patterns should always start with `^`, have at least 1 capturing group and end with `$`. This capturing group will capture the `raw_data`


```python
rs.items["TypeKnownBlocks"].add_item(
    name="BlockOrcaDemonstration", item=pattern)
```

Pattern was successfully added:


```python
print(rs)
```

    RegexGroup:
      TypeKnownBlocks:
        RegexGroup:
          BlockOrcaTotalRunTime: RegexRequest(p_type='Block', p_subtype='BlockOrcaTotalRunTime', pattern='^([ \t]*TOTAL RUN TIME...', flags=re.MULTILINE, comment='This pattern captures ...')
          BlockOrcaTerminatedNormally: RegexRequest(p_type='Block', p_subtype='BlockOrcaTerminatedNormally', pattern='^([ \t]*\*{4}ORCA TERM...', flags=re.MULTILINE, comment='This pattern captures ...')
          BlockOrcaFinalSinglePointEnergy: RegexRequest(p_type='Block', p_subtype='BlockOrcaFinalSinglePointEnergy', pattern='^((-{20,}\s+-{15,}\n)[...', flags=re.MULTILINE, comment='This pattern matches t...')
          BlockOrcaGeometryConvergence: RegexRequest(p_type='Block', p_subtype='BlockOrcaGeometryConvergence', pattern='((?:[ \t]*\.-{5,}\.[ \...', flags=re.MULTILINE, comment='Orca Geometry converge...')
          BlockOrcaDipoleMomentFromOrca6: RegexRequest(p_type='Block', p_subtype='BlockOrcaDipoleMoment', pattern='^(([ \t]*-{10,}[ \t]*\...', flags=re.MULTILINE, comment='Equal signs around the...')
          BlockOrcaDipoleMoment: RegexRequest(p_type='Block', p_subtype='BlockOrcaDipoleMoment', pattern='^(([ \t]*-{10,}[ \t]*\...', flags=re.MULTILINE, comment='Equal signs around the...')
          BlockOrcaInputFile: RegexRequest(p_type='Block', p_subtype='BlockOrcaInputFile', pattern='^((?:[ \t]*={10,}[ \t]...', flags=re.MULTILINE, comment='Equal signs around the...')
          BlockOrcaErrorMessage: RegexRequest(p_type='Block', p_subtype='BlockOrcaErrorMessage', pattern='^((?:[ \t]*[\-\*\#\=]{...', flags=re.MULTILINE, comment='Block with error messa...')
          BlockOrcaShark: RegexRequest(p_type='Block', p_subtype='BlockOrcaShark', pattern='^((?:[ \t]*-{50,}[ \t]...', flags=re.MULTILINE, comment='Starts with line of  -...')
          BlockOrcaWarnings: RegexRequest(p_type='Block', p_subtype='BlockOrcaWarnings', pattern='^((?:[ \t]*\={5,}[ \t]...', flags=re.MULTILINE, comment='WARNINGS, should captu...')
          BlueprintParagraphStartsWith:
            RegexBlueprint:
              BlockOrcaVersion: Pattern: ^([ \t]*Program Version.*?\n(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
              BlockOrcaContributions: Pattern: ^([ \t]*With contributions from.*?\n(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
              BlockOrcaAcknowledgement: Pattern: ^([ \t]*We gratefully acknowledge.*?\n(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
              BlockOrcaLibint2: Pattern: ^([ \t]*Your calculation uses the libint2.*?\n(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
              BlockOrcaLibXc: Pattern: ^([ \t]*Your ORCA version has been built with support for libXC.*?\n(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
              BlockOrcaUses: Pattern: ^([ \t]*This ORCA versions uses.*?\n(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
          BlueprintHurray:
            RegexBlueprint:
              BlockOrcaHurrayTS: Pattern: ^((?:[ \t]*\*{5,}[ \t]*H[ \t]*U[ \t]*R[ \t]*R[ \t]*A[ \t]*Y[ \t]*\*{5,}\*{5,}[ \t]*\n)(?:[ \t]*\*+[ \t]*THE TS OPTIMIZATION HAS CONVERGED[ \t]*\*+[ \t]*\n)(?:[ \t]*\*{5,}\n))
              BlockOrcaHurrayCI: Pattern: ^((?:[ \t]*\*{5,}[ \t]*H[ \t]*U[ \t]*R[ \t]*R[ \t]*A[ \t]*Y[ \t]*\*{5,}\*{5,}[ \t]*\n)(?:[ \t]*\*+[ \t]*THE N[Ee][Bb] OPTIMIZATION HAS CONVERGED[ \t]*\*+[ \t]*\n)(?:[ \t]*\*{5,}\n))
              BlockOrcaHurrayOptimization: Pattern: ^((?:[ \t]*\*{5,}[ \t]*H[ \t]*U[ \t]*R[ \t]*R[ \t]*A[ \t]*Y[ \t]*\*{5,}\*{5,}[ \t]*\n)(?:[ \t]*\*+[ \t]*THE OPTIMIZATION HAS CONVERGED[ \t]*\*+[ \t]*\n)(?:[ \t]*\*{5,}\n))
          BlueprintBlockWithSingeLineHeader:
            RegexBlueprint:
              BlockOrcaRotationalSpectrum: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*Rotational spectrum[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
              BlockOrcaOrbitalEnergies: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*ORBITAL ENERGIES[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
              BlockOrcaTotalScfEnergy: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*TOTAL SCF ENERGY[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
              BlockOrcaTddftExcitedStatesSinglets: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*TD-DFT EXCITED STATES \(SINGLETS\)[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
              BlockOrcaTddftTdaExcitedStates: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*TD-DFT\/TDA EXCITED STATES[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
              BlockOrcaPathSummaryForNebTs: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*PATH SUMMARY FOR N[Ee][Bb]-TS[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
              BlockOrcaPathSummaryForNebCi: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*PATH SUMMARY[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
              BlockOrcaVibrationalFrequencies: Pattern: ^((?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:[ \t]*VIBRATIONAL FREQUENCIES[ \t]*\n)(?:^[ \t]*[\-\*\#\=]{5,}.*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*)
          BlueprintBlockWithSingeLineHeaderAndSubheader:
            RegexBlueprint:
              BlockOrcaAbsorptionSpectrumViaTransitionElectricDipoleMoments: Pattern: ^((?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:[ \t]*ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS[ \t]*\n)(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n){1,2}(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)+)
              BlockOrcaAbsorptionSpectrumViaTransitionVelocityDipoleMoments: Pattern: ^((?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:[ \t]*ABSORPTION SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS[ \t]*\n)(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n){1,2}(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)+)
              BlockOrcaCdSpectrumViaTransitionElectricDipoleMoments: Pattern: ^((?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:[ \t]*CD SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS[ \t]*\n)(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n){1,2}(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)+)
              BlockOrcaCdSpectrumViaTransitionVelocityDipoleMoments: Pattern: ^((?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:[ \t]*CD SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS[ \t]*\n)(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n){1,2}(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)+)
              BlockOrcaCdSpectrum: Pattern: ^((?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:[ \t]*CD SPECTRUM[ \t]*\n)(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n){1,2}(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)+)
          BlueprintBlockWithInlineHeader:
            RegexBlueprint:
              BlockOrcaOrbitalBasis: Pattern: ^((?:^[ \t]*([\-\*\#\=]+)[ \t]*Orbital basis set information[ \t]*\2[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
              BlockOrcaAuxJBasis: Pattern: ^((?:^[ \t]*([\-\*\#\=]+)[ \t]*AuxJ basis set information[ \t]*\2[ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
          BlueprintBlockNote:
            RegexBlueprint:
              BlockOrcaAllRightsReserved: Pattern: ^((?:[ \t]*(([\-\*\#\=]){5,})[ \t]*\n)(?:^[ \t]*\3(?!\3).*\3[ \t]*\n)*?(^[ \t]*\3[ \t]*All rights reserved[ \t]*\3[ \t]*\n)(?:^[ \t]*\3(?!\3).*\3[ \t]*\n)*?(?:[ \t]*\2[ \t]*\n))
          BlueprintBlockSCF:
            RegexBlueprint:
              BlockOrcaScf: Pattern: ^((?:(?:[ \t]*([\-\*\#\=]){5,})[ \t]*S-C-F[ \t]*\2{7,}\n)(?:(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n){1,2}(?:\2*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
              BlockOrcaSoscf: Pattern: ^((?:(?:[ \t]*([\-\*\#\=]){5,})[ \t]*S-O-S-C-F[ \t]*\2{7,}\n)(?:(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n){1,2}(?:\2*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n)*)
          BlockOrcaScfConverged: RegexRequest(p_type='Block', p_subtype='BlockOrcaScfConverged', pattern='^((?:[ \t]*\*{5,}[ \t]...', flags=re.MULTILINE, comment='Note, but with CF CONV...')
          BlockOrcaTimingsForIndividualModules: RegexRequest(p_type='Block', p_subtype='BlockOrcaTimingsForIndividualModules', pattern='^((?:[ \t]*Timings for...', flags=re.MULTILINE, comment='Timings for individual...')
          BlockOrcaCiNebConvergence: RegexRequest(p_type='Block', p_subtype='BlockOrcaCiNebConvergence', pattern='^((?:[ \t]*\.\-{5,}\.[...', flags=re.MULTILINE, comment='CI-Neb convergence blo...')
          BlockOrcaIcon: RegexRequest(p_type='Block', p_subtype='BlockOrcaIcon', pattern='^((?:^[ \t]*#,[ \t]*\n...', flags=re.MULTILINE, comment='Unsafe as can ignore t...')
          BlockOrcaDemonstration: RegexRequest(p_type='Block', p_subtype='BlockOrcaDemonstration', pattern='^(aaa)$', flags=re.MULTILINE, comment='Patterns should always...')
      TypeDefaultBlocks:
        RegexGroup:
          BlockOrcaUnrecognizedScf: RegexRequest(p_type='Block', p_subtype='BlockOrcaUnrecognizedScf', pattern='^((?:(?:[ \t]*([\-\*\#...', flags=re.MULTILINE, comment='SCF type of block: the...')
          BlockOrcaUnrecognizedHurray: RegexRequest(p_type='Block', p_subtype='BlockOrcaUnrecognizedHurray', pattern='((?:[ \t]*\*{5,}[ \t]*...', flags=re.MULTILINE, comment='Hurray type of block: ...')
          BlockOrcaUnrecognizedWithSingeLineHeaderAndSubheader: RegexRequest(p_type='Block', p_subtype='BlockOrcaUnrecognizedWithSingeLineHeaderAndSubheader', pattern='^((?:[ \t]*[\-\*\#\=]{...', flags=re.MULTILINE, comment='Block starts with a li...')
          BlockOrcaUnrecognizedWithSingeLineHeader: RegexRequest(p_type='Block', p_subtype='BlockOrcaUnrecognizedWithSingeLineHeader', pattern='^((?:^[ \t]*[\-\*\#\=]...', flags=re.MULTILINE, comment='Block starts with a li...')
          BlockOrcaUnrecognizedWithHeader: RegexRequest(p_type='Block', p_subtype='BlockOrcaUnrecognizedWithHeader', pattern='(([ \t]*[\-\*\#\=]{5,}...', flags=re.MULTILINE, comment='Special, from 1 to 3 n...')
      Spacer: RegexRequest(p_type='Spacer', p_subtype='Spacer', pattern='^(\s*\n)', flags=re.MULTILINE, comment='Just some empty lines,...')
    



```python

```
