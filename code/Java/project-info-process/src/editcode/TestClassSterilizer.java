package editcode;

import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import spoon.Launcher;
import spoon.reflect.CtModel;
import spoon.reflect.declaration.CtClass;
import spoon.reflect.declaration.CtField;
import spoon.reflect.declaration.CtMethod;
import spoon.reflect.declaration.CtType;
import spoon.reflect.visitor.Filter;

public class TestClassSterilizer {
    public static String main(String[] args){
        if (args.length < 2) {
            throw new IllegalArgumentException("Usage: TestClassSterilizer <original code> <operation>");
        }
        String originalCode = args[0];
        String operation = args[1];

        TestClassSterilizer testClassSterilizer = new TestClassSterilizer();
        switch (operation) {
            case "inner_class":
                return testClassSterilizer.removeRedundantInnerClass(originalCode);
            default:
                throw new IllegalArgumentException("Invalid operation: " + operation);
        }
    }

    Launcher launcher;
    CtModel model;

    public TestClassSterilizer() {
        launcher = new Launcher();
    }

    public String removeRedundantInnerClass(String code) {
        launcher.addInputResource(code);
        launcher.buildModel();
        model = launcher.getModel();

        CtClass<?>[] classDeclarations = getClassDeclaration();
        CtClass<?> root_class = classDeclarations[0];
        String root_class_name = root_class.getSimpleName();
        HashMap<String, CtClass<?>> merged_classes = new HashMap<>();
        merged_classes.put(root_class_name, root_class);
        for (CtClass<?> inner: getNestedClass(root_class)) {
            String class_name = inner.getSimpleName();
            if (!merged_classes.containsKey(class_name)) {
                merged_classes.put(class_name, inner);
            } else {
                mergeInnerClass(merged_classes.get(class_name), inner);
                root_class.removeNestedType(inner);
            }
        }
        
        return code;
    }

    protected CtClass<?>[] getClassDeclaration() {
        List<CtClass<?>> class_decs =  model.getElements((Filter<CtClass<?>>) element -> true);
        if (class_decs.isEmpty()) return new CtClass<?>[] {null};
        class_decs.sort(Comparator.comparingInt(a -> a.getPosition().getLine()));
        return class_decs.toArray(new CtClass<?>[0]);
    }

    protected CtType<?>[] getNestedClass(CtClass<?> root_class) {
        return root_class.getNestedTypes().toArray(new CtType<?>[0]);
    }

    protected void mergeInnerClass(CtClass<?> target, CtClass<?> source) {
        mergeFields(target, source);
        mergeMethods(target, source);
        Set<CtType<?>> nestedTypes = source.getNestedTypes();
        if (source.getNestedTypes().size() > 0) {
            Set<CtType<?>> target_nested = target.getNestedTypes();
            
            for (CtType<?> inner: target_nested) {
                
            }
        }
    }


    protected void mergeFields(CtClass<?> target, CtClass<?> source) {
        HashSet<String> fieldNames = new HashSet<String>();
        for (CtField<?> field : target.getFields()) {
            fieldNames.add(field.getSimpleName());
        }
        for (CtField<?> field : source.getFields()) {
            if (!fieldNames.contains(field.getSimpleName())) {
                fieldNames.add(field.getSimpleName());
                target.addField(field);
            }
        }
    }

    protected void mergeMethods(CtClass<?> target, CtClass<?> source) {
        HashSet<String> methodNames = new HashSet<String>();
        for (CtMethod<?> method : target.getMethods()) {
            methodNames.add(method.getSimpleName());
        }
        for (CtMethod<?> method : source.getMethods()) {
            if (!methodNames.contains(method.getSimpleName())) {
                methodNames.add(method.getSimpleName());
                target.addMethod(method);
            } else {
                CtMethod<?> targetMethod = target.getMethod(method.getSimpleName());
                CtMethod<?> sourceMethod = source.getMethod(method.getSimpleName());
                if (sourceMethod.prettyprint().length() > targetMethod.prettyprint().length()) {
                    target.removeMethod(targetMethod);
                    target.addMethod(method);
                }
            }
        }
    }
}
