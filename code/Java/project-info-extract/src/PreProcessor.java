import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class PreProcessor {
    public static void main(String[] args) throws IOException{
        Path dataset_root = Paths.get(args[0]);
        Path output_dir = Paths.get(args[1]);
        if (!Files.exists(output_dir)) {
            try {
                Files.createDirectories(output_dir); 
            }
            catch (IOException e) {
                System.out.println("Failed to create output directory: " + output_dir);
                System.out.println(e.getMessage());
                System.exit(1);
            }
            Files.createDirectories(output_dir);
        }
        // process each project in dataset_root
        Gson gson = new GsonBuilder().setPrettyPrinting().disableHtmlEscaping().create();
        Files.list(dataset_root).filter(Files::isDirectory).forEach(project_dir -> {
            String project_name = project_dir.getFileName().toString();
            System.out.println("process project: " + project_name);
            JsonObject datasetJson = processProject(project_name, project_dir);
            String json = gson.toJson(datasetJson);
            
            try{
                Files.writeString(output_dir.resolve(project_name + ".json"), json);
            } catch (IOException e) {
                System.out.println("Error: "+e.getMessage());
            }
        });
    }

    private static JsonObject processProject(String projectName, Path sourceDir){
        JsonObject projectJson = new JsonObject();
        projectJson.addProperty("project", projectName);

        Path source_folder = sourceDir.resolve("src/main/java");
        Path test_folder = sourceDir.resolve("src/test/java");
        Path jar_folder = sourceDir.resolve("libs");

        CodeInfoExtractor codeInfoExtractor = new CodeInfoExtractor();
        try{
            JsonObject[] codeInfo = codeInfoExtractor.processProject(source_folder, test_folder, jar_folder);
            projectJson.add("source", codeInfo[0]);
            projectJson.add("test", codeInfo[1]);
        } catch (IOException e) {
            System.out.println("Error: " + e.getMessage());
        }

        return projectJson;
    }
}
