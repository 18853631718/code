// 测试用例1: 空指针异常
public class NullPointerExceptionTest {
    public static void main(String[] args) {
        String str = null;
        System.out.println(str.length()); // 空指针异常
    }
}

// 测试用例2: SQL注入
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;

public class SQLInjectionTest {
    public static void main(String[] args) throws Exception {
        String userInput = "admin' OR '1'='1";
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/test", "root", "password");
        Statement stmt = conn.createStatement();
        String sql = "SELECT * FROM users WHERE username = '" + userInput + "'";
        stmt.executeQuery(sql); // SQL注入风险
    }
}

// 测试用例3: 内存泄漏
import java.util.ArrayList;
import java.util.List;

public class MemoryLeakTest {
    private static List<Object> list = new ArrayList<>();
    
    public static void main(String[] args) {
        while (true) {
            list.add(new byte[1024 * 1024]); // 内存泄漏
        }
    }
}

// 测试用例4: 竞态条件
public class RaceConditionTest {
    private static int counter = 0;
    
    public static void main(String[] args) {
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                counter++; // 竞态条件
            }
        });
        
        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                counter++; // 竞态条件
            }
        });
        
        t1.start();
        t2.start();
    }
}

// 测试用例5: 安全问题
public class SecurityTest {
    public static void main(String[] args) {
        String password = "secret123"; // 硬编码密码
        System.out.println("Password: " + password); // 打印密码
    }
}

// 测试用例6: 数组越界
public class ArrayIndexOutOfBoundsTest {
    public static void main(String[] args) {
        int[] arr = {1, 2, 3};
        System.out.println(arr[5]); // 数组越界
    }
}

// 测试用例7: 未关闭资源
import java.io.FileInputStream;

public class ResourceLeakTest {
    public static void main(String[] args) throws Exception {
        FileInputStream fis = new FileInputStream("test.txt");
        byte[] data = new byte[1024];
        fis.read(data);
        // 未关闭资源
    }
}

// 测试用例8: 逻辑错误
public class LogicErrorTest {
    public static void main(String[] args) {
        int x = 5;
        if (x = 10) { // 应该是 == 而不是 =
            System.out.println("x is 10");
        }
    }
}
