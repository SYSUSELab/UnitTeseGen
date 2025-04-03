import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.type.Type;
import com.github.javaparser.ast.ImportDeclaration;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.Expression;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.resolution.TypeSolver;
import com.github.javaparser.resolution.types.ResolvedType;
import com.github.javaparser.symbolsolver.JavaSymbolSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.CombinedTypeSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.ReflectionTypeSolver;

import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class JavaExtractor {
    Path datasetRoot;
    Path outputPath;
    CombinedTypeSolver typeSolver;
    JavaParser parser;

    JavaExtractor() {
        this.setParser();
    }

    private void setParser() {
        typeSolver = new CombinedTypeSolver(new ReflectionTypeSolver());
        JavaSymbolSolver symbolSolver = new JavaSymbolSolver(typeSolver);
        parser = new JavaParser();
        parser.getParserConfiguration().setSymbolResolver(symbolSolver);
        return;
    }

    protected void addTypeSolver(TypeSolver solver) {
        this.typeSolver.add(solver);
        JavaSymbolSolver symbolSolver = new JavaSymbolSolver(typeSolver);
        parser.getParserConfiguration().setSymbolResolver(symbolSolver);
        return;
    }

    protected static boolean isJavaFile(Path file) {
        String fileName = file.getFileName().toString();
        if (fileName.endsWith(".java")) {
            return true;
        }
        // try {
        // String content = Files.readString(file);
        // return content.contains("class ") || content.contains("interface ") ||
        // content.contains("public static void main");
        // } catch (IOException e) {
        // return false;
        // }
        return false;
    }

    protected static boolean isJarFile(Path file) {
        String fileName = file.getFileName().toString();
        if (fileName.endsWith(".jar")) {
            return true;
        }
        return false;
    }

    protected CompilationUnit parseJavaFile(Path javaFile) throws IOException {
        CompilationUnit cu = parser.parse(javaFile).getResult().orElse(null);
        return cu;
    }

    protected List<String> getImports(CompilationUnit cu) {
        // get imports
        List<String> imports = new ArrayList<>();
        for (ImportDeclaration imp_node : cu.getImports()) {
            imports.add(imp_node.getNameAsString());
            // System.out.println(imp_node.getNameAsString());
        }
        return imports;
    }

    protected String extractJavadoc(Node node) {
        final String javadoc;
        if (node instanceof ClassOrInterfaceDeclaration classDecl) {
            javadoc = classDecl.getJavadocComment().map(text -> text.getContent()).orElse(null);
            return javadoc;
        } else if (node instanceof MethodDeclaration methodDecl) {
            javadoc = methodDecl.getJavadocComment().map(text -> text.getContent()).orElse(null);
            return javadoc;
        } else if (node instanceof ConstructorDeclaration consDecl) {
            javadoc = consDecl.getJavadocComment().map(text -> text.getContent()).orElse(null);
            return javadoc;
        }
        return null;
    }

    protected String resolveQualifiedName(MethodCallExpr method_call) {
        String qualified_name = "";
        try {
            qualified_name = method_call.resolve().getQualifiedName();
        } catch (Exception e) {
            qualified_name = method_call.getNameAsString();
            System.out.println("Error: " + e.getMessage());
        }
        return qualified_name;
    }

    protected String resolveType(Expression expr, String simple) {
        String fqn = "";
        try {
            ResolvedType resolvedType = expr.calculateResolvedType();
            fqn = resolvedType.describe();
        } catch (Exception e) {
            fqn = simple;
            System.out.println("Error: " + e.getMessage());
        }
        return fqn;
    }

    protected String resolveType(Type type) {
        String fqn = "";
        try {
            ResolvedType resolvedType = type.resolve();
            fqn = resolvedType.describe();
        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
            fqn = type.toString();
        }
        return fqn;
    }
}
