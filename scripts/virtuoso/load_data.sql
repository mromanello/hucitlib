
-- Disable auto indexing before doing bulk insertions / deletions

-- Deleting previous entries of loader script
delete from DB.DBA.load_list;

-- see http://www.openlinksw.com/dataspace/dav/wiki/Main/VirtBulkRDFLoader
select 'Loading data...';
-- load data directly from main branch of the github repo
DB.DBA.TTLP_MT (http_get('https://raw.githubusercontent.com/mromanello/hucit_kb/master/knowledge_base/data/kb/hucit_000001.ttl'), '', 'http://purl.org/hucit/kb');
--DB.DBA.TTLP_MT (file_to_string_output('/Users/rromanello/Documents/ClassicsCitations/hucit_kb/knowledge_base/data/kb/kb-all-in-one.ttl'), '', 'http://purl.org/hucit/kb');

rdf_loader_run();

grant SPARQL_UPDATE to "SPARQL";

-- See if we have any errors
select * from DB.DBA.load_list where ll_state <> 2;
