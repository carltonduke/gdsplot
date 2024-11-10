from plotly import exceptions, optional_imports
from plotly.graph_objs import graph_objs

import gdstk
import shapely.geometry as sg
import shapely
import distinctipy
from typing import *
from os.path import isfile, splitext


file_types_allowed = [
            ".gds",
            ".gds2",
            ".oas"
        ]


class FileExtensionError(Exception):
    """Exception raised for unsupported layout file extensions.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = f"""
                File Extension ({message}) not supported.
                Must be of type:
                    {file_types_allowed}
            """
        super().__init__(self.message)


def create_gdsplot(file_path: str, 
                   show_layers: bool = True, 
                   show_layers_legend: bool = True) -> graph_objs.Figure:
    """Create gdsplot. Pass path to layout file. 
        show_layers = False to disable coloring by layer.datatypes available in layout file
        show_layers_legend = False to hide layer based legend, requires show_layers

        File types allowed: .gds, .gds2, .oas
    """
    return _Gdsplot(
        file_path=file_path,
        show_layers=show_layers,
        show_layer_legend=show_layers_legend
    ).make_plot()


class _Gdsplot(object):


    def __init__(
        self,
        file_path: str,
        show_layers: bool = True,
        show_layer_legend: bool = True,
    ):
        if not isfile(file_path):
            raise FileNotFoundError(file_path)
        else:
            self.file_path = file_path

        if show_layers:
            self.show_layers = True
        else:
            self.show_layers = False

        if show_layer_legend:
            self.show_layers_legend = True
        else:
            self.show_layers_legend = False

        self.file_types_allowed = file_types_allowed


    def read_file(self) -> gdstk.Library:
        """read layout file with gdstk and return library 
        """
        file_ext = splitext(self.file_path)[-1]
        if file_ext not in self.file_types_allowed:
            raise FileExtensionError(file_ext)
        
        gds_ext = [".gds", ".gds2"]
        oas_ext = [".oas"]

        library = gdstk.Library("lib")
        if file_ext in gds_ext:
            library = gdstk.read_gds(self.file_path)
        if file_ext in oas_ext:
            library = gdstk.read_oas(self.file_path)

        return library
    

    def make_plot(self) -> graph_objs.Figure:
        """_summary_
        """
        lib = self.read_file()

        polygons = []
        for c in lib.cells:
            for p in c.get_polygons():
                polygons.append(p)

        if self.show_layers or self.show_layers_legend:
            layer_names = set()
            for pol in polygons:
                layer_dtype = f"{pol.layer}.{pol.datatype}"
                layer_names.add(layer_dtype)

            colors = distinctipy.get_colors(len(layer_names))
            colors_alpha = [ tuple(list(c) + [1]) for c in colors ]
            colors_final = [ f"rgba{c}" for c in colors_alpha ]

            layer_color_map = dict(zip(list(layer_names), colors_final))

            layers_legend_map = set()

        data = []
        for p in polygons:
            x, y = [], []
            for point in p.points:
                x.append(float(point[0]))
                y.append(float(point[1]))
        
            legend = False
            if self.show_layers_legend:
                if color not in layers_legend_map:
                    layers_legend_map.add(color)
                    legend = True

            layer_datatype = None
            if self.show_layer or self.show_layers_legend:
                layer_datatype = f"{p.layer}.{p.datatype}"
            else:
                color = None    
            
            fillcolor = None
            if self.show_layers:
                fillcolor = layer_color_map[layer_datatype]

            data.append(
                graph_objs.Scatter(
                        name="",
                        x=x, 
                        y=y, 
                        fill="toself",
                        mode="lines",
                        fillcolor=fillcolor,
                        legendgroup=layer_datatype,
                        legendgrouptitle={"text":layer_datatype},
                        showlegend=legend,
                        legend="legend1"
                    )
            )

        layout = graph_objs.Layout(
            title=dict(text="gdsplot"),
            clickmode=None, 
            boxmode="group",
            dragmode="pan",
            showlegend=True,
            height=1000,
            width=1000,
            legend={"visible":True}
        )

        return graph_objs.Figure(data=data, layout=layout)
        

if __name__ == "__main__":
    f = create_gdsplot(
        file_path="./test_data/nand2.oas"
    )
    
    