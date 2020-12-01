import java.util.Objects;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class Main {

    interface Node {
    }
    static class Column implements Node {
        public final String name;
        Column(String name) {
            this.name = name;
        }
        public String toString() {
            if (parent() != null) {
                return "_" + name;
            }
            return name;
        }
        public String parent() {
            var parts = name.split("\\.");
            if (parts.length > 1) {
                return parts[0];
            }
            return null;
        }
    }
    static class Value implements Node {
        public final Object value;
        Value(Object value) {
            this.value = value;
        }

        public String toString() {
            if (value instanceof String) {
                return "'%s'".formatted(value);
            } else if (value == null) {
                return "NULL";
            }
            return value.toString();
        }
    }
    static class Condition implements Node {
        public final Node left;
        public final String operator;
        public final Node right;

        public Condition(Node column, String operator, Node value) {
            this.left = column;
            this.operator = operator;
            this.right = value;
        }

        public Condition(String column, String operator, int value) {
            this(new Column(column), operator, new Value(value));
        }

        public Condition(String column, String operator, String value) {
            this(new Column(column), operator, new Value(value));
        }

        Condition And(Condition right) {
            return new Condition(this, "AND", right);
        }

        Condition Or(Condition right) {
            return new Condition(this, "OR", right);
        }

        private Stream<String> unnestRecurse(Node node) {
            if (node instanceof Column) {
                return Stream.of(((Column) node).parent());
            } else if (node instanceof Condition) {
                return ((Condition) node).columnsToUnnest();
            }
            return Stream.empty();
        }

        Stream<String> columnsToUnnest() {
            return Stream.concat(unnestRecurse(left), unnestRecurse(right));
        }

        @Override
        public String toString() {
            return "(%s %s %s)".formatted(left, operator, right);
        }
    }

    static class Dataset {
        public final String table;
        public final Condition condition;

        public Dataset(String table, Condition condition) {
            this.table = table;
            this.condition = condition;
        }

        String sql() {
            var fromClause =
                    Stream.concat(Stream.of(table),
                            condition.columnsToUnnest()
                                    .filter(Objects::nonNull)
                                    .distinct()
                                    .map("UNNEST(%1$s) AS _%1$s"::formatted))
                                    .collect(Collectors.joining(", "));

            return "SELECT * FROM %s WHERE %s".formatted(fromClause, condition);
        }
    }

    static final String expected = "SELECT * FROM gdc-bq-sample.gdc_metadata.r26_clinical, UNNEST(demographic) AS _demographic, " +
            "UNNEST(project) AS _project, UNNEST(diagnoses) AS _diagnoses " +
            "WHERE (((_demographic.age_at_index >= 50) AND (_project.project_id = 'TCGA-OV')) AND (_diagnoses.figo_stage = 'Stage IIIC'))";

    public static void main(String[] args) {
        var c1 = new Condition("demographic.age_at_index", ">=", 50);
        var c2 = new Condition("project.project_id", "=", "TCGA-OV");
        var c3 = new Condition("diagnoses.figo_stage", "=", "Stage IIIC");

        var c = c1.And(c2).And(c3);

        var dataset = new Dataset("gdc-bq-sample.gdc_metadata.r26_clinical", c);

        var sql = dataset.sql();
        if (!sql.equals(expected)) {
            System.out.println("incorrect sql" + sql);
        }
    }
}
