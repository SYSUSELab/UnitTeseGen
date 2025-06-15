package editcode;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseStart;
import com.github.javaparser.Provider;
import com.github.javaparser.Providers;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.ImportDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.FieldDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.printer.YamlPrinter;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.Dictionary;
import java.util.HashSet;
import java.util.Hashtable;
import java.util.List;
import java.util.Set;

public class TestClassUpdator {
    JavaParser parser;
    boolean force_update = false;

    public static String main(String[] args) {
        if (args.length < 2) {
            throw new IllegalArgumentException("usage: TestClassEditor <existing_class> <add_class>");
        }
        String existingClass = args[0];
        String addClass = args[1];

        TestClassUpdator editor = new TestClassUpdator();
        if (args.length >= 3) {
            String force = args[2];
            if (force.equals("true"))
                editor.force_update = true;
        }
        String result = editor.mergeTestClasses(existingClass, addClass);
        return result;
    }

    public TestClassUpdator() {
        parser = new JavaParser();
    }

    /**
     * merge test methods from add_class to exist_class
     */
    public String mergeTestClasses(String exist_class, String add_class) {
        try {
            CompilationUnit existCU = parser.parse(exist_class).getResult().orElse(null);
            CompilationUnit addCU = parser.parse(add_class).getResult().orElse(null);
            // get class declaration of exist_class
            ClassOrInterfaceDeclaration existClassDecl = getClassDeclaration(existCU)[0];
            if (existClassDecl == null) {
                System.err.println("can't find class declaration in existing class");
                return add_class;
            }
            // get class declaration of add_class
            if (addCU == null || addCU.getTypes().isEmpty()) { // try to parse incomplete code
                System.err.println("can't parse add code as class");
                return exist_class;
                // addCU = dealInCompeleteCode(add_class);
                // addClassDecl = getClassDeclaration(addCU);
                // if(addClassDecl==null || addClassDecl.getChildNodes().isEmpty()) {
                // System.err.println("can't find method in add class");
                // return exist_class;
                // }
            }
            ClassOrInterfaceDeclaration[] addClassDeclList = getClassDeclaration(addCU);
            ClassOrInterfaceDeclaration addClassDecl = addClassDeclList[0];
            if (addClassDecl == null) {
                System.err.println("can't find class declaration in add class");
                return exist_class;
            }
            // merge imports
            if (force_update) updateImports(existCU, addCU);
            else mergeImports(existCU, addCU);
            // add fields
            addFields(existClassDecl, addClassDecl);
            // add inner classes
            if (addClassDeclList.length > 1) {
                ClassOrInterfaceDeclaration[] innerClasses = new ClassOrInterfaceDeclaration[addClassDeclList.length - 1];
                System.arraycopy(addClassDeclList, 1, innerClasses, 0, addClassDeclList.length - 1);
                addInnerClasses(existClassDecl, innerClasses);
            }
            // add test methods
            addNewTestMethods(existClassDecl, addClassDecl);
            return existCU.toString();
        } catch (Exception e) {
            e.printStackTrace();
            return exist_class;
        }
    }

    /**
     * get class declarations from CompilationUnit
     */
    protected ClassOrInterfaceDeclaration[] getClassDeclaration(CompilationUnit cu) {
        if (cu == null || cu.getTypes().isEmpty()) {
            return new ClassOrInterfaceDeclaration[] {null};
        }
        List<ClassOrInterfaceDeclaration> classes = cu.findAll(ClassOrInterfaceDeclaration.class);
        if (classes.isEmpty()) {
            return new ClassOrInterfaceDeclaration[] {null};
        }
        // sort classes by line number
        classes.sort(Comparator.comparingInt(a -> a.getBegin().map(pos->pos.line).orElse(-1)));
        return classes.toArray(new ClassOrInterfaceDeclaration[0]);
    }

    private CompilationUnit dealInCompeleteCode(String add_code) {
        CompilationUnit addCU = new CompilationUnit();
        ClassOrInterfaceDeclaration addClassDecl = new ClassOrInterfaceDeclaration();
        // get all imports and methods from add_code
        Provider provider = Providers.provider(add_code);

        boolean flag = false;
        do {
            flag = false;
            ImportDeclaration importDecl = parser.parse(ParseStart.IMPORT_DECLARATION, provider).getResult()
                    .orElse(null);
            if (importDecl != null) {
                addCU.addImport(importDecl);
                flag = true;
                String stmt = importDecl.toString();
                add_code = add_code.substring(add_code.indexOf(stmt) + stmt.length());
                provider = Providers.provider(add_code);
            }

            MethodDeclaration methodDecl = parser.parse(ParseStart.METHOD_DECLARATION, provider).getResult()
                    .orElse(null);
            if (methodDecl != null) {
                addClassDecl.addMember(methodDecl.clone());
                flag = true;
                String body = methodDecl.getBody().get().toString();
                add_code = add_code.substring(add_code.indexOf(body) + body.length());
                provider = Providers.provider(add_code);
            }

        } while (flag);
        addClassDecl.setName("TempTestClass");
        addCU.addType(addClassDecl);
        return addCU;
    }

    private void updateImports(CompilationUnit existCU, CompilationUnit addCU) {
        // get all imports from existCU
        Dictionary<String,Boolean> existingImports = new Hashtable<String, Boolean>();
        for (ImportDeclaration importDecl : existCU.getImports()) {
            existingImports.put(importDecl.getNameAsString(), false);
        }
        // add new imports from addCU
        for (ImportDeclaration importDecl : addCU.getImports()) {
            String importName = importDecl.getNameAsString();
            if (existingImports.get(importName) == null) {
                existCU.addImport(importDecl.clone());
            }
            existingImports.put(importName, true);
        }
        // remove unused imports
        List<ImportDeclaration> del_imports = new ArrayList<ImportDeclaration>();
        for (ImportDeclaration importDecl : existCU.getImports()) {
            String importName = importDecl.getNameAsString();
            if (existingImports.get(importName) == false) {
                del_imports.add(importDecl);
            }
        }
        for (ImportDeclaration importDecl : del_imports) {
            existCU.remove(importDecl);
        }
    }

    /**
     * merge imports from two CompilationUnit
     */
    private void mergeImports(CompilationUnit existCU, CompilationUnit addCU) {
        // get all imports from existCU
        Set<String> existingImports = new HashSet<>();
        for (ImportDeclaration importDecl : existCU.getImports()) {
            existingImports.add(importDecl.getNameAsString());
        }
        // add new imports from addCU
        for (ImportDeclaration importDecl : addCU.getImports()) {
            String importName = importDecl.getNameAsString();
            if (!existingImports.contains(importName)) {
                existCU.addImport(importDecl.clone());
            }
        }
    }

    private void addFields(ClassOrInterfaceDeclaration existClassDecl, ClassOrInterfaceDeclaration addClassDecl) {
        // get all fields from addClassDecl
        Set<String> existingFields = new HashSet<>();
        for (FieldDeclaration field : existClassDecl.getFields()) {
            existingFields.add(field.getVariable(0).getNameAsString());
        }
        // add new fields from addClassDecl to existClassDecl
        for (FieldDeclaration field : addClassDecl.getFields()) {
            String fieldName = field.getVariable(0).getNameAsString();
            if (!existingFields.contains(fieldName)) {
                existClassDecl.addMember(field.clone());
            }
        }
    }

    private void addInnerClasses(ClassOrInterfaceDeclaration existClassDecl, 
        ClassOrInterfaceDeclaration[] addClassDeclList) {
        // find exist inner classes
        List<ClassOrInterfaceDeclaration> existingInnerClasses = existClassDecl.findAll(ClassOrInterfaceDeclaration.class);
        Set<String> innerClassesNames = new HashSet<>();
        for (ClassOrInterfaceDeclaration decl: existingInnerClasses){
            innerClassesNames.add(decl.getNameAsString());
        }
        for (ClassOrInterfaceDeclaration addClassDecl : addClassDeclList) {
            String className = addClassDecl.getNameAsString();
            // If the class does not exist in the existing class, add it
            if (!innerClassesNames.contains(className)) {
                // Clone the method to avoid modifying the original AST
                ClassOrInterfaceDeclaration cloneclass = addClassDecl.clone();
                existClassDecl.addMember(cloneclass);
            } else {
                // update inner classes
                ClassOrInterfaceDeclaration existingInnerClass = existingInnerClasses.stream()
                        .filter(decl -> decl.getNameAsString().equals(className))
                        .findFirst()
                        .orElse(null);
                if (existingInnerClass != null) {
                    if (force_update || existingInnerClass.getChildNodes().isEmpty()) {
                        existClassDecl.remove(existingInnerClass);
                        existClassDecl.addMember(addClassDecl.clone());
                    } else { // Compare the length of the method body, and replace if the method body to be
                             // added is longer
                        int exist_length = existingInnerClass.toString().length();
                        int add_length = addClassDecl.toString().length();
                        if (add_length > exist_length) {
                            existClassDecl.remove(existingInnerClass);
                            existClassDecl.addMember(addClassDecl.clone());
                        }
                    }
                }
            }
        }
    }

    private MethodDeclaration getMethodByName(ClassOrInterfaceDeclaration classDecl, String methodName) {
        for (MethodDeclaration method : classDecl.getMethods()) {
            if (method.getNameAsString().equals(methodName)) {
                return method;
            }
        }
        return null;
    }

    /**
     * add new test methods to exist class
     */
    private void addNewTestMethods(ClassOrInterfaceDeclaration existClassDecl,
            ClassOrInterfaceDeclaration addClassDecl) {
        // Get the method names in the existing class for checking duplicates
        Set<String> existingMethodNames = new HashSet<>();
        for (MethodDeclaration method : existClassDecl.getMethods()) {
            existingMethodNames.add(method.getNameAsString());
        }
        // Iterate over all methods in the class to be added
        for (MethodDeclaration method : addClassDecl.getMethods()) {
            String methodName = method.getNameAsString();
            // // Check if the method is a test method
            // if (method.getAnnotationByName("Test").isEmpty()) {
            // continue;
            // }
            // If the method does not exist in the existing class, add it
            if (!existingMethodNames.contains(methodName)) {
                // Clone the method to avoid modifying the original AST
                MethodDeclaration clonedMethod = method.clone();
                existClassDecl.addMember(clonedMethod);
            } else {
                // update method body
                MethodDeclaration existingMethod = getMethodByName(existClassDecl, methodName);
                if (existingMethod!= null) {
                    if (force_update || !existingMethod.getBody().isPresent()) {
                        existingMethod.setBody(method.getBody().get().clone());
                    } else { // Compare the length of the method body, and replace if the method body to be
                             // added is longer
                        int exist_length = existingMethod.getBody().get().toString().length();
                        int add_length = method.getBody().get().toString().length();
                        System.out.println("exist_length: " + exist_length);
                        System.out.println("add_length: " + add_length);
                        if (add_length > exist_length) {
                            existingMethod.setBody(method.getBody().get().clone());
                        }
                    }
                }
            }
        }
    }
    
    public void printAST(CompilationUnit cu) {
        if (cu == null) {
            System.out.println("CompilationUnit is null");
            return;
        }
        String yaml = new YamlPrinter(true).output(cu);
        System.out.println(yaml);
    }
}
