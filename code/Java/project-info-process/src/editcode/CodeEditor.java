package editcode;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.printer.YamlPrinter;

public class CodeEditor {
    JavaParser parser;
    CompilationUnit exist_cu;
    ClassOrInterfaceDeclaration class_decl;

    public CodeEditor() {
        this.parser = new JavaParser();
    }

    public void ParseClass(String exist_class) {
        this.parser = new JavaParser();
        this.exist_cu = parser.parse(exist_class).getResult().orElse(null);
        if (exist_cu == null || exist_cu.getTypes().isEmpty()) {
            throw new IllegalArgumentException("can't parse code as compelete class");
        }
        class_decl = exist_cu.getTypes().stream()
                .filter(type -> type instanceof ClassOrInterfaceDeclaration)
                .map(type -> (ClassOrInterfaceDeclaration) type)
                .findFirst()
                .orElse(null);
    }

    /**
     * get class declaration
     */
    public ClassOrInterfaceDeclaration getClassDeclaration() {
        return class_decl;
    }

    public void printAST(CompilationUnit cu) {
        if (cu == null) {
            System.out.println("CompilationUnit is null");
            return;
        }
        String yaml = new YamlPrinter(true).output(cu);
        System.out.println(yaml);
    }

    public void addImports(String[] imports) {
        for (String imp : imports) {
            if (imp == null || imp.isEmpty()) {
                continue;
            }
            String name = ""; // imp.split(" ")
            boolean isStatic = imp.indexOf("static") >= 0;
            boolean isAsterisk = imp.endsWith(".*");
            exist_cu.addImport(name, isStatic, isAsterisk);
            // 删除指定的import
            // exist_cu.getImports().removeIf(i -> i.getNameAsString().equals(name));
        }
    }

    /**
     * output the current class as a string
     */
    public String outputCode() {
        if (exist_cu == null)
            return "";
        return exist_cu.toString();
    }
}