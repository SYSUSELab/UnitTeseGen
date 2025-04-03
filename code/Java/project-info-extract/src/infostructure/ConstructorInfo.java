package infostructure;

import java.util.List;

public class ConstructorInfo extends FunctionInfo {
    public String body;

    public ConstructorInfo(String signature, List<VariableInfo> parameters, String body) {
        super(signature, parameters);
        this.body = body;
    }
}
