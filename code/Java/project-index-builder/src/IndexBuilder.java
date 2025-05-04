import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.InvalidParameterException;

/**
 * Index Builder class - used to add documents and build Lucene index
 */
public class IndexBuilder {
    private final Path index_path;
    private final StandardAnalyzer analyzer;
    private Directory directory;
    private IndexWriter index_writer;

    public static void main(String[] args) {
        int arg_len = args.length;
        if (arg_len < 1) {
            throw new IllegalArgumentException("missing argument: project root");
        }
        if (arg_len < 2) {
            throw new IllegalArgumentException("missing argument: index path");
        }
        System.out.println("Hello, World!");
        Path project_root = Paths.get(args[0]);
        Path index_path = Paths.get(args[1]);
        if (!Files.isDirectory(project_root)){
            throw new InvalidParameterException("project root should be a directory!");
        }
        if (!Files.exists(index_path)) {
            try {
                Files.createDirectories(index_path); 
            }
            catch (IOException e) {
                System.out.println("Failed to create output directory: " + index_path);
                System.out.println(e.getMessage());
                System.exit(1);
            }
        }
        IndexBuilder builder = new IndexBuilder(index_path);
    }

    /**
     * initializes the index builder
     * @param indexPath Path to store the index
     */
    public IndexBuilder(Path index_path) {
        this.index_path = index_path;
        this.analyzer = new StandardAnalyzer();
        // this.directory = FSDirectory.open(index_path);
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        config.setOpenMode(OpenMode.CREATE_OR_APPEND);
        // this.index_writer = new IndexWriter(directory, config);
    }

    /**
     * Add text document to index
     * @param id Unique identifier for the document
     * @param title Document title
     * @param content Document content
     * @throws IOException If an error occurs while adding the document
     */
    public void addDocument(String id, String title, String content) throws IOException {
        Document document = new Document();
        
        // Add non-tokenized field (for exact match)
        document.add(new StringField("id", id, Field.Store.YES));
        
        // Add tokenized field (for full-text search)
        document.add(new TextField("title", title, Field.Store.YES));
        document.add(new TextField("content", content, Field.Store.YES));
        
        index_writer.addDocument(document);
    }
    
    /**
     * Add file to index
     * @param id Unique identifier for the document
     * @param title Document title
     * @param file File to be indexed
     * @throws IOException If an error occurs while adding the file
     */
    public void addFile(String id, String title, File file) throws IOException {
        Document document = new Document();
        
        document.add(new StringField("id", id, Field.Store.YES));
        document.add(new TextField("title", title, Field.Store.YES));
        document.add(new TextField("filename", file.getName(), Field.Store.YES));
        document.add(new TextField("filepath", file.getCanonicalPath(), Field.Store.YES));
        
        // Add file content
        document.add(new TextField("content", new FileReader(file)));
        
        index_writer.addDocument(document);
    }
    
    /**
     * Commit changes and close the index writer
     * @throws IOException If an error occurs during commit
     */
    public void commit() throws IOException {
        index_writer.commit();
    }
    
    /**
     * Close the index writer and directory
     * @throws IOException If an error occurs during closing
     */
    public void close() throws IOException {
        if (index_writer != null) {
            index_writer.close();
        }
        if (directory != null) {
            directory.close();
        }
    }
    
    /**
     * Get the number of indexed documents
     * @return Number of documents in the index
     */
    public int getDocumentCount() {
        return index_writer.getDocStats().numDocs;
    }
}