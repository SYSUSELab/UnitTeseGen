package infostructure;

public class EnumConstantInfo {
    String constant_name;
    int start_line;
    int end_line;
    public EnumConstantInfo(String constant_name, int position[]) {
        this.constant_name = constant_name;
        this.start_line = position[0];
    }
}
