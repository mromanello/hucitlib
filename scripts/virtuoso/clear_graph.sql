select 'Clearing existing data...';
-- Add here all the graphs we use for a clean update (RDF_GLOBAL_RESET deletes them all)
SPARQL CLEAR GRAPH <http://128.178.21.39:8080/matteo-data>;

SPARQL CLEAR GRAPH <http://purl.org/hucit/kb>;


