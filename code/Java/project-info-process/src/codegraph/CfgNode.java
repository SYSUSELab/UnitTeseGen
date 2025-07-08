package codegraph;

import java.util.stream.IntStream;

import fr.inria.controlflow.BranchKind;

public class CfgNode implements Comparable<CfgNode> {
    int id;
    BranchKind kind;
    int[] lines;
    public CfgNode (int id, BranchKind kind, int start, int end) {
        this.id = id;
        this.kind = kind;
        this.lines = IntStream.rangeClosed(start, end).toArray();
    }
    public CfgNode (int id, BranchKind kind) {
        this.id = id;
        this.kind = kind;
        this.lines = new int[] {};
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        CfgNode that = (CfgNode) obj;
        return id == that.id && kind == that.kind;
    }

    @Override
    public int hashCode() {
        return Integer.hashCode(id) + kind.hashCode();
    }

    @Override
    public int compareTo(CfgNode other) {
        return Integer.compare(this.id, other.id);
    }
}
