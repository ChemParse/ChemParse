If you need to handle reasonably large outputs ~ 100MB, it would be faster to extract the particular block you are interested in, instead of creating a markup for the whole document


```python
import pychemparse as chp
```

You can create your own regex or use one from the standard ones (see add_block_example)


```python
regex = (chp.RegexSettings(chp.DEFAULT_ORCA_REGEX_FILE).
         items["TypeKnownBlocks"].items["BlockOrcaFinalSinglePointEnergy"])
regex
```




    RegexRequest(p_type='Block', p_subtype='BlockOrcaFinalSinglePointEnergy', pattern='^((-{20,}\s+-{15,}\n)[...', flags=re.MULTILINE, comment='This pattern matches t...')




```python
with open("example.out", "r") as file:
    long_orca = file.read()
```


```python
processed_text, new_blocks = regex.apply(long_orca, show_progress=True)
```

    Processing BlockOrcaFinalSinglePointEnergy: 100%|█| 626/626 [00:00<00:00, 219902



```python
new_blocks
```




    {8520959472914: {'Element': <pychemparse.orca_elements.BlockOrcaFinalSinglePointEnergy at 0x7bff0c335120>,
      'CharPosition': (354, 500),
      'LinePosition': (18, 21)}}




```python
for v in new_blocks.values():
    block: chp.elements.Block = v["Element"]
    print(block.data()["Energy"])
```

    -440.508559636589 hartree


If you want to work with something that weight more than 1GB and you have the same pattern repeating many times, you might benefit form excluding the creation of `Block` instances at all, working with the pure regex: 


```python
compiled_pattern = regex.compile()
compiled_pattern
```




    re.compile(r'^((-{20,}\s+-{15,}\n)[ \t]*FINAL SINGLE POINT ENERGY[ \t]+-?\d+\.\d+\n\2)',
               re.MULTILINE|re.UNICODE)




```python
for match in compiled_pattern.finditer(long_orca):
    print(match.group(1))
```

    -------------------------   --------------------
    FINAL SINGLE POINT ENERGY      -440.508559636589
    -------------------------   --------------------
    



```python

```
