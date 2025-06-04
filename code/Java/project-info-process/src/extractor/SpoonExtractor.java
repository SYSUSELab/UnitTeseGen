package extractor;

import java.util.ArrayList;
import java.util.List;

import spoon.Launcher;
import spoon.reflect.CtModel;
import spoon.reflect.code.CtComment;
import spoon.reflect.declaration.CtClass;
import spoon.reflect.declaration.CtElement;
import spoon.reflect.declaration.CtImport;
import spoon.reflect.declaration.CtMethod;
import spoon.reflect.declaration.CtParameter;
import spoon.reflect.reference.CtTypeReference;
import spoon.reflect.visitor.Filter;

public class SpoonExtractor {
    Launcher launcher;
    CtModel model;
    public SpoonExtractor() {
        this.launcher = new Launcher();
    }
    public SpoonExtractor(String[] sourceDir, String[] classPath) {
        setLauncher(sourceDir, classPath);
    }

    public void setLauncher(String[] sourceDir, String[] classPath) {
        this.launcher = new Launcher();
        if (sourceDir != null) {
            for (String source : sourceDir) {
                launcher.addInputResource(source);
            }
        }
        if (classPath!= null) {
            launcher.getEnvironment().setSourceClasspath(classPath);
        }
        this.launcher.getFactory().getEnvironment().setComplianceLevel(11);
        model = this.launcher.buildModel();
    }

    public CtClass<?> getCtClass(String className) {
        // return launcher.getFactory().Class().get(className);
        return model.getElements((Filter<CtClass<?>>) element -> true)
                    .stream()
                    .filter(c -> c.getQualifiedName().equals(className))
                    .findFirst()
                    .orElse(null);
    }

    public CtMethod<?> getCtMethod(CtClass<?> ctClass, String methodName, String[] argTypes) {
        System.out.println("methodName: "+methodName+" argTypes: "+String.join(" ", argTypes));

        List<CtMethod<?>> methods = ctClass.getMethodsByName(methodName);
        for (CtMethod<?> method : methods) {
            List<CtParameter<?>> methodArgs = method.getParameters();
    
            if (methodArgs.size() == argTypes.length) {
                boolean match = true;
                for (int i = 0; i < argTypes.length; i++) {
                    CtTypeReference<?> argType = methodArgs.get(i).getType();
                    String processed = argTypes[i].replace(".", "$");
                    if (!argType.getQualifiedName().endsWith(processed)) {
                        System.out.println("argType: "+argType.getQualifiedName()+" processed: "+processed);
                        match = false;
                        break;
                    }
                }
                if (match) {
                    return method;
                }
            }
        }
        return null;
    }

    public CtTypeReference<?> createTypeReference(String argType) {
        return launcher.getFactory().Type().createReference(argType);
    }

    public List<CtImport> getImports(CtClass<?> ctClass) {
        return ctClass.getPosition().getCompilationUnit().getImports(); 
    }

    public void removeComment(CtElement ctElement) {
        List<CtComment> comment = new ArrayList<>(ctElement.getComments());
        for (CtComment c : comment) {
            ctElement.removeComment(c);
        }
    }
}
