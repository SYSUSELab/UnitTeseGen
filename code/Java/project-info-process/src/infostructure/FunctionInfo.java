package infostructure;

import java.util.List;

public class FunctionInfo {
    public String signature;
    public VariableInfo[] parameters;
    // public String body;
    public FunctionInfo(String signature, List<VariableInfo> parameters) {
        this.signature = signature;
        this.parameters = parameters.toArray(new VariableInfo[0]);
        // this.body = body;
    }
}
