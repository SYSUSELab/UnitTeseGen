package infostructure;

import java.util.List;

public class CallMethodInfo {
    String method_name;
    VariableInfo[] arguments;

    public CallMethodInfo(String method_name, List<VariableInfo> arguments) {
        this.method_name = method_name;
        this.arguments = arguments.toArray(new VariableInfo[0]);
    }
}
