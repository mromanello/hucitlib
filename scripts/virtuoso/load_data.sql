
-- Disable auto indexing before doing bulk insertions / deletions

-- Deleting previous entries of loader script
delete from DB.DBA.load_list;

-- see http://www.openlinksw.com/dataspace/dav/wiki/Main/VirtBulkRDFLoader
select 'Loading data...';
-- load data directly from main branch of the github repo
DB.DBA.TTLP_MT (http_get('https://raw.githubusercontent.com/mromanello/hucit_kb/master/knowledge_base/data/kb/hucit_000001.ttl'), '', 'http://purl.org/hucit/kb');
DB.DBA.RDF_LOAD_RDFXML (http_get('http://erlangen-crm.org/170309/'), '', 'http://erlangen-crm.org/170309/');
DB.DBA.RDF_LOAD_RDFXML (http_get('http://erlangen-crm.org/efrbroo/'), '', 'http://erlangen-crm.org/efrbroo/');

rdf_loader_run();

grant SPARQL_UPDATE to "SPARQL";

-- See if we have any errors
select * from DB.DBA.load_list where ll_state <> 2;
