package infostructure;

import java.util.List;

public class MethodInfo extends FunctionInfo{
    CallMethodInfo[] call_methods;

    public MethodInfo(String signature, List<VariableInfo> parameters, CallMethodInfo[] call_methods) {
        super(signature, parameters);
        this.call_methods = call_methods;
    }
}
