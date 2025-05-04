import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryparser.classic.MultiFieldQueryParser;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Search Engine class - used to retrieve documents from Lucene index
 */
public class CodeSearcher {
    private final Path indexPath;
    private final StandardAnalyzer analyzer;
    private Directory directory;
    private IndexReader indexReader;
    private IndexSearcher indexSearcher;
    
    /**
     * Initialize the search engine
     * @param indexPath Index path
     * @throws IOException If an error occurs while opening the index
     */
    public CodeSearcher(Path indexPath) throws IOException {
        this.indexPath = indexPath;
        this.analyzer = new StandardAnalyzer();
        this.directory = FSDirectory.open(indexPath);
        this.indexReader = DirectoryReader.open(directory);
        this.indexSearcher = new IndexSearcher(indexReader);
    }
    
    /**
     * Search in a single field
     * @param field Field name to search
     * @param queryString Query string
     * @param maxResults Maximum number of results
     * @return List of matching documents
     * @throws IOException If an error occurs during search
     * @throws ParseException If an error occurs while parsing the query
     */
    public List<Document> searchByField(String field, String queryString, int maxResults) 
            throws IOException, ParseException {
        QueryParser parser = new QueryParser(field, analyzer);
        Query query = parser.parse(queryString);
        return executeSearch(query, maxResults);
    }
    
    /**
     * Search in multiple fields
     * @param fields Array of field names to search
     * @param queryString Query string
     * @param maxResults Maximum number of results
     * @return List of matching documents
     * @throws IOException If an error occurs during search
     * @throws ParseException If an error occurs while parsing the query
     */
    public List<Document> searchByMultipleFields(String[] fields, String queryString, int maxResults) 
            throws IOException, ParseException {
        MultiFieldQueryParser parser = new MultiFieldQueryParser(fields, analyzer);
        Query query = parser.parse(queryString);
        return executeSearch(query, maxResults);
    }
    
    /**
     * Search in multiple fields with specified weights for each field
     * @param fields Array of field names to search
     * @param weights Weights for each field
     * @param queryString Query string
     * @param maxResults Maximum number of results
     * @return List of matching documents
     * @throws IOException If an error occurs during search
     * @throws ParseException If an error occurs while parsing the query
     */
    public List<Document> searchByMultipleFieldsWithWeights(String[] fields, Map<String, Float> weights, 
            String queryString, int maxResults) throws IOException, ParseException {
        MultiFieldQueryParser parser = new MultiFieldQueryParser(fields, analyzer, weights);
        Query query = parser.parse(queryString);
        return executeSearch(query, maxResults);
    }
    
    /**
     * Execute search and return results
     * @param query Query to execute
     * @param maxResults Maximum number of results
     * @return List of matching documents
     * @throws IOException If an error occurs during search
     */
    private List<Document> executeSearch(Query query, int maxResults) throws IOException {
        TopDocs results = indexSearcher.search(query, maxResults);
        ScoreDoc[] hits = results.scoreDocs;
        
        List<Document> documents = new ArrayList<>();
        for (ScoreDoc hit : hits) {
            // Document doc = indexSearcher.doc(hit.doc);
            // documents.add(doc);
        }
        
        return documents;
    }
    
    /**
     * Get detailed information of search results
     * @param query Query to execute
     * @param maxResults Maximum number of results
     * @return List of results containing documents and scores
     * @throws IOException If an error occurs during search
     */
    public List<SearchResult> getDetailedResults(Query query, int maxResults) throws IOException {
        TopDocs results = indexSearcher.search(query, maxResults);
        ScoreDoc[] hits = results.scoreDocs;
        
        List<SearchResult> searchResults = new ArrayList<>();
        for (ScoreDoc hit : hits) {
            // Document doc = indexSearcher.doc(hit.doc);
            // searchResults.add(new SearchResult(doc, hit.score));
        }
        
        return searchResults;
    }
    
    /**
     * Close the index reader and directory
     * @throws IOException If an error occurs during closing
     */
    public void close() throws IOException {
        if (indexReader != null) {
            indexReader.close();
        }
        if (directory != null) {
            directory.close();
        }
    }
    
    /**
     * Get the number of documents in the index
     * @return Number of documents in the index
     */
    public int getDocumentCount() {
        return indexReader.numDocs();
    }
    
    /**
     * Search result class, containing document and relevance score
     */
    public static class SearchResult {
        private final Document document;
        private final float score;
        
        public SearchResult(Document document, float score) {
            this.document = document;
            this.score = score;
        }
        
        public Document getDocument() {
            return document;
        }
        
        public float getScore() {
            return score;
        }
        
        /**
         * Get all fields in the document
         * @return Mapping of field names and values
         */
        public Map<String, String> getAllFields() {
            Map<String, String> fields = new HashMap<>();
            for (String fieldName : document.getFields().stream().map(f -> f.name()).distinct().toArray(String[]::new)) {
                fields.put(fieldName, document.get(fieldName));
            }
            return fields;
        }
    }
    
    /**
     * Main method example
     */
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Usage: java SearchEngine <index path> <query string>");
            System.exit(1);
        }
        
        Path indexPath = Path.of(args[0]);
        String queryString = args[1];
        
        try {
            CodeSearcher searchEngine = new CodeSearcher(indexPath);
            
            // Search in title and content fields
            String[] fields = {"title", "content"};
            List<Document> results = searchEngine.searchByMultipleFields(fields, queryString, 10);
            
            System.out.println("Found " + results.size() + " matching documents:");
            for (Document doc : results) {
                System.out.println("ID: " + doc.get("id"));
                System.out.println("Title: " + doc.get("title"));
                System.out.println("Filename: " + doc.get("filename"));
                System.out.println("Path: " + doc.get("filepath"));
                System.out.println("-------------------");
            }
            
            searchEngine.close();
            
        } catch (IOException | ParseException e) {
            System.err.println("Error occurred during search: " + e.getMessage());
            e.printStackTrace();
        }
    }
}