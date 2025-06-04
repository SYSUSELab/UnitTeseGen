package infostructure;

public class VariableInfo {
    public String name;
    public String type;
    public VariableInfo(String variableName, String vairableType) {
        this.name = variableName;
        this.type = vairableType;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        VariableInfo that = (VariableInfo) obj;
        return name.equals(that.name) && 
            type.equals(that.type);
    }

    @Override
    public int hashCode() {
        return (name+type).hashCode();
    }
}
