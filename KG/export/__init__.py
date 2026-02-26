"""Export module for standard formats."""

# Lazy imports to handle missing dependencies gracefully
__all__ = ["RDFExporter", "JSONLDExporter", "GraphMLExporter", "GEXFExporter"]

def __getattr__(name):
    if name == "RDFExporter":
        from icml_exp.KG.export.rdf_exporter import RDFExporter
        return RDFExporter
    elif name == "JSONLDExporter":
        from icml_exp.KG.export.jsonld_exporter import JSONLDExporter
        return JSONLDExporter
    elif name == "GraphMLExporter":
        from icml_exp.KG.export.graphml_exporter import GraphMLExporter
        return GraphMLExporter
    elif name == "GEXFExporter":
        from icml_exp.KG.export.graphml_exporter import GEXFExporter
        return GEXFExporter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
