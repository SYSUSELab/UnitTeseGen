import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.type.Type;
import com.github.javaparser.ast.ImportDeclaration;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.Expression;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.resolution.TypeSolver;
import com.github.javaparser.resolution.declarations.ResolvedMethodDeclaration;
import com.github.javaparser.resolution.types.ResolvedType;
import com.github.javaparser.symbolsolver.JavaSymbolSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.CombinedTypeSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.ReflectionTypeSolver;

import infostructure.CallMethodInfo;
import infostructure.VariableInfo;

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
            imports.add(imp_node.toString().trim());
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

    protected CallMethodInfo resolveQualifiedName(MethodCallExpr method_call) {
        String qualified_name = method_call.getNameAsString();;
        List <VariableInfo> args = new ArrayList<VariableInfo>();
        String return_type = "unresolved";
        ResolvedMethodDeclaration rsv_method = null;
        NodeList<Expression> arguments = method_call.getArguments();
        int arg_count = arguments.size();
        try {
            rsv_method = method_call.resolve();
            qualified_name = rsv_method.getQualifiedSignature();
            return_type = rsv_method.getReturnType().describe();
            int rsv_arg_count = rsv_method.getNumberOfParams();
            for (int i = 0; i < arg_count; i++) {
                String arg_type;
                if (i >= rsv_arg_count) {
                    arg_type = rsv_method.getParam(rsv_arg_count-1).describeType();
                }
                else{
                    arg_type = rsv_method.getParam(i).describeType();
                }
                String arg_name = arguments.get(i).toString();
                VariableInfo arg_info = new VariableInfo(arg_name, arg_type);
                args.add(arg_info);
            }
        } catch (Exception e) {
            for (int i = 0; i < arg_count; i++) {
                String arg_type = "unresolved";
                String arg_name = arguments.get(i).toString();
                VariableInfo arg_info = new VariableInfo(arg_name, arg_type); 
                args.add(arg_info);
            }
            System.out.println("Error: " + e.getMessage());
        }
        CallMethodInfo method_call_info = new CallMethodInfo(qualified_name, args, return_type);
        return method_call_info;
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
