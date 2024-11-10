# gdsplot
Turn a GDS or OAS file into a Plotly figure.

![image](https://github.com/user-attachments/assets/08d173c3-93c1-4b93-bbfb-0645147982cf)


## usage
```python
from _gdsplot import create_gdsplot

fig = create_gdsplot(
    file_path=file_path,
    show_layers=True,
    show_layers_legend=True
)
```

## supported file types
- .oas
- .gds
- .gds2

## example gds files
https://www.yzuda.org/download/_GDSII_examples.html

