
-- Disable auto indexing before doing bulk insertions / deletions

-- Deleting previous entries of loader script
delete from DB.DBA.load_list;

-- see http://www.openlinksw.com/dataspace/dav/wiki/Main/VirtBulkRDFLoader
select 'Loading data...';
--      <folder with data>  <pattern>    <default graph if no graph file specified>
--#DB.DBA.TTLP_MT (http_get('https://raw.githubusercontent.com/mromanello/hucit_kb/master/knowledge_base/data/kb/kb-all-in-one.ttl'), '', 'http://128.178.21.39:8080/matteo-data');
ld_dir('/Users/rromanello/Documents/ClassicsCitations/hucit_kb/knowledge_base/data/kb/','kb-all-in-one.ttl','http://purl.org/hucit/kb');

rdf_loader_run();

grant SPARQL_UPDATE to "SPARQL";

-- See if we have any errors
select * from DB.DBA.load_list where ll_state <> 2;
