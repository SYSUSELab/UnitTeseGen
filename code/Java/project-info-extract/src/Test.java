import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class Test {
    public static void main(String[] args) throws Exception {
        System.out.println("Class test, args:");
        for (int i = 0; i < args.length; i++) {
            System.out.println(args[i]);
        }
        // Path java_file =
        // Paths.get("../../dataset/puts/commons-csv/src/main/java/org/apache/commons/csv/CSVFormat.java");
        // CodeInfoExtractor codeInfoExtractor = new CodeInfoExtractor();
        // JsonObject info = codeInfoExtractor.extractCodeInfo(java_file);
        // Gson gson = new
        // GsonBuilder().setPrettyPrinting().disableHtmlEscaping().create();
        // String json = gson.toJson(info);
        // Path outputPath = Paths.get("./test.json");
        // Files.writeString(outputPath, json);

        String source_dir = "../../dataset/puts";
        String output_dir = "../../dataset/puts_json";
        String[] arg = new String[] { source_dir, output_dir };
        PreProcessor.main(arg);
    }
}
