package infostructure;

import java.util.List;

public class ConstructorInfo extends FunctionInfo {
    int start_line;
    int end_line;
    CallMethodInfo[] call_methods;
    VariableInfo[] external_fields;

    public ConstructorInfo(String sig, 
            List<VariableInfo> params, 
            int[] position,
            CallMethodInfo[] cmethods,
            VariableInfo[] fields) {
        super(sig, params);
        this.start_line = position[0];
        this.end_line = position[1];
        this.call_methods = cmethods;
        this.external_fields = fields;
    }
}
