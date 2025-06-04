package infostructure;

public class FieldInfo extends VariableInfo {
    int start_line;
    int end_line;
    public FieldInfo(String name, String type, int[] position) {
        super(name, type);
        this.start_line = position[0];
        this.end_line = position[1];
    }
}
